from plotutils import plotts
from bokeh.io import save, output_file
from bokeh.layouts import Column, Row
from bokeh.models.widgets import DatePicker
from bokeh.models import HoverTool, CustomJS, Div, ColumnDataSource, DataRange1d, TapTool, Button, Band, Legend
from bokeh.plotting import figure
from bokeh.models.widgets import Panel, Tabs

import glob
import os
import time
from pathlib import Path
import pandas as pd
import numpy as np
import dask
import dask.dataframe as dd
from dask.diagnostics import ProgressBar
from datetime import datetime

from wodupcrawler import WodUp
import json


plot_window = pd.Timedelta('31 days')
datadir_hrsum = '/Users/hasannagib/Documents/s3stage/wahoo/heartrate_sumstat/'

df = dd.read_csv(Path(f'{datadir_hrsum}*.csv')).compute()
df = df.rename(columns={'Unnamed: 0': 'timestamp', '174_': '174_220'})
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.set_index('timestamp')
df_bar = df.copy()
df_bar['L0'] = 22
df_bar['L1'] = 53
df_bar['L2'] = 59
df_bar['L3'] = 66

df_bar = df_bar.reset_index()
df_bar['timestamp'] = pd.to_datetime(df_bar['timestamp'].dt.strftime('%Y-%m-%d 07:00:00'))
df_bar = df_bar.set_index('timestamp')

ts_files = sorted(glob.glob('/Users/hasannagib/Documents/s3stage/wahoo/heartrate_ts/*.csv'))

@dask.delayed
def read_ts(file):
    df = pd.read_csv(file, parse_dates=['timestamp']
                     ).set_index('timestamp').sort_index().reset_index()[
        ['heart_rate']
    ].rename(columns={
        'heart_rate': pd.to_datetime(os.path.basename(file)[:-11]).strftime('%Y-%m-%d'),

    })
    return df


dfs = [read_ts(file) for file in ts_files]

with ProgressBar():
    dfs = dask.compute(dfs)[0]

df_ts = pd.concat(dfs, axis=1).reset_index().rename(columns={'index': 's'})
df_ts['Time'] = df_ts['s'].apply(lambda x: time.strftime('%H:%M:%S', time.gmtime(x)))

# Pick latest date for HR data
df_ts['BPM'] = df_ts.iloc[:, -2]


def plot_cal_ts(df_ts):
    p = figure(
        width=450,
        height=325,
        title='Heart Rate',
        x_axis_label='Time (seconds)',
        y_axis_label='BPM',
        toolbar_location="above",
        tooltips=[
            ('Time', '@Time'),
            ('BPM', '@BPM'),
        ]
    )

    cds = ColumnDataSource(df_ts)
    p.line('s', 'BPM', source=cds, color="black", alpha=0)

    band = Band(base='s', upper='BPM', source=cds, level='underlay',
                fill_alpha=0.99, fill_color='#ab383a') #e73360
    p.add_layout(band)
    return p, cds


with open('../data/session_urls.json') as json_file:
    urls = json.load(json_file)

with open('../data/session_wods.json') as json_file:
    wods = json.load(json_file)

# Get list of dates to look urls for
dts = []
for f in ts_files:
    dt = os.path.basename(f)[:10]
    if pd.to_datetime(dt) > pd.to_datetime('2020-09-01'):
        dts.append(dt)

if set(dts) - set(wods.keys()):
    wu = WodUp(
        email='hasan.nagib@gmail.com',
        password=os.environ['wodify_password'],
        username='hasannagib'
    )

    wu.session_urls = urls
    wu.session_wods = wods

    # Add missing urls
    urls = wu.get_session_urls(dts)
    wods = wu.get_session_wods()

    for k, v in wods.items():
        for i in range(4-len(v)):
            wods[k].append('')

    # Save json
    with open('../data/session_urls.json', 'w') as outfile:
        json.dump(urls, outfile)

    with open('../data/session_wods.json', 'w') as outfile:
        json.dump(wods, outfile)

    wu.browser.quit()

# Add rest day descriptions
for dt in pd.date_range('2020-09-01', datetime.today()):
    dt_str = dt.strftime('%Y-%m-%d')
    if dt_str not in wods.keys():
        wods[dt_str] = ['Rest day', '', '', '']


