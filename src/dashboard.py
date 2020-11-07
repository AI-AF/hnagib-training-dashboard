import glob
import os
import time
import dask
import pandas as pd
import numpy as np
from plotutils import plotts, gen_plot_df, plotcal, plot_hr_profile, plot_sleep_stages
from bokeh.io import save, output_file
from bokeh.plotting import figure
from bokeh.layouts import Column, Row
from bokeh.models.widgets import DatePicker, Panel, Tabs
from bokeh.models import (HoverTool, CustomJS, Div, ColumnDataSource, 
    DataRange1d, TapTool, Button, Band, Legend, BasicTicker, ColorBar, 
    ColumnDataSource, LinearColorMapper, PrintfTickFormatter, Rect)
from bokeh.transform import transform
from pathlib import Path
import dask.dataframe as dd
from dask.diagnostics import ProgressBar
from datetime import datetime
import wodupcrawler
import json
import htmltext
import fitetl
import sleepetl

#########################################################################################################
# Data load
#########################################################################################################

# Heart rate .fit files
fitetl.main()
df_hr_rcvry = fitetl.read_rcvry_csv(fitetl.datadir_hrsum)
df_hr_profile = fitetl.read_hr_profile_csv(fitetl.datadir_hrts)
ts_files = sorted(glob.glob(f'{fitetl.datadir_hrts}*.csv'))

# WOD logs
wodupcrawler.main()
with open(f'{wodupcrawler.datadir}session_wods.json') as json_file:
    wods = json.load(json_file)

latest_wodup_log_dt = wodupcrawler.get_latest_wodup_log_date(wods)

# Sleep data
df_sleep = sleepetl.read_sleep_plot_df()

# PR data
df_pr = pd.read_csv('../../WodUp-Scraper/data/hasannagib-pr-table.csv').query('reps > 0')

#########################################################################################################
# Plot parameters
#########################################################################################################

plot_window = pd.Timedelta('70 days')

p1, p1_cds = plotts(
    df_hr_rcvry[['120_sec_rec', 'L2', 'L1', 'L0', 'L3']],
    units=['bpm'],
    x_range=DataRange1d(end=datetime.today()+pd.Timedelta('1 days'), follow='end', follow_interval=plot_window),
    styles=['|'] + ['-'] * 4,
    alphas=[1, 1, 1, 1],
    title='2 min heart rate recovery',
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
    (df_hr_rcvry.rolling(7).sum().dropna() / 60),
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

p3, p3_cds = plot_hr_profile(df_hr_profile, x='s', y='BPM')


p4, p4_cds = plot_sleep_stages(df_sleep, plot_window)


p5, p5_cds = plotts(
    df_sleep,
    plot_height=400,
    plot_width=800,
    alphas=[1],
    xvar='date',
    ys=['end_hour', 'start_hour'],
    hover_vars=['start_time', 'end_time'],
    hide_hovers=['start_hour', 'end_hour'],
    units=['hour'],
    x_range=p4.x_range,
    y_range=[2, 24],
    ylabel='24-Hour',
    title='Sleep schedule',
    styles=['b'],
    palette=['grey'], #'#154ba6', '#3f8dff', '#7ec4ff', '#e73360'
    bounded_bar_label='sleep',
    tools='xwheel_pan,pan,reset,box_zoom',
    active_scroll='xwheel_pan',
    show_plot=False
);

movements = ['deadlift', 'barbell_bench_press', 'back_squat', 'shoulder_press']
three_lift_total = int(df_pr.query("reps==1")[
    ['barbell_bench_press', 'back_squat', 'deadlift']
].sum().sum())

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
    plot_height=350,#275,
    plot_width=900,
    show_plot=False,
    tools='box_zoom,undo,redo,reset',
    palette=['#154ba6', '#3f8dff', '#7ec4ff', 'grey'],
    legend_position='right',
    legend_location='top_right',
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
        plot_height=350,
        plot_width=900,
        tools='box_zoom,undo,redo,reset',
        palette=['#154ba6', '#3f8dff', '#7ec4ff', 'grey'], #e73360
        show_plot=False,
        legend_position='right',
        legend_location='top_right',
        legend_orientation='vertical',

    );

    tabs.append(Panel(child=p, title=f"{i} RM"))

p7_tabs = Tabs(tabs=tabs, tabs_location='above', margin=(0,0,0,0))

#########################################################################################################

date = []
cals = []
wods_text = []
sleep = []

df_sleep['dt'] = df_sleep['start'].dt.strftime('%Y-%m-%d')

for f in glob.glob('/Users/hasannagib/Documents/s3stage/wahoo/heartrate_ts/*.csv'):
    dt = pd.to_datetime(os.path.basename(f)[:10])
    date.append(dt)
    cals.append(max(pd.read_csv(f)['calories']))
    try:
        wods_text.append(wods[dt.strftime('%Y-%m-%d')])
    except KeyError:
        wods_text.append([''] * 4)

    try:
        dur = df_sleep.set_index('dt').loc[dt.strftime('%Y-%m-%d')]['duration'] - \
              df_sleep.set_index('dt').loc['2020-10-30']['awake']
        sleep.append(dur)
    except KeyError:
        sleep.append(0)

