import glob
import os
import time
import dask
import pandas as pd
import numpy as np
from plotutils import plotts
from bokeh.io import save, output_file
from bokeh.plotting import figure
from bokeh.layouts import Column, Row
from bokeh.models.widgets import DatePicker, Panel, Tabs
from bokeh.models import (HoverTool, CustomJS, Div, ColumnDataSource, 
    DataRange1d, TapTool, Button, Band, Legend, BasicTicker, ColorBar, 
    ColumnDataSource, LinearColorMapper, PrintfTickFormatter)
from bokeh.palettes import OrRd
from bokeh.transform import transform
from pathlib import Path
import dask.dataframe as dd
from dask.diagnostics import ProgressBar
from datetime import datetime
from wodupcrawler import WodUp
import json

import htmltext

plot_window = pd.Timedelta('70 days')
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


def plot_hr_profile(df_ts):
    p = figure(
        width=450,
        height=325,
        title=f'Heart rate',
        x_axis_label='Time (seconds)',
        y_axis_label='BPM',
        toolbar_location="above",
        tools='box_zoom,undo,redo,reset',
        tooltips=[
            ('Time', '@Time'),
            ('BPM', '@BPM'),
        ]
    )

    cds = ColumnDataSource(df_ts)
    p.line('s', 'BPM', source=cds, color="black", alpha=0)

    band = Band(base='s', upper='BPM', source=cds, level='underlay',
                fill_alpha=0.90, fill_color='#ab383a') #e73360
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
    alphas=[1, 1, 1, 1],
    title='120 sec HR recovery trend',
    palette=['grey']+['#3f8dff', '#7ec4ff', '#e73360', '#154ba6'], #154ba6
    bar_line_color='white',
    ts_format='%Y-%m-%d',
    line_width=2,
    ylabel='Beats',
    plot_height=325,
    plot_width=450,
    tools='xwheel_pan,pan,reset',
    active_scroll='xwheel_pan',
    show_plot=False
);


p2, p2_cds = plotts(
    (df.rolling(7).sum().dropna() / 60),
    ys=['174_220', '152_173', '138_151'],
    styles=['o-'],
    units=['min'],
    title='HR zones (7 day rolling sum)',
    x_range=p1.x_range,
    ylabel='Minutes',
    tools='xwheel_pan,pan,reset',
    active_scroll='xwheel_pan',
    plot_height=325,
    plot_width=450,
    show_plot=False
);

p3, p3_cds = plot_hr_profile(df_ts)


div_wodup = Div(text=htmltext.div_wodup.format(
                A=wods[dts[-1]][0],
                B=wods[dts[-1]][1],
                C=wods[dts[-1]][2],
                D=wods[dts[-1]][3]
            ))