p1, p1_cds = plotts(
    df_bar[['120_sec_rec', 'L2', 'L1', 'L0', 'L3']],
    units=['bpm'],
    x_range=DataRange1d(end=datetime.today()+pd.Timedelta('1 days'), follow='end', follow_interval=plot_window),
    styles=['|'] + ['-'] * 4,
    alphas=[0.5, 1, 1, 1],
    title='120 sec HR recovery trend',
    palette=['grey']+['#3f8dff', '#7ec4ff', '#e73360', 'green'], #154ba6
    bar_line_color='white',
    line_width=2,
    ylabel='Beats',
    plot_height=325,
    plot_width=450,
    show_plot=False
);

p2, p2_cds = plotts(
    (df.rolling(7).sum().dropna() / 60),
    ys=['174_220', '152_173', '138_151'],
    styles=['o-'],
    units=['min'],
    title='Time spent in HR zones (7 day rolling sum)',
    x_range=p1.x_range,
    ylabel='Minutes',
    plot_height=325,
    plot_width=450,
    trace=True,
    show_plot=False
);

p3, p3_cds = plot_cal_ts(df_ts)

html ="""
<div style="width: 100%; overflow: hidden;">
     <div style="margin-left: 50px; width: 350px; float: left;"> {A} &nbsp; {B} &nbsp; {C} &nbsp; {D} </div>
</div>
"""

div = Div(text=html.format(
    A=wods[dts[-1]][0],
    B=wods[dts[-1]][1],
    C=wods[dts[-1]][2],
    D=wods[dts[-1]][3]
    )
)

dp_callback = CustomJS(
    args={
        'source': p3_cds,
        'div': div,
        'wods': wods,
        'html': html
    },

    code=
    """
    div.text = html.replace("{A}", wods[cb_obj.value][0]).replace("{B}", wods[cb_obj.value][1]).replace("{C}", wods[cb_obj.value][2]).replace("{D}", wods[cb_obj.value][3])

    var yval = cb_obj.value;
    console.log(yval);
    source.data['BPM'] = source.data[cb_obj.value];
    source.change.emit();

    """
)

datePicker = DatePicker(width=100, value=df_ts.columns[-3])
datePicker.js_on_change('value', dp_callback)

tap_code = """
        var dt_idx = p.selected.indices[0]
        var dt = p.data['ts_str'][dt_idx]

        dp.value = dt
        dp.change.emit()
        p.change.emit()
        r.change.emit()
        """

tap1_callback = CustomJS(args={'p': p1_cds, 'r': p2, 'dp': datePicker}, code=tap_code)
tap2_callback = CustomJS(args={'p': p2_cds, 'r': p1, 'dp': datePicker}, code=tap_code)

p1.add_tools(TapTool(callback=tap1_callback))
p2.add_tools(TapTool(callback=tap2_callback))

url = "https://www.wodup.com/timeline?date=@dt_str"

# button = Button(width=100, label="WodUp", button_type="success")
# button.js_on_click(CustomJS(
#     args={
#         'dp': datePicker,
#         'urls': urls
#     },
#     code="""
#     var url = "https://www.wodup.com"
#
#     function formatDate(date) {
#     var d = new Date(date),
#         month = '' + (d.getMonth() + 1),
#         day = '' + d.getDate(),
#         year = d.getFullYear();
#
#     if (month.length < 2)
#         month = '0' + month;
#     if (day.length < 2)
#         day = '0' + day;
#
#     return [year, month, day].join('-');
#     }
#
#     var dt = dp.value
#
#     if (typeof dt === 'string') {
#
#       window.open(url.concat(urls[formatDate(Date.parse(dt))][0]))
#     }
#     else {
#         var day = 60 * 60 * 24 * 1000;
#         window.open(url.concat(urls[formatDate(dt+day)][0]))
#     }
#     """
# )
# )

df_sleep = pd.read_csv('../data/sleep.csv', parse_dates=['start', 'end', 'date'])
df_sleep['7.5hr'] = 450
df_sleep['time_asleep'] = df_sleep['deep'] + df_sleep['rem'] + df_sleep['light']
df_sleep['7day_avg'] = df_sleep.set_index('date')['time_asleep'].rolling('7d', closed='right').mean().reset_index()['time_asleep']
df_sleep['date_str'] = df_sleep['date'].dt.strftime('%a %b %d %Y')
df_sleep['start_time'] = df_sleep['start'].dt.strftime('%I:%M %p')
df_sleep['end_time'] = df_sleep['end'].dt.strftime('%I:%M %p')

stages = ["deep", "rem", "light", "awake"]
colors = ['#154ba6', '#3f8dff', '#7ec4ff', '#e73360']
data = ColumnDataSource(df_sleep)