##################################################################################################

pcal_30_df = gen_plot_df(date, cals, wods_text, sleep, datetime.today() - pd.Timedelta('31 d'), datetime.today())
pcal_30, pcal_30_cds = plotcal(pcal_30_df)


pcal_df = gen_plot_df(date, cals, wods_text, sleep, datetime.today() - pd.Timedelta('165 d'), datetime.today())
pcal, pcal_cds = plotcal(
    pcal_df,
    weekdays=['Sat', 'Fri', 'Thu', 'Wed', 'Tue', 'Mon', 'Sun'],
    mode='github',
    fig_args={
        'plot_width':665,
        'plot_height':175,
        'tools':'hover',
        'toolbar_location':None,
    },
    hover_tooltips=[
        ("Date", "@Date"),
        ("Calories", f"@Cals"),
        ("Hours slept", "@sleep_hr:@sleep_min")
    ],
    show_dates=False
)

"""
#######################################################################################################

Bokeh interactive data load
    Elements to update: 
        - WODs html text
        - Heart rate profile plot

    Control elements:
        - Calendar plot tap
        - Datepicker widget select
        - HR recovery plot tap

#########################################################################################################
"""
div_wodup = Div(text=htmltext.div_wodup.format(
                A=wods[latest_wodup_log_dt][0],
                B=wods[latest_wodup_log_dt][1],
                C=wods[latest_wodup_log_dt][2],
                D=wods[latest_wodup_log_dt][3]
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
    source.data['BPM'] = source.data[cb_obj.value];
    div.text = html.replace("{A}", wods[cb_obj.value][0]).replace("{B}", wods[cb_obj.value][1]).replace("{C}", wods[cb_obj.value][2]).replace("{D}", wods[cb_obj.value][3])
    source.change.emit();

    """
)

datePicker = DatePicker(width=100, value=df_hr_profile.columns[-3], align='center', sizing_mode='stretch_width')
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

p1.add_tools(TapTool(callback=tap1_callback))

url = "https://www.wodup.com/timeline?date=@dt_str"

cal_tap_code = """
    var dt_idx = p.selected.indices[0]
    var dt = p.data['Date'][dt_idx]

    dp.value = dt
    dp.change.emit()
    p.change.emit()
    r.change.emit()
"""

tap_cal_callback = CustomJS(args={'p': pcal_30_cds, 'r': p2, 'dp': datePicker}, code=cal_tap_code)
pcal_30.add_tools(TapTool(callback=tap_cal_callback))

tap_cal_callback = CustomJS(args={'p': pcal_cds, 'r': p2, 'dp': datePicker}, code=cal_tap_code)
pcal.add_tools(TapTool(callback=tap_cal_callback))

#########################################################################################################
# Dashboard
#########################################################################################################

def space(width):
    return Div(text=htmltext.div_space.format(width=width))


dash = Column(
    Column(
        Div(text=htmltext.div_header), 
        Row(space('40'), pcal)
    ),

    Row(
        space(2),
        Div(text=htmltext.div_intro),
        Div(text=htmltext.div_conclusion),
    ),

    Tabs(tabs=[
        Panel(
            child=Row(
                Column(
                    Div(text=htmltext.div_workout_cal), 
                    Row(space('100'), pcal_30), 
                    Div(text=htmltext.div_hr_profile), 
                    Row(space('30'), p3), 
                ),
                Column(
                    Div(text=htmltext.div_wod_logs), 
                    Row(space('30'), datePicker), 
                    div_wodup
                )
            ), 
            title="WODs"
        ),
        Panel(
            child=Row(
                Row(
                Column(
                    Div(text=htmltext.div_hr_rcvry), 
                    Row(space('30'), p1),
                    Row(space('30'), p3)
                ),
                Column(
                    Div(text=htmltext.div_hr_zones), 
                    Row(space('30'), p2)
                )
            )), 
            title="Heart Rate"
            
        ), 
        Panel(
            child=Column(
                Div(text=htmltext.div_weight_lifting.format(three_lift_total)), 
                Div(text=htmltext.div_lift_total.format(three_lift_total)),
                Row(space('30'), p7_tabs),
                Row(space('30'), p6), 
            ), 
            title="Weight Lifting"
        ),
        Panel(
            child=Column(
                Div(text=htmltext.div_sleep),
                Row(space('30'), p4), 
                Row(space('30'), p5)
            ), 
            title="Sleep"
        ),             
    ], 
    sizing_mode='stretch_both', 
    tabs_location='above',
    width_policy='max',
    margin=(0,0,0,50),
    css_classes=['bokeh-plots'],
    ),
)

# Save dashboard
output_dir = '/Users/hasannagib/Documents/s3stage/dashboards/index.html'
output_file(output_dir, title="Hasan's Data Blog")
save(dash, template=htmltext.bokeh_template)
