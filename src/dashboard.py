import glob
import os
import time
import dask
import pandas as pd
import numpy as np
from plotutils import plot_ts, gen_cal_plot_df, plot_cal, plot_hr_profile, plot_sleep_stages
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
wods, df_wods = wodupcrawler.read_wods_json(f'{wodupcrawler.datadir}session_wods.json')
latest_wodup_log_dt = wodupcrawler.get_latest_wodup_log_date(wods)

# Sleep data
sleepetl.main()
df_sleep = sleepetl.read_sleep_plot_df()

# PR data
df_pr = pd.read_csv(
    '../../WodUp-Scraper/data/hasannagib-pr-table.csv', 
    parse_dates=[f'date_{mvmt}' for mvmt in ['back_squat', 'front_squat', 'deadlift', 'shoulder_press']]
).query('(reps > 0) and (reps <= 10)')

#########################################################################################################
# Time series plots
#########################################################################################################

plot_window = pd.Timedelta('70 days')

plot_hr_rcvry, plot_hr_rcvry_cds = plot_ts(
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


plot_hr_zones, plot_hr_zones_cds = plot_ts(
    (df_hr_rcvry.rolling(7).sum().dropna() / 60),
    ys=['174_220', '152_173', '138_151'],
    styles=['o-'],
    units=['min'],
    title='HR zones (7 day rolling sum)',
    x_range=plot_hr_rcvry.x_range,
    ylabel='Minutes',
    tools='xwheel_pan,pan,reset,box_zoom',
    active_scroll='xwheel_pan',
    plot_height=325,
    plot_width=450,
    show_plot=False
);

plot_hr_profile, plot_hr_profile_cds = plot_hr_profile(df_hr_profile, x='s', y='BPM')


plot_sleep_stages, plot_sleep_stages_cds = plot_sleep_stages(df_sleep, plot_window)


plot_sleep_schedule, plot_sleep_schedule_cds = plot_ts(
    df_sleep,
    plot_height=400,
    plot_width=800,
    alphas=[1],
    xvar='date',
    ys=['end_hour', 'start_hour'],
    hover_vars=['start_time', 'end_time'],
    hide_hovers=['start_hour', 'end_hour'],
    units=['hour'],
    x_range=plot_sleep_stages.x_range,
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
three_lift_total = int(df_pr.query("reps==1")[['barbell_bench_press', 'back_squat', 'deadlift']].sum().sum())

plot_rep_prs, plot_rep_prs_cds = plot_ts(
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

tabs = []
for i in [1, 2, 3, 4, 5]:

    pr_hist = []
    for movement in movements:
        df_hist = pd.read_csv(f'../../WodUp-Scraper/data/hasannagib-{movement.replace("_", "-")}.csv', parse_dates=['date'])
        df = df_hist.query(f'(reps>={i})').sort_values('date')
        dfi = np.maximum.accumulate(df).set_index('date')[['weights']].rename(
            columns={'weights': movement}).sort_index().drop_duplicates().groupby('date').max().reindex(
            pd.date_range('2019-10-01', datetime.today())
        )
        dfi.index.name='date'
        pr_hist.append(dfi)
    
    plot_pr_hist = pd.concat(pr_hist).dropna(thresh=1).sort_index().fillna(method='bfill').fillna(method='ffill')
    add = plot_pr_hist.iloc[-1,:]
    add.name = datetime.today()
    plot_pr_hist = plot_pr_hist.append(add)

    p, _ = plot_ts(
        plot_pr_hist,
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

plot_pr_history_tabs = Tabs(tabs=tabs, tabs_location='above', margin=(0,0,0,0))

#########################################################################################################
# Calendar plots
#########################################################################################################

df_cal = pd.DataFrame({'date': pd.date_range('2019-09-16', datetime.today())})
df_cal = df_cal.merge(df_hr_rcvry, on='date', how='left').merge(df_wods, on='date', how='left')
df_cal = df_cal[['date','calories', 'max_hr', '120_sec_rec', 'html', '174_220']]

# If WodUp data is available but Wahoo data is not, impute calories to 300
missing_wahoo = df_cal.calories.isna() & (df_cal.html != "<p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p>")
df_cal.loc[missing_wahoo,'calories'] = 500

pcal, pcal_cds = plot_cal(
    df_cal, 
    date_column='date', 
    color_column='calories',
    
    mode='github', 
    fig_args={
        'plot_width':1000,
        'plot_height':150,
        'tools':'hover',
        'toolbar_location':None,
        'x_axis_location':"below"
    }, 
    rect_args={
        'width':1,
        'height':1,
        'line_color':'grey',
        'line_width':1,
        'line_alpha':0.15,
    },
    hover_tooltips=[
        ('Calories','@calories'),
        ('Max HR','@max_hr BPM'),
        ('2-min recovery','@120_sec_rec BPM'),
        ('HR zone (>174 BPM)', '@174_220 s')
    ], 
    show_dates=False
)

pcal_30, pcal_30_cds = plot_cal(
    df_cal.iloc[-31:].copy(), 
    date_column='date', 
    color_column='calories',
    mode='calendar',
    yaxis_major_label_orientation='vertical',
    fig_args={
        'plot_width':400,
        'plot_height':200,
        'tools':'hover',
        'toolbar_location':None,
        'x_axis_location':"above",
        'y_axis_location':"left",
    },
    rect_args={
        'width':1,
        'height':1,
        'line_color':'grey',
        'line_width':1,
        'line_alpha':0.15,
    }, 
    hover_tooltips=[
        ('Calories','@calories'),
        ('Max HR','@max_hr BPM'),
        ('2-min recovery','@120_sec_rec BPM'),
        ('HR zone (>174 BPM)', '@174_220 s'),
        #('WOD','@html{safe}'),
    ], 
    show_dates=True,
    date_text_color='grey'
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
                wod=wods[latest_wodup_log_dt],
            ))

dp_callback = CustomJS(
    args={
        'source': plot_hr_profile_cds,
        'div': div_wodup,
        'wods': wods,
        'html': htmltext.div_wodup
    },

    code=
    """
    div.text = html.replace("{wod}", wods[cb_obj.value])
    //source.data['BPM'] = source.data[cb_obj.value];
    
    if (cb_obj.value in source.data) {
        source.data['BPM'] = source.data[cb_obj.value];
    } else {
        source.data['BPM'] = 0
    }

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

tap_plot_hr_rcvry_callback = CustomJS(args={'p': plot_hr_rcvry_cds, 'r': plot_hr_zones, 'dp': datePicker}, code=hr_tap_code)

plot_hr_rcvry.add_tools(TapTool(callback=tap_plot_hr_rcvry_callback))

url = "https://www.wodup.com/timeline?date=@dt_str"

cal_tap_code = """
    var dt_idx = p.selected.indices[0]
    var dt = p.data['date_str_Ymd'][dt_idx]

    dp.value = dt
    dp.change.emit()
    p.change.emit()
    r.change.emit()
"""

tap_cal_callback = CustomJS(args={'p': pcal_30_cds, 'r': plot_hr_zones, 'dp': datePicker}, code=cal_tap_code)
pcal_30.add_tools(TapTool(callback=tap_cal_callback))

tap_cal_callback = CustomJS(args={'p': pcal_cds, 'r': plot_hr_zones, 'dp': datePicker}, code=cal_tap_code)
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
                    Row(space('60'), pcal_30), 
                    Div(text=htmltext.div_hr_profile), 
                    Row(space('30'), plot_hr_profile), 
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
                    Row(space('30'), plot_hr_rcvry),
                    Row(space('30'), plot_hr_profile)
                ),
                Column(
                    Div(text=htmltext.div_hr_zones), 
                    Row(space('30'), plot_hr_zones)
                )
            )), 
            title="Heart Rate"
            
        ), 
        Panel(
            child=Column(
                Div(text=htmltext.div_weight_lifting.format(three_lift_total)), 
                Div(text=htmltext.div_lift_total.format(three_lift_total)),
                Row(space('30'), plot_pr_history_tabs),
                Row(space('30'), plot_rep_prs), 
            ), 
            title="Weight Lifting"
        ),
        Panel(
            child=Column(
                Div(text=htmltext.div_sleep),
                Row(space('30'), plot_sleep_stages), 
                Row(space('30'), plot_sleep_schedule)
            ), 
            title="Sleep"
        ),
        Panel(
            child=Column(
                Div(text = htmltext.div_program)
            ),
            title="Program"
        )             
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