p4 = figure(
    x_range=DataRange1d(end=datetime.today()+pd.Timedelta('1 days'), follow='end', follow_interval=plot_window),
    x_axis_type="datetime",
    plot_height=325,
    plot_width=450,
    title="Sleep quality",
)
p4.add_layout(Legend(), 'below')
p4.vbar_stack(stages, x='date', width=24*60*60*900, color=colors, source=data, legend_label=[s for s in stages])
p4.line(x='date', y='7.5hr', source=data, color='grey', line_width=2, line_dash="4 4")
p4.line(x='date', y='7day_avg', source=data, line_width=3, legend_label='7day_avg')
p4.y_range.start = 0
p4.x_range.range_padding = 0.1
p4.xgrid.grid_line_color = None
p4.axis.minor_tick_line_color = None
p4.add_tools(HoverTool(
        tooltips=[
            ("Awake", "@awake"),
            ("REM", "@rem"),
            ("Light", "@light"),
            ("Deep", "@deep"),
            ("7day avg", "@7day_avg"),
            ("Date", "@date_str")
        ]
    ))
p4.outline_line_color = None
p4.legend.click_policy = 'hide'
p4.legend.orientation = "horizontal"
p4.yaxis.axis_label = 'Minutes'

p5, p5_cds = plotts(
    df_sleep,
    plot_height=325,
    plot_width=450,
    alphas=[0.5],
    xvar='date',
    ys=['end_hour', 'start_hour'],
    hover_vars=['start_time', 'end_time'],
    hide_hovers=['start_hour', 'end_hour'],
    units=['hour'],
    x_range=p4.x_range,
    ymin=22,
    ylabel='Hour',
    title='Sleep schedule',
    styles=['b'],
    palette=['grey'], #'#154ba6', '#3f8dff', '#7ec4ff', '#e73360'
    bounded_bar_label='sleep',
    show_plot=False
);

df_pr = pd.read_csv('../../WodUp-Scraper/data/hasannagib-pr-table.csv').query('reps > 0')
movements = ['barbell_bench_press', 'back_squat', 'deadlift']
three_lift_total = int(df_pr.query("reps==1")[movements].sum().sum())

rep_pr_desc = f"""
<div style="style=font-family:courier; color:grey; margin-left: 40px; width: 400px; height: 180px; float: left;"> 
<h2>&#127947;&#127997; Weight Lifting</h2>
<p>The views below show lift PRs for different movements and reps. 
I weigh 170 lbs and my current three lift total is {three_lift_total} lbs. 
In terms of <a href="https://strengthlevel.com/powerlifting-standards" class="url">powerlifting standards</a>,
I am an intermediate lifter. My goal is to get to an advanced level (i.e. 1000 lbs) by end of 2021. 
I am hoping to get there with a 405 lbs deadlift, 355 lbs back squat & 240 lbs bench press &#129310;&#127997;
</p>
</div>
"""
rep_pr_desc = Div(text=rep_pr_desc)

p6, p6_cds = plotts(
    df_pr,
    ys=movements,
    hover_vars=[f'date_{mvmt}' for mvmt in movements],
    xvar='reps',
    styles=['-o'],
    x_axis_type='linear',
    ylabel='Weight (lbs)',
    xlabel='Reps',
    title=f'Rep PRs - Three lift total: {three_lift_total} lbs',
    plot_height=353,
    plot_width=450,
    show_plot=False,
    palette=['#154ba6', '#3f8dff', '#7ec4ff', '#e73360'],
    legend_position='center',
    legend_location='top_right',
    legend_orientation='vertical',

)

p6_tabs = Tabs(tabs=[Panel(child=p6, title="n-Rep PR")])

lift_total = f"""
<div style="style=font-family:courier; text-align: center;color:grey; margin-left: 40px; width: 400px; float: left;"> 
<p>&nbsp;</p>
<p>&nbsp;</p>
<h2>
<span style="color:#154ba6">Bench</span> +
<span style="color:#3f8dff">Squat</span> + 
<span style="color:#7ec4ff">Deadlift</span> = 
<span style="color:#e73360">{three_lift_total}</span> lbs</h2>
</div>
"""
lift_total = Div(text=lift_total)

