import glob
import os
import time
import dask
import pandas as pd
import numpy as np
from scipy import stats
from plotutils import plot_ts, gen_cal_plot_df, plot_cal, plot_hr_profile, plot_sleep_stages, plot_stacked_hr_zones
from bokeh.io import save, output_file
from bokeh.plotting import figure
from bokeh.layouts import Column, Row
from bokeh.models.widgets import DatePicker, Panel, Tabs, Select, Slider
from bokeh.models import (FixedTicker, HoverTool, CustomJS, Div, ColumnDataSource, LinearAxis,
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
    df_hr_rcvry,
    ys=['120_sec_rec', 'L2', 'L1', 'L0', 'L3'],
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

plot_stacked_hr = plot_stacked_hr_zones(plot_hr_rcvry_cds, plot_hr_rcvry.x_range)


plot_hr_zones, plot_hr_zones_cds = plot_ts(
    (df_hr_rcvry.rolling('7d').sum().dropna()),
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


plot_window = pd.Timedelta('365 days')

# Prep sleep dataframe for plotting
plot_sleep_scatter_initial_x = 'start_hour'#'end_last_7day_stdev'
plot_sleep_scatter_initial_y = 'time_asleep'

df_sleep['x'] = df_sleep[plot_sleep_scatter_initial_x]
df_sleep['y'] = df_sleep[plot_sleep_scatter_initial_y]
df_sleep['color'] = 'grey'

# Impute missing data with mean 
for col in df_sleep.columns:
    if df_sleep[col].isna().sum() > 0:
        df_sleep[col].fillna(value=df_sleep[col].mean(), inplace=True)


plot_sleep_stages, plot_sleep_stages_cds = plot_sleep_stages(
    df_sleep, 
    plot_window, 
    plot_height=300,
    plot_width=450
    )

plot_sleep_schedule, plot_sleep_schedule_cds = plot_ts(
    df_sleep,
    source=plot_sleep_stages_cds,
    plot_height=300,
    plot_width=450,
    alphas=[0.95],
    xvar='date',
    ys=['end_hour', 'start_hour_rel'],
    hover_vars=['start_time', 'end_time', 'time_asleep'],
    hide_hovers=['start_hour_rel', 'end_hour'],
    units=['hour'],
    x_range=plot_sleep_stages.x_range,
    y_range=[-8, 10],
    title='Sleep schedule',
    styles=['b'],
    palette=['grey'], #'#154ba6', '#3f8dff', '#7ec4ff', '#e73360'
    bounded_bar_label='sleep logs',
    tools='lasso_select,box_select,xwheel_pan,pan,reset,box_zoom',
    active_drag='box_select',
    show_plot=False
);

#'#3f8dff', '#7ec4ff',
#'#e73360', '#154ba6'
plot_sleep_schedule.line(x="date", y='5hr', color="grey", line_dash="4 2", line_width=2, alpha=0.95, source=plot_sleep_schedule_cds)
plot_sleep_schedule.line(x="date", y='-4hr', color="grey", line_dash="4 2", line_width=2, alpha=0.95, source=plot_sleep_schedule_cds)
plot_sleep_schedule.line(x="date", y='start_rel_last_7day_avg', legend_label="bed time", color="#706897", line_width=3, alpha=0.95, source=plot_sleep_schedule_cds)
plot_sleep_schedule.line(x="date", y='end_last_7day_avg', legend_label="wake up time", color="#AA4A30", line_width=3, alpha=0.95, source=plot_sleep_schedule_cds)

hour_label = {
    -6:'6 pm',
    -4:'8 pm',
    -2:'10 pm',
     0:'12 am',
     2:'2 am',
     4:'4 am',
     6:'6 am',
     8:'8 am'
}

tick_label = {}
for i in range(-8,11):
    if i in hour_label.keys():
        tick_label[i] = hour_label[i]
    else:
        tick_label[i] = ''

plot_sleep_schedule.yaxis.ticker =  FixedTicker(ticks=list(hour_label.keys()))
plot_sleep_schedule.yaxis.major_label_overrides = tick_label
#plot_sleep_schedule.yaxis.minor_label_overrides = tick_label


plot_sleep_scatter = figure(
    plot_height=400,
    plot_width=450,
    tools="lasso_select, pan, box_zoom, box_select, reset",
    toolbar_location='right',
    title="",
    x_axis_label=f'{plot_sleep_scatter_initial_x} (hours)', 
    active_drag='box_select',
    y_axis_label=f'{plot_sleep_scatter_initial_y} (hours)'
)


plot_sleep_scatter.circle(
    x='x', 
    y='y', 
    size=7,
    alpha=0.25,
    color='color',#'#3f8dff', #154ba6', #, '#3f8dff', '#7ec4ff', '#e73360'],
    source=plot_sleep_schedule_cds
)

plot_sleep_scatter.add_tools(HoverTool(
        tooltips=[
            ("Date", "@date_str"),
            ("Time asleep", "@time_asleep"),
            ("Start", "@start_time"),
            ("End", "@end_time"),
            ("Deep", "@deep"),
            ("REM", "@rem"),
            ("Light", "@light"),
            ("Awake", "@awake"),
        ]
    ))

slope, intercept, r_value, p_value, std_err = stats.linregress(df_sleep['x'], df_sleep['y'])
import statsmodels.api as sm

reg = sm.OLS(df_sleep['y'], sm.add_constant(df_sleep['x'])).fit()
print(reg.summary())


div_smry = Div(text=htmltext.div_smry.format(

    b0="{:.3f}".format(reg.params[0]),
    se_b0="{:.3f}".format(reg.HC3_se[0]),
    t_b0="{:.3f}".format(reg.tvalues[0]),
    p_b0="{:.3f}".format(reg.pvalues[0]),
    ci_025_b0="{:.3f}".format(reg.conf_int()[0][0]),
    ci_975_b0 ="{:.3f}".format(reg.conf_int()[1][0]),

    b1="{:.3f}".format(reg.params[1]),
    se_b1="{:.3f}".format(reg.HC3_se[1]),
    t_b1="{:.3f}".format(reg.tvalues[1]),
    p_b1="{:.3f}".format(reg.pvalues[1]),
    ci_025_b1="{:.3f}".format(reg.conf_int()[0][1]),
    ci_975_b1 ="{:.3f}".format(reg.conf_int()[1][1]),
))

div_sample_smry = Div(text=htmltext.div_sample_smry.format(
    n_total="{:.0f}".format(df_sleep.shape[0]),
    n_selected="{:.0f}".format(df_sleep.shape[0]),
    avg_x="{:.3f}".format(df_sleep['x'].mean()),
    avg_y="{:.3f}".format(df_sleep['y'].mean())
))

avgline_x_cds = ColumnDataSource(data={'x':[df_sleep['x'].min(), df_sleep['x'].max()], 'y':[df_sleep['y'].mean(), df_sleep['y'].mean()]})
plot_sleep_scatter.line(
    x='x', 
    y='y', 
    color="#e73360",#'firebrick', #154ba6',# '#3f8dff',#"#154ba6", 
    line_width=3,
    line_dash="8 4", 
    alpha=0.9, 
    source=avgline_x_cds,
    #legend_label='ave'
)

avgline_y_cds = ColumnDataSource(data={'y':[df_sleep['y'].min(), df_sleep['y'].max()], 'x':[df_sleep['x'].mean(), df_sleep['x'].mean()]})
plot_sleep_scatter.line(
    x='x', 
    y='y', 
    color="#e73360",#'firebrick', #154ba6',#'#3f8dff',#"#154ba6", 
    line_width=3,
    line_dash="8 4", 
    alpha=0.9, 
    source=avgline_y_cds,
    legend_label='avg'
)

regline_cds = ColumnDataSource(data={'x':[df_sleep['x'].min(), df_sleep['x'].max()], 'y':[df_sleep['x'].min()*(slope)+intercept, df_sleep['x'].max()*(slope)+intercept]})
plot_sleep_scatter.line(
    x='x', 
    y='y', 
    color='#154ba6',
    line_width=3,
    #line_dash="8 4", 
    alpha=0.90, 
    source=regline_cds,
    legend_label='reg'
)

legend = Legend()
plot_sleep_scatter.add_layout(legend, 'center')
plot_sleep_scatter.legend.orientation = 'vertical'
plot_sleep_scatter.legend.location = 'bottom_left'
plot_sleep_scatter.legend.click_policy = 'hide'

plot_sleep_scatter.legend.background_fill_alpha = 0.5
plot_sleep_scatter.legend.border_line_alpha = 0



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
    plot_height=250, #350,
    plot_width=700, #900,
    show_plot=False,
    tools='box_zoom,undo,redo,reset',
    palette=['#154ba6', '#3f8dff', '#7ec4ff', 'grey'],
    legend_position='right',
    legend_location='top_right',
    legend_orientation='vertical',

)

tabs = []
df_pr_hist = {}

for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:

    pr_hist = []
    for movement in movements:
        df_hist = pd.read_csv(f'../../WodUp-Scraper/data/hasannagib-{movement.replace("_", "-")}.csv', parse_dates=['date'])
        df = df_hist.query(f'(reps>={i})').sort_values('date')
        dfi = np.maximum.accumulate(df).set_index('date')[['weights']].rename(
            columns={'weights': movement}).sort_index().drop_duplicates().groupby('date').max()
        dfi.index.name='date'
        pr_hist.append(dfi)
    
    plot_pr_hist = pd.concat(pr_hist).dropna(thresh=1).sort_index().fillna(method='ffill').groupby('date').max()
    df_pr_hist[i] = plot_pr_hist
    add = plot_pr_hist.iloc[-1,:]
    add.name = datetime.today()
    plot_pr_hist = plot_pr_hist.append(add)

    p, _ = plot_ts(
        plot_pr_hist,
        xvar='date',
        styles=['oL'],
        units=['lbs'],
        circle_size=3,
        x_axis_type='datetime',
        title=f'{i} rep max PR over time ',
        xlabel='Date',
        ylabel='Weight (lbs)',
        plot_height=250,#350,
        plot_width=700,#900,
        tools='box_zoom,undo,redo,reset',
        palette=['#154ba6', '#3f8dff', '#7ec4ff', 'grey'], #e73360
        show_plot=False,
        legend_position='right',
        legend_location='top_right',
        legend_orientation='vertical',

    );

    tabs.append(Panel(child=p, title=f"{i}"))

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
        'plot_height':175,
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
    df_cal,#.iloc[-31:].copy(), 
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


for i, df in df_pr_hist.items():
    df_pr_hist[i]['Y'] = df[df.columns[0]]

df_pr_cal = {}
plot_pr_cal = {}
cds_pr_cal = {}

for mvmt in movements + ['Y']:
    df_pr_cal[mvmt] = {}
    plot_pr_cal[mvmt] = {}
    cds_pr_cal[mvmt] = {}
    
    for i in [1,2,3,4,5,6,7,8,9,10]:
        df = df_pr_hist[i][[mvmt]].reset_index().groupby(mvmt).min().reset_index().set_index('date')
        df = df.reindex(pd.date_range('2019-09-16', datetime.today()))
        df.index.name = 'date'
        df = df.reset_index().rename(columns={mvmt:'weight'})
        
        p, p_cds = plot_cal(
            df, 
            date_column='date', 
            color_column='weight',
            palette=['#e73360'],
            mode='github',
            x_range=[0, 60], 
            fig_args={
                'plot_width':900,
                'plot_height':125,
                'tools':'hover',
                'toolbar_location':None,
                'x_axis_location':"above"
            }, 
            rect_args={
                'width':1,
                'height':1,
                'line_color':'grey',
                'line_width':1,
            },
            hover_tooltips=[('Weight',f'@weight lbs')], 
            show_dates=False
        )
        
        df_pr_cal[mvmt][i] = df
        plot_pr_cal[mvmt][i] = p
        cds_pr_cal[mvmt][i] = p_cds

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
plot_stacked_hr.add_tools(TapTool(callback=tap_plot_hr_rcvry_callback))

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

# Slider and select for PR calendar
mvmt_name_mapper = {
    'Bench Press':'barbell_bench_press',
    'Shoulder Press':'shoulder_press',
    'Back Squat':'back_squat',
    'Deadlift':'deadlift',
}

select = Select(title="Movement", value="Deadlift", options=list(mvmt_name_mapper.keys()), width=200)
slider = Slider(start=1, end=10, value=1, step=1, title="Reps", width=200)

select.js_on_change(
    "value", 
    CustomJS(
        args={
            'p1_cds':cds_pr_cal['Y'][1],
            'cds_pr_cal':cds_pr_cal, 
            'slider':slider,
            'mvmt_name_mapper':mvmt_name_mapper
        },
        code="""            
            const select_value = mvmt_name_mapper[cb_obj.value]
            p1_cds.data = cds_pr_cal[select_value][slider.value].data
            p1_cds.change.emit()
        """
    )
)

slider.js_on_change(
    'value', 
    CustomJS(
        args={
            'p1_cds':cds_pr_cal['Y'][1],
            'cds_pr_cal':cds_pr_cal,
            'select':select,
            'mvmt_name_mapper':mvmt_name_mapper
        },
        code="""
            const select_value = mvmt_name_mapper[select.value]
            p1_cds.data = cds_pr_cal[select_value][cb_obj.value].data
            p1_cds.change.emit()
        """
    )
)

# Horozontal range slider for gitub calendar plot
date_slider_callback = CustomJS(args=dict(p=pcal), code="""
    var a = cb_obj.value;
    var delta = p.x_range.end - p.x_range.start
    p.x_range.start = a;
    p.x_range.end = a+delta;
""")

date_slider = Slider(
    start=-0.5, 
    end=df_cal['week'].max() - (pcal.x_range.end - pcal.x_range.start)+0.5, 
    value=-0.5, 
    step=1, 
    show_value=False, 
    width=220,
    tooltips=False
)
date_slider.js_on_change('value', date_slider_callback)

# Vertical range slider for calendar plot
date_slider_30_callback = CustomJS(args=dict(p=pcal_30), code="""
    var a = cb_obj.value;
    var delta = p.y_range.end - p.y_range.start
    p.y_range.start = a;
    p.y_range.end = a+delta;
""")

date_slider_30 = Slider(
    start=-0.5, 
    end=df_cal['week'].max() - (pcal_30.y_range.end - pcal_30.y_range.start)+0.5, 
    value=0, 
    step=1, 
    show_value=False,
    height=200,
    orientation='vertical',
    direction='rtl',
    tooltips=False
)
date_slider_30.js_on_change('value', date_slider_30_callback)


select_sleep_scatter_x = Select(
    title="X", 
    value=plot_sleep_scatter_initial_x, 
    options=[
        'deep', 'rem', 'light', 'awake',
        'start_hour', 'end_hour', 'time_asleep',
        'start_last_3day_avg', 'end_last_3day_avg', 
        'start_last_3day_stdev', 'end_last_3day_stdev', 
        'start_last_7day_avg', 'end_last_7day_avg', 
        'start_last_7day_stdev', 'end_last_7day_stdev', 
        'start_hour_prev_day', 'end_hour_prev_day', 'time_asleep_prev_day'
    ], 
    width=190
    )

select_sleep_scatter_y = Select(
    title="Y", 
    value=plot_sleep_scatter_initial_y, 
    options=[
        'deep', 'awake', 'light', 'rem', 
        'time_asleep', 'efficiency',
        '7day_avg', 'start_hour', 'end_hour'], 
    width=190
    )

sleep_scatter_code = """
    const x_range_start = Math.min(...s.data[sx.value])
    const x_range_end = Math.max(...s.data[sx.value])
    const y_range_start = Math.min(...s.data[sy.value])
    const y_range_end = Math.max(...s.data[sy.value]) 

    const [m, b, se_m, se_b] = linearRegression(xm, ym)

    const average_ym = average(ym)
    const average_xm = average(xm)

    var reg_x0 = x_range_start
    var reg_x1 = x_range_end
    var reg_y0 = x_range_start*m+b
    var reg_y1 = x_range_end*m+b
    if (reg_y0 > y_range_end) { reg_x0 = (y_range_end - b)/m; reg_y0 = reg_x0*m+b}
    if (reg_y0 < y_range_start) { reg_x0 = (y_range_start - b)/m; reg_y0 = reg_x0*m+b}
    if (reg_y1 > y_range_end) { reg_x1 = (y_range_end - b)/m; reg_y1 = reg_x1*m+b}
    if (reg_y1 < y_range_start) { reg_x1 = (y_range_start - b)/m; reg_y1 = reg_x1*m+b}

    s2.data['x'] = [reg_x0, reg_x1]
    s2.data['y'] = [reg_y0, reg_y1]
    s3.data['x'] = [x_range_start, x_range_end] 
    s3.data['y'] = [average_ym, average_ym]
    s4.data['x'] = [average_xm, average_xm]
    s4.data['y'] = [y_range_start, y_range_end]  

    const se_b0 = se_b
    const t_b0 = b/se_b
    const p_b0 = jStat.ztest(t_b0, 0, 1, 2)
    const ci_025_b0 = b - 1.96*se_b 
    const ci_975_b0 = b + 1.96*se_b

    const se_b1 = se_m
    const t_b1 = m/se_m
    const p_b1 = jStat.ztest(t_b1, 0, 1, 2)
    const ci_025_b1 = m - 1.96*se_m 
    const ci_975_b1 = m + 1.96*se_m

    const dec_places = 3
    document.getElementById("se_b1").textContent=se_b1.toFixed(dec_places);
    document.getElementById("t_b1").textContent=t_b1.toFixed(dec_places);
    document.getElementById("p_b1").textContent=p_b1.toFixed(dec_places);
    document.getElementById("ci_025_b1").textContent=ci_025_b1.toFixed(dec_places);
    document.getElementById("ci_975_b1").textContent=ci_975_b1.toFixed(dec_places);

    document.getElementById("se_b0").textContent=se_b0.toFixed(dec_places);
    document.getElementById("t_b0").textContent=t_b0.toFixed(dec_places);
    document.getElementById("p_b0").textContent=p_b0.toFixed(dec_places);
    document.getElementById("ci_025_b0").textContent=ci_025_b0.toFixed(dec_places);
    document.getElementById("ci_975_b0").textContent=ci_975_b0.toFixed(dec_places);

    const n_total = s.data['x'].length
    const n_selected = xm.length

    document.getElementById("n_total").textContent=n_total.toFixed(0);
    document.getElementById("n_selected").textContent=n_selected.toFixed(0);
    document.getElementById("avg_x").textContent=average_xm.toFixed(dec_places);
    document.getElementById("avg_y").textContent=average_ym.toFixed(dec_places);


    document.getElementById("b0").textContent=b.toFixed(dec_places);
    document.getElementById("b1").textContent=m.toFixed(dec_places);
    //document.getElementById("n_total").textContent=d['y'].length;
    //document.getElementById("n_selected").textContent=xm.length;
"""

plot_sleep_schedule_cds.selected.js_on_change(
    'indices', 
    CustomJS(
        args={
        's':plot_sleep_schedule_cds, 
        's2':regline_cds, 
        's3':avgline_x_cds,
        's4':avgline_y_cds, 
        'sx':select_sleep_scatter_x, 
        'sy':select_sleep_scatter_y,
        'p':plot_sleep_scatter,
        },
        code="""
            
            const inds = s.selected.indices;
            const d = s.data;

            var ym = []
            var xm = []

            for (var i = 0; i < d['color'].length; i++) {
                d['color'][i] = "grey"
            }

            if (inds.length == 0) {
                return;
            }

            else if (inds.length == 1){
                s2.data['y'] = [d[sy.value][inds[0]], d[sy.value][inds[0]]]
                s3.data['y'] = [d[sy.value][inds[0]], d[sy.value][inds[0]]]
                s4.data['x'] = [d[sx.value][inds[0]], d[sx.value][inds[0]]]
            }

            else if (inds.length > 1){

                for (var i = 0; i < inds.length; i++) {
                    ym.push(d[sy.value][inds[i]])
                    xm.push(d[sx.value][inds[i]])
                    d['color'][inds[i]] = "firebrick"
                }

                {code}
            }

        s.change.emit();
        s2.change.emit();
        s3.change.emit();
        s4.change.emit();
        """.replace("{code}", sleep_scatter_code)
    )
)

plot_sleep_scatter.js_on_event('reset', CustomJS(
        args={
            's':plot_sleep_schedule_cds, 
            's2':regline_cds, 
            's3':avgline_x_cds,
            's4':avgline_y_cds, 
            'sx':select_sleep_scatter_x, 
            'sy':select_sleep_scatter_y, 
            'p':plot_sleep_scatter,
        },
        code="""
        const d = s.data;
        var xm = [].slice.call(d[sx.value])
        var ym = [].slice.call(d[sy.value])

        for (var i = 0; i < d['color'].length; i++) {
            d['color'][i] = "grey"
        }

        {code}      

        s.change.emit();
        s2.change.emit();
        s3.change.emit();
        s4.change.emit();
        """.replace("{code}", sleep_scatter_code)
))


select_sleep_scatter_x.js_on_change(
    "value", 
    CustomJS(
        args={
            's':plot_sleep_stages_cds, 
            's2':regline_cds, 
            's3':avgline_x_cds,
            's4':avgline_y_cds, 
            'p':plot_sleep_scatter,
            'sx':select_sleep_scatter_x, 
            'sy':select_sleep_scatter_y,
            'xaxis':plot_sleep_scatter.xaxis[0], 
            'yaxis':plot_sleep_scatter.yaxis[0],
        },
        code="""    
            const inds = s.selected.indices;  
            const d = s.data;
            const select_value = cb_obj.value
            d['x'] = d[select_value]

            if (inds.length > 1){
                var xm = []
                var ym = []

                for (var i = 0; i < inds.length; i++) {
                    ym.push(d[sy.value][inds[i]])
                    xm.push(d[sx.value][inds[i]])
                }
            }
            else {
                var xm = [].slice.call(d['x'])
                var ym = [].slice.call(d['y'])
            }

            {code}      

            xaxis.axis_label = sx.value + " (hours)";
            yaxis.axis_label = sy.value + " (hours)";    
            s.change.emit();
            s2.change.emit();
            s3.change.emit();
            s4.change.emit();
        """.replace("{code}", sleep_scatter_code)
    )
)

select_sleep_scatter_y.js_on_change(
    "value", 
    CustomJS(
        args={
            's':plot_sleep_stages_cds, 
            's2':regline_cds, 
            's3':avgline_x_cds,
            's4':avgline_y_cds, 
            'p':plot_sleep_scatter,
            'sx':select_sleep_scatter_x, 
            'sy':select_sleep_scatter_y,
            'xaxis':plot_sleep_scatter.xaxis[0], 
            'yaxis':plot_sleep_scatter.yaxis[0],
        },
        code="""  
            const inds = s.selected.indices;    
            const d = s.data;
            const select_value = cb_obj.value
            d['y'] = d[select_value]


            if (inds.length > 1){
                var xm = []
                var ym = []

                for (var i = 0; i < inds.length; i++) {
                    ym.push(d[sy.value][inds[i]])
                    xm.push(d[sx.value][inds[i]])
                }
            }
            else {
                var xm = [].slice.call(d['x'])
                var ym = [].slice.call(d['y'])
            }

            {code}     
            
            xaxis.axis_label = sx.value + " (hours)";
            yaxis.axis_label = sy.value + " (hours)";    
            s.change.emit();
            s2.change.emit();
            s3.change.emit();
            s4.change.emit();
        """.replace("{code}", sleep_scatter_code)
    )
)

#########################################################################################################
# Dashboard
#########################################################################################################

def space(width, height=0):
    return Div(text=htmltext.div_space.format(width=width, height=height))


dash = Column(
    Row(space('20'), Div(text=htmltext.div_social)), 
    Column(
        Row(space('40'), date_slider),
        Row(space('40'), pcal)
    ),

    Row(
        space(2),
        Div(text=htmltext.div_intro),
        Div(text=htmltext.div_conclusion),
    ),
    #Div(text=htmltext.div_squatchek),

    Tabs(tabs=[
        Panel(
            child=Row(
                Column(
                    Div(text=htmltext.div_sleep),
                    Row(
                        space('30'), 
                        Column(
                            plot_sleep_stages, 
                            plot_sleep_schedule,
                        ),
                    ),
                    Div(text=htmltext.div_sleep_regression_desc) 
                ),
                Column(
                    Div(text=htmltext.div_sleep_plot), 
                    div_smry,
                    Row(space('70'),select_sleep_scatter_x, select_sleep_scatter_y), 
                    Row(space('30'), Column(plot_sleep_scatter)
                        
                    ),
                    div_sample_smry
                ),
            ),
            title="Sleep"
        ),
        Panel(
            child=Column(
                Div(text=htmltext.div_weight_lifting.format(three_lift_total)), 
                Div(text=htmltext.div_lift_total.format(three_lift_total)),
                Row(space('30'),Column(Row(select, space('30'), slider), Div(text=htmltext.div_pr_cal_header), plot_pr_cal['Y'][1])),
                Row(space('0','30')),
                Row(space('60'), plot_pr_history_tabs),
                Row(space('60'), plot_rep_prs), 
            ), 
            title="Lift PRs"
        ),
        Panel(
            child=Row(
                Column(
                    Div(text=htmltext.div_workout_cal), 
                    Row(space('60'), pcal_30, date_slider_30), 
                    Div(text=htmltext.div_hr_profile), 
                    Row(space('30'), plot_hr_profile), 
                ),
                Column(
                    Div(text=htmltext.div_wod_logs), 
                    Row(space('30'), datePicker), 
                    div_wodup
                )
            ), 
            title="Workouts"
        ),
        Panel(
            child=Row(
                Row(
                Column(
                    Div(text=htmltext.div_hr_rcvry), 
                    Row(space('30'), plot_stacked_hr),
                    Row(space('30'), plot_hr_rcvry),
                ),
                Column(
                    Div(text=htmltext.div_hr_zones), 
                    Row(space('30'), plot_hr_zones),
                    Row(space('30'), plot_hr_profile),
                )
            )), 
            title="Heart Rate"
            
        ), 
        # Panel(
        #     child=Column(
        #         Div(text = htmltext.div_program)
        #     ),
        #     title="Program"
        # )             
    ], 
    sizing_mode='stretch_both', 
    tabs_location='above',
    width_policy='max',
    margin=(0,0,0,50),
    css_classes=['bokeh-plots'],
    ),
)

# Save dashboard
output_dir = '/Users/hasannagib/Documents/hnagib.github.io/index.html'
output_file(output_dir, title="Hasan's Data Blog")
save(dash, template=htmltext.bokeh_template)