dp_callback = CustomJS(
    args={
        'source': p3_cds,
        'div': div_wodup,
        'wods': wods,
        'html': htmltext.div_wodup
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

datePicker = DatePicker(width=100, value=df_ts.columns[-3], align='center', sizing_mode='stretch_width')
datePicker.js_on_change('value', dp_callback)

hr_tap_code = """
    var dt_idx = p.selected.indices[0]
    var dt = p.data['ts_str'][dt_idx]

    dp.value = dt
    dp.change.emit()
    p.change.emit()
    r.change.emit()
"""

tap1_callback = CustomJS(args={'p': p1_cds, 'r': p2, 'dp': datePicker}, code=hr_tap_code)
tap2_callback = CustomJS(args={'p': p2_cds, 'r': p1, 'dp': datePicker}, code=hr_tap_code)

p1.add_tools(TapTool(callback=tap1_callback))
p2.add_tools(TapTool(callback=tap2_callback))

url = "https://www.wodup.com/timeline?date=@dt_str"

df_sleep = pd.read_csv('../data/sleep.csv', parse_dates=['start', 'end', 'date'])
stages = ["deep", "rem", "light", "awake"]

for s in stages:
    df_sleep[s] = df_sleep[s]/60

df_sleep['8hr'] = 8
df_sleep['time_asleep'] = df_sleep['deep'] + df_sleep['rem'] + df_sleep['light']
df_sleep['7day_avg'] = df_sleep.set_index('date')['time_asleep'].rolling('7d', closed='right').mean().reset_index()['time_asleep']
df_sleep['date_str'] = df_sleep['date'].dt.strftime('%a %b %d %Y')
df_sleep['start_time'] = df_sleep['start'].dt.strftime('%I:%M %p')
df_sleep['end_time'] = df_sleep['end'].dt.strftime('%I:%M %p')

colors = ['#154ba6', '#3f8dff', '#7ec4ff', '#e73360']
data = ColumnDataSource(df_sleep)

p4 = figure(
    x_range=DataRange1d(end=datetime.today()+pd.Timedelta('1 days'), follow='end', follow_interval=plot_window),
    x_axis_type="datetime",
    plot_height=325,
    plot_width=450,
    tools='xwheel_pan,pan,reset',
    active_scroll='xwheel_pan',
    toolbar_location='above',
    title="Sleep quality",
)
p4.add_layout(Legend(), 'below')
p4.vbar_stack(stages, x='date', width=24*60*60*900, color=colors, source=data, legend_label=[s for s in stages])
p4.line(x='date', y='8hr', source=data, color='black', line_width=2, line_dash="4 4")
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
p4.legend.border_line_alpha = 0
p4.yaxis.axis_label = 'Hours'

p5, p5_cds = plotts(
    df_sleep,
    plot_height=325,
    plot_width=450,
    alphas=[1],
    xvar='date',
    ys=['end_hour', 'start_hour'],
    hover_vars=['start_time', 'end_time'],
    hide_hovers=['start_hour', 'end_hour'],
    units=['hour'],
    x_range=p4.x_range,
    y_range=[2, 24],
    ylabel='Hour',
    title='Sleep schedule',
    styles=['b'],
    palette=['grey'], #'#154ba6', '#3f8dff', '#7ec4ff', '#e73360'
    bounded_bar_label='sleep',
    tools='xwheel_pan,pan,reset',
    active_scroll='xwheel_pan',
    show_plot=False
);

df_pr = pd.read_csv('../../WodUp-Scraper/data/hasannagib-pr-table.csv').query('reps > 0')
movements = ['barbell_bench_press', 'back_squat', 'deadlift']
three_lift_total = int(df_pr.query("reps==1")[movements].sum().sum())


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
    plot_height=400,#275,
    plot_width=450,
    show_plot=False,
    tools='box_zoom,undo,redo,reset',
    palette=['#154ba6', '#3f8dff', '#7ec4ff', '#e73360'],
    legend_position='below',
    legend_location='bottom_left',
    legend_orientation='vertical',

)

p6_tabs = Tabs(tabs=[Panel(child=p6, title="n-Rep PR")])

tabs = []
for i in [1, 2, 3, 4, 5]:

    df_plot = []
    for movement in movements:
        df_hist = pd.read_csv(f'../../WodUp-Scraper/data/hasannagib-{movement.replace("_", "-")}.csv', parse_dates=['date'])
        df = df_hist.query(f'(reps>={i})').sort_values('date')
        dfi = np.maximum.accumulate(df).set_index('date')[['weights']].rename(
            columns={'weights': movement}).sort_index().drop_duplicates().groupby('date').max().reindex(
            pd.date_range('2019-10-01', datetime.today())
        )
        dfi.index.name='date'
        df_plot.append(dfi)
    
    plot_df = pd.concat(df_plot).dropna(thresh=1).sort_index().fillna(method='bfill').fillna(method='ffill')
    add = plot_df.iloc[-1,:]
    add.name = datetime.today()
    plot_df = plot_df.append(add)

    p, _ = plotts(
        plot_df,
        xvar='date',
        styles=['oL'],
        units=['lbs'],
        x_axis_type='datetime',
        title=f'{i} rep max PR over time ',
        xlabel='Date',
        ylabel='Weight (lbs)',
        #y_range=[50,500],
        #circle_size=1,
        plot_height=370,
        plot_width=450,
        tools='box_zoom,undo,redo,reset',
        palette=['#154ba6', '#3f8dff', '#7ec4ff', '#e73360'],
        show_plot=False,
        legend_position='below',
        legend_location='bottom_left',
        legend_orientation='vertical',

    );

    tabs.append(Panel(child=p, title=f"{i} RM"))

p7_tabs = Tabs(tabs=tabs, tabs_location='above', margin=(0,0,0,0))

#########################################################################################################

def calendar_array(dates, data):
    i, j = zip(*[d.isocalendar()[1:] for d in dates])
    i = np.array(i) - min(i)
    j = np.array(j) - 1
    ni = max(i) + 1

    calendar = np.nan * np.zeros((ni, 7))
    calendar[i, j] = data
    return i, j, calendar


date = []
cals = []
wods = []

with open('../data/session_wods.json') as json_file:
    workouts = json.load(json_file)

for f in glob.glob('/Users/hasannagib/Documents/s3stage/wahoo/heartrate_ts/*.csv'):
    dt = pd.to_datetime(os.path.basename(f)[:10])
    date.append(dt)
    cals.append(max(pd.read_csv(f)['calories']))
    try:
        wods.append(workouts[dt.strftime('%Y-%m-%d')])
    except KeyError:
        wods.append([''] * 4)


def gen_plot_df(date, cals, wods, start, end):
    df = pd.DataFrame({
        'date': date,
        'cals': cals,
        'A': [w[0] for w in wods],
        'B': [w[1] for w in wods],
        'C': [w[2] for w in wods],
        'D': [w[3] for w in wods],
    }).set_index('date')

    df = df.reindex(pd.date_range(min(date), max(date))).fillna(
        {'cals': 0, 'A': 'Rest day', 'B': '', 'C': '', 'D': ''}
    )[start:end]

    dates = df.index
    data = np.random.randint(0, 20, len(dates))

    cal = calendar_array(df.index, df['cals'].values)
    weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    df = pd.DataFrame({
        'dt': dates,
        'A': df['A'],
        'B': df['B'],
        'C': df['C'],
        'D': df['D'],
        'Date': [dt.strftime('%Y-%m-%d') for dt in dates],
        'dom': [dt.strftime('%d') for dt in dates],
        'Day': [weekdays[i] for i in cal[1]],
        'Week': [f"Week {i}" for i in cal[0]],
        'Cals': cal[2][~np.isnan(cal[2])],
    })

    return df


def plot_cal(df):
    weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    source = ColumnDataSource(df)
    mapper = LinearColorMapper(palette=OrRd[9], low=df['Cals'].max(), high=df['Cals'].min())

    p = figure(
        plot_width=350,
        plot_height=250,
        title='-'.join([dt for dt in df['dt'].dt.strftime('%B').unique()]),
        x_range=weekdays,
        y_range=list(reversed(list(df['Week'].unique()))),
        toolbar_location='above',
        tools="reset,hover",
        x_axis_location="above"
    )

    p.rect(
        x="Day",
        y="Week",
        width=1,
        height=1,
        source=source,
        line_color='white',
        line_width=5,
        fill_color=transform('Cals', mapper)
    )

    p.text(
        x="Day",
        y="Week",
        text='dom',
        text_align='center',
        text_baseline='middle',
        text_color='grey',
        text_font='courier',
        source=source
    )


    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = "15px"
    p.outline_line_color = None
    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_standoff = 0
    p.yaxis.major_label_text_font_size = '0pt'
    p.yaxis.axis_label=' '

    p.hover.tooltips = [
        ("Calories", "@Cals"),
        ("Date", "@Date"),
        ("", "@A{safe}"),
        ("", "@B{safe}"),
        ("", "@C{safe}"),
        ("", "@D{safe}")
    ]
    return p, source


pcal_30, pcal_30_cds = plot_cal(gen_plot_df(
    date, cals, wods,
    datetime.today() - pd.Timedelta('31 d'),
    datetime.today())
)

cal_tap_code = """
    var dt_idx = p.selected.indices[0]
    console.log(dt_idx)
    var dt = p.data['Date'][dt_idx]
    console.log(dt)

    dp.value = dt
    dp.change.emit()
    p.change.emit()
    r.change.emit()
"""

tap_cal_callback = CustomJS(
    args={
        'p': pcal_30_cds, 
        'r': p2, 
        'dp': datePicker
    }, 
    code=cal_tap_code
)

pcal_30.add_tools(TapTool(callback=tap_cal_callback))


#########################################################################################################
date = []
cals = []
wods = []
sleep = []

with open('../data/session_wods.json') as json_file:
    workouts = json.load(json_file)

df_sleep = pd.read_csv('../data/sleep.csv', parse_dates=['start', 'end'])
df_sleep['dt'] = df_sleep['start'].dt.strftime('%Y-%m-%d')

for f in glob.glob('/Users/hasannagib/Documents/s3stage/wahoo/heartrate_ts/*.csv'):
    dt = pd.to_datetime(os.path.basename(f)[:10])
    date.append(dt)
    cals.append(max(pd.read_csv(f)['calories']))
    try:
        wods.append(workouts[dt.strftime('%Y-%m-%d')])
    except KeyError:
        wods.append([''] * 4)

    try:
        dur = df_sleep.set_index('dt').loc[dt.strftime('%Y-%m-%d')]['duration'] - \
              df_sleep.set_index('dt').loc['2020-10-30']['awake']
        sleep.append(dur)
    except KeyError:
        sleep.append(0)


def gen_plot_df(date, cals, wods, sleep, start, end):
    df = pd.DataFrame({
        'date': date,
        'cals': cals,
        'sleep': sleep,
        'A': [w[0] for w in wods],
        'B': [w[1] for w in wods],
        'C': [w[2] for w in wods],
        'D': [w[3] for w in wods],
    }).set_index('date')

    df = df.reindex(pd.date_range(pd.to_datetime('2019-01-01'), max(date))).fillna(
        {'cals': 0, 'A': 'Rest day', 'B': '', 'C': '', 'D': ''}
    )[start:end]

    dates = df.index
    cal = calendar_array(df.index, df['cals'].values)
    weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    df = pd.DataFrame({
        'dt': dates,
        'A': df['A'],
        'B': df['B'],
        'C': df['C'],
        'D': df['D'],
        'sleep_hr': [f"{n:02}" for n in (df['sleep'].fillna(0) // 60).astype(int)],
        'sleep_min': [f"{n:02}" for n in (df['sleep'].fillna(0) % 60).astype(int)],
        'Date': [dt.strftime('%Y-%m-%d') for dt in dates],
        'dom': [dt.strftime('%d') for dt in dates],
        'Day': [weekdays[i] for i in cal[1]],
        'Week': [f"Week {i}" for i in cal[0]],
        'Cals': cal[2][~np.isnan(cal[2])],
    })

    return df


def plot_cal(df):
    weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    source = ColumnDataSource(df)
    mapper = LinearColorMapper(palette=OrRd[9], low=df['Cals'].max(), high=df['Cals'].min())

    start = df['dt'].min().strftime('%Y %B')
    end = df['dt'].max().strftime('%Y %B')

    p = figure(
        plot_width=450,
        plot_height=150,
        title=f"{start} - {end}",
        y_range=list(reversed(weekdays)),
        x_range=list(df['Week'].unique()),
        toolbar_location=None,
        tools="hover",
        x_axis_location="above",
    )

    p.rect(
        y="Day",
        x="Week",
        width=1,
        height=1,
        source=source,
        line_color='white',
        line_width=4,
        fill_color=transform('Cals', mapper)
    )

    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = "0px"
    p.outline_line_color = 'white'
    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_text_font_size = '0pt'
    p.yaxis.axis_label=' '

    p.hover.tooltips = [
        ("Date", "@Date"),
        ("Calories burned", "@Cals"),
        ("Hours slept", "@sleep_hr:@sleep_min")
    ]
    return p


pcal = plot_cal(gen_plot_df(
    date, cals, wods, sleep,
    datetime.today() - pd.Timedelta('180 d'),
    datetime.today())
)
##################################################################################################

def space(width):
    return Div(text=htmltext.div_space.format(width=width))


dash = Column(
    Column(
        Div(text=htmltext.div_header), 
        Row(space('15'), pcal)
    ),
    Div(text=htmltext.div_intro),
    Div(text=htmltext.div_sleep),
    Row(
        Row(space('30'), p4), 
        Row(space('30'), p5)
    ),
    Row(
        Div(text=htmltext.div_weight_lifting.format(three_lift_total)), 
        Div(text=htmltext.div_lift_total.format(three_lift_total))
    ),
    Row(
        Row(space('30'), p6), 
        Row(space('30'), p7_tabs)
    ),
    Row(
        Column(
            Div(text=htmltext.div_hr_rcvry), 
            Row(space('30'), p1)
        ),
        Column(
            Div(text=htmltext.div_hr_zones), 
            Row(space('30'), p2)
        )
    ),
    Row(
        Column(
            Div(text=htmltext.div_hr_profile), 
            p3, 
            Div(text=htmltext.div_workout_cal), 
            Row(space('60'), pcal_30), 
            Div(text=htmltext.div_conclusion)
        ),
        Column(
            Div(text=htmltext.div_wod_logs), 
            Row(space('30'), datePicker), 
            div_wodup
        )
        ),
)


output_dir = '/Users/hasannagib/Documents/s3stage/dashboards/416-dash.html'
output_file(output_dir, title="Hasan's Data Blog")
save(dash, template=htmltext.bokeh_template)