tabs = []
for i in [1, 2, 3, 4, 5]:

    df_plot = []
    for movement in movements:
        df_hist = pd.read_csv(f'../../WodUp-Scraper/data/hasannagib-{movement.replace("_", "-")}.csv', parse_dates=['date'])
        df = df_hist.query(f'(reps>={i})').sort_values('date')
        df_plot.append(np.maximum.accumulate(df).set_index('date')[['weights']].rename(
            columns={'weights': movement}).sort_index()
        )

    p, _ = plotts(
        pd.concat(df_plot),
        xvar='date',
        styles=['o-'],
        units=['lbs'],
        x_axis_type='datetime',
        title=f'{i} rep max PR over time ',
        xlabel='Date',
        ylabel='Weigt (lbs)',
        circle_size=5,
        plot_height=325,
        plot_width=450,
        palette=['#154ba6', '#3f8dff', '#7ec4ff', '#e73360'],
        show_plot=False,
        legend_position='center',
        legend_location='bottom_right',
        legend_orientation='vertical',

    );

    tabs.append(Panel(child=p, title=f"{i} RM"))

p7_tabs = Tabs(tabs=tabs, tabs_location='above', margin=(0,0,0,0))


header = """
<div style="style=font-family:courier; color:grey; margin-left: 40px; width: 400px; float: left;">
<h1>Hasan Nagib</h1> 
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
<a href="https://www.linkedin.com/in/hnagib?_l=en_US" class="fa fa-linkedin" style="font-size:24px"></a>
<a href="https://github.com/hnagib" class="fa fa-github" style="font-size:24px"></a>
<a href="https://www.facebook.com/bigannasah/" class="fa fa-facebook" style="font-size:24px"></a>
<a href="https://www.instagram.com/hnagib/" class="fa fa-instagram" style="font-size:24px"></a>
<a href="mailto:hasan.nagib@gmail.com?subject = Hasan's fitness data blog&body = Hello!" class="fa fa-envelope" style="font-size:24px"></a>
<a href="https://s3.amazonaws.com/hnagib.com/Hasan-Nagib-Resume.pdf" class="tooltip fa fa-file" style="font-size:24px">
<span class="tooltiptext">Resume</span></a>
<p>
    Welcome to my health & fitness data journal! This project was born out of my love for fitness, data & 
    <a href="https://docs.bokeh.org/en/latest/index.html" class="url">Bokeh</a>. This is a simple static 
    Bokeh dashboard hosted on AWS S3. The data is sourced from my Fitbit, Polar HR10, Wahoo TickerX and WodUp.com 
    account. The data is refreshed by a daily batch job that runs on my local machine. Check out my GitHub for 
    details of the project.
</p>
"""
div_header = Div(text=header)

sleep_desc = """
<div style="style=font-family:courier; color:grey; margin-left: 40px; width: 400px; float: left;">
<p>&nbsp;</p>
<p>&nbsp;</p>
<p>&nbsp;</p>
<h2>&#128564; Sleep Logs</h2>
<p>
    Sleep data is sourced from Fitbit sleep logs. 
    My goal is to average 7.5 hours of time asleep and 9 hours time in bed.
    Sleep start and end hours are plotted in 24 hour format.
</p>
</div>
"""
sleep_desc = Div(text=sleep_desc)

hr_rec = """
<div style="style=font-family:courier; color:grey; margin-left: 40px; width: 400px; float: left;"> 
<h2>&#127939;&#127997; Workout Heart Rate</h2>
<p>Heart rate recovery greater than 53 bpm in 2 minutes indicates that one's biological age 
is younger than calendar age. Greater recovery HR generally correlates with better health. Check out this 
<a href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5524096/#jah32178-sec-0016title" class="url">meta analysis</a> 
for more on this. The bar chart below shows my 2 minute recovery heart rate following workouts. 
This is calculated automatically using data collected from my Polar HR10 or Wahoo TickerX chest straps.   
Click on any bar to see corresponding workout and HR profile.
</p>
</div>
"""
hr_rec = Div(text=hr_rec)

hr_zones = """
<div style="style=font-family:courier; color:grey; margin-left: 40px; width: 400px; float: left;">   
<p>&nbsp;</p>
<p>&nbsp;</p>
<p>I also find it useful to monitor time spend in different HR zones. This can help guide my own programming 
and help me decide when to push hard or slow down in CrossFit classes. I generally aim to keep 7 day cumulative 
peak HR zone around or under 30-45 minutes depending on the goal of a given programming cycle. 
</p>
</div>
"""
hr_zones = Div(text=hr_zones)


