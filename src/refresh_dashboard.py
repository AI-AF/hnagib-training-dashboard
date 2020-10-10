from plotutils import plotts
from bokeh.io import save, output_file
from bokeh.layouts import Column, Row
from bokeh.models.widgets import DatePicker
from bokeh.models import CustomJS, Div, ColumnDataSource, DataRange1d, TapTool, Button, Band
from bokeh.plotting import figure

import glob
import os
import time
from pathlib import Path
import pandas as pd
import dask
import dask.dataframe as dd
from dask.diagnostics import ProgressBar
from datetime import datetime

from wodupcrawler import WodUp
import json


plot_window = pd.Timedelta('31 days')
datadir_hrsum = '/Users/hasannagib/Documents/s3stage/wahoo/heartrate_sumstat/'

df = dd.read_csv(Path(f'{datadir_hrsum}*.csv')).compute()
df = df.rename(columns={'Unnamed: 0': 'timestamp'})
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.set_index('timestamp')
df_bar = df.copy()
df_bar['L0'] = 22
df_bar['L1'] = 53
df_bar['L2'] = 59
df_bar['L3'] = 66

ts_files = sorted(glob.glob('/Users/hasannagib/Documents/s3stage/wahoo/heartrate_ts/*.csv'))


@dask.delayed
def read_ts(file):
    df = pd.read_csv(file, parse_dates=['timestamp']
                     ).set_index('timestamp').sort_index().reset_index()[
        ['heart_rate']
    ].rename(columns={
        'heart_rate': pd.to_datetime(os.path.basename(file)[:-11]).strftime('%a %b %d %Y'),

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
        width=900,
        height=350,
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
                fill_alpha=0.95, fill_color='#ab383a')
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

    # Save json
    with open('../data/session_urls.json', 'w') as outfile:
        json.dump(urls, outfile)

    with open('../data/session_wods.json', 'w') as outfile:
        json.dump(wods, outfile)

    wu.browser.quit()


header="""
<div style="style=font-family:courier; color:grey; margin-left: 40px; width: 350px; float: left;"> <h1>Training Dashboard</h1> </div>
"""
div_header = Div(text=header)
A = wods[dts[-1]][0]
B = wods[dts[-1]][1]

html ="""
<p> &nbsp;&nbsp; </p>
<div style="width: 100%; overflow: hidden;">
     <div style="margin-left: 100px; width: 350px; float: left;"> {A} </div>
     <div style="margin-left: 500px; width: 350px"> {B} </div>
</div>
"""

div = Div(text=html.format(A=A, B=B))

p1, p1_cds = plotts(
    df_bar[['L0', 'L1', 'L2', 'L3', '120_sec_rec']],
    units=['bpm'],
    x_range=DataRange1d(end=datetime.today()+pd.Timedelta('1 days'), follow='end', follow_interval=plot_window),
    styles=['--'] * 4 + 2 * ['|'],
    title='120 sec HR recovery trend',
    ylabel='Beats',
    plot_width=450,
    show_plot=False
);

p2, p2_cds = plotts(
    (df.rolling(7).sum().dropna() / 60),
    ys=['174_', '152_173', '138_151'],
    styles=['o-'],
    units=['min'],
    title='Time spent in HR zones (7 day rolling sum)',
    x_range=p1.x_range,
    ylabel='Minutes',
    plot_width=450,
    trace=True,
    show_plot=False
);

p3, p3_cds = plot_cal_ts(df_ts)

dp_callback = CustomJS(
    args={
        'source': p3_cds,
        'div': div,
        'wods': wods,
        'html': html
    },

    code=
    """
    console.log('div: ', cb_obj.value)
    console.log('test: ', html.replace("{A}", wods[cb_obj.value][0]))

    div.text = html.replace("{A}", wods[cb_obj.value][0]).replace("{B}", wods[cb_obj.value][1])

    var yval = cb_obj.value;
    source.data['BPM'] = source.data[yval];
    source.change.emit()

    """
)

datePicker = DatePicker(width=150, value=df_ts.columns[-3])
datePicker.js_on_change('value', dp_callback)

tap_code = """
        console.log('DatePicker: ', dp.value)

        var dt_idx = p.selected.indices[0]
        var dt = p.data['ts_str'][dt_idx]

        console.log('Data selected: ', dt)
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

button = Button(width=100, label="WodUp", button_type="success")
button.js_on_click(CustomJS(
    args={
        'dp': datePicker,
        'urls': urls
    },
    code="""    
    var url = "https://www.wodup.com"

    function formatDate(date) {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2) 
        month = '0' + month;
    if (day.length < 2) 
        day = '0' + day;

    return [year, month, day].join('-');
    }

    var dt = dp.value
    console.log('Date:', formatDate(dt))

    if (typeof dt === 'string') {

      window.open(url.concat(urls[formatDate(Date.parse(dt))][0]))
    }
    else {
        var day = 60 * 60 * 24 * 1000;
        window.open(url.concat(urls[formatDate(dt+day)][0]))
    }

    """
)
)

dash = Column(div_header, Row(p1, p2), Row(button), p3, div)
output_dir = '/Users/hasannagib/Documents/s3stage/dashboards/416-dash.html'

output_file(output_dir, title="Hasan's Data Blog")
save(dash)