hr_desc = """
<div style="style=font-family:courier; color:grey; margin-left: 40px; width: 400px; float: left;">   
<p>
Heart rate data is sourced from Polar HR10 and Wahoo TickerX's .fit files. 
The .fit files are synced to Dropbox from the Wahoo iOS app and 
parsed using the <a href="https://pypi.org/project/fitparse/" class="url">fitparse</a> python library.
</p>
</div>
"""
hr_desc = Div(text=hr_desc)

wod_desc="""
<div style="style=font-family:courier; color:grey; margin-left: 40px; width: 400px; float: left;">   
<p>Workout data is sourced from my <a href="https://www.wodup.com" class="url">WodUp</a> account. The data is scraped using selenium. 
WodUp currently does not have an API. 
</p>
</div>
"""
wod_desc = Div(text=wod_desc)



div_space = Div(text='<div style="width: 30px; height: 10px;"></div>')

dash = Column(
    Row(div_header, sleep_desc),
    Row(p4, p5),
    Row(rep_pr_desc, lift_total),
    Row(p6, p7_tabs),
    Row(hr_rec, hr_zones),
    Row(p1, p2),
    Row(hr_desc, Column(wod_desc, Row(div_space, datePicker))),
    Row(p3,div)
)
output_dir = '/Users/hasannagib/Documents/s3stage/dashboards/416-dash.html'


output_file(output_dir, title="Hasan's Data Blog")
save(dash, template=
     """
     {% from macros import embed %}

<!DOCTYPE html>
<html lang="en">
  {% block head %}
  <head>
    {% block inner_head %}
      <meta charset="utf-8">
      <title>{% block title %}{{ title | e if title else "Bokeh Plot" }}{% endblock %}</title>
      {% block preamble %}{% endblock %}
      {% block resources %}
        {% block css_resources %}
          {{ bokeh_css | indent(8) if bokeh_css }}
        {% endblock %}
        {% block js_resources %}
          {{ bokeh_js | indent(8) if bokeh_js }}
        {% endblock %}
      {% endblock %}
      {% block postamble %}{% endblock %}
    {% endblock %}
  </head>
  {% endblock %}
  {% block body %}
  <body>
    {% block inner_body %}
        <style>
            .tooltip {
              position: relative;
              display: inline-block;
              
            }
            
            .tooltip .tooltiptext {
              visibility: hidden;
              width: 100px;
              background-color: #555;
              color: #fff;
              font-family:courier;
              font-size: 75%;
              text-align: center;
              border-radius: 6px;
              padding: 5px 0;
              position: absolute;
              z-index: 1;
              bottom: 20%;
              left: 50%;
              margin-left: 20px;
              opacity: 0;
              transition: opacity 0.3s;
            }
            
            .tooltip .tooltiptext::after {
              content: "";
              position: absolute;
              top: 0%;
              left: 50%;
              margin-left: -5px;
              border-width: 5px;
              border-style: solid;
              border-color: #555 transparent transparent transparent;
            }
            
            .tooltip:hover .tooltiptext {
              visibility: visible;
              opacity: 1;
            }
            
            .fa {
              padding: 10px;
              font-size:200px;
              width: 10px;
              text-align: center;
              text-decoration: none;
            }
            
            /* Add a hover effect if you want */
            .fa:hover {
              opacity: 0.7;
            }
            
            /* Set a specific color for each brand */
            .fa-facebook {
              background: transparent;
              color: #3B5998;
            }
            
            .fa-linkedin {
              background: transparent;
              color: #007bb5;
            }
            
            .fa-instagram {
              background: transparent;
              color: red;
            }
            
            .fa-github {
              background: transparent;
              color: black;
            }
            
            .fa-envelope {
              background: transparent;
              color: red;
            }
            
            .fa-file {
              background: transparent;
              color: #367da3;
            }

            a.url:link {
              color: #e73360;
              background-color: transparent;
              text-decoration: none;
            }
    
            a.url:visited {
              color: #e73360;
              background-color: transparent;
              text-decoration: none;
            }
    
            a.url:hover {
              color: #154ba6;
              background-color: transparent;
              text-decoration: none;
            }
    
            a.url:active {
              color: #e73360;
              background-color: transparent;
              text-decoration: underline;
            }
            
        </style>
      {% block contents %}
        {% for doc in docs %}
          {{ embed(doc) if doc.elementid }}
          {% for root in doc.roots %}
            {% block root scoped %}
              {{ embed(root) | indent(10) }}
            {% endblock %}
          {% endfor %}
        {% endfor %}
      {% endblock %}
      {{ plot_script | indent(8) }}
    {% endblock %}
  </body>
  {% endblock %}
</html>
"""
     )


