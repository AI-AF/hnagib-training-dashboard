import glob
import os
import time
import dask
import pandas as pd
import numpy as np
from scipy import stats
from plotutils import plot_ts, gen_cal_plot_df, plot_cal, plot_hr_profile, plot_sleep_stages
from bokeh.io import save, output_file
from bokeh.plotting import figure
from bokeh.layouts import Column, Row
from bokeh.models.widgets import DatePicker, Panel, Tabs, Select, Slider
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


plot_window = pd.Timedelta('365 days')

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
    alphas=[0.75],
    xvar='date',
    ys=['end_hour', 'start_hour'],
    hover_vars=['start_time', 'end_time', 'time_asleep'],
    hide_hovers=['start_hour', 'end_hour'],
    units=['hour'],
    x_range=plot_sleep_stages.x_range,
    y_range=[2, 30],
    ylabel='24-Hour',
    title='Sleep schedule',
    styles=['b'],
    palette=['grey'], #'#154ba6', '#3f8dff', '#7ec4ff', '#e73360'
    bounded_bar_label='sleep',
    tools='lasso_select,box_select,xwheel_pan,pan,reset,box_zoom',
    active_drag='box_select',
    show_plot=False
);
plot_sleep_schedule.line(x="date", y='5hr', color="grey", line_dash="4 2", line_width=2, alpha=0.95, source=plot_sleep_schedule_cds)
plot_sleep_schedule.line(x="date", y='20hr', color="grey", line_dash="4 2", line_width=2, alpha=0.95, source=plot_sleep_schedule_cds)
plot_sleep_schedule.line(x="date", y='start_7d_avg', color="grey", line_width=3, alpha=0.95, source=plot_sleep_schedule_cds)
plot_sleep_schedule.line(x="date", y='end_7d_avg', color="grey", line_width=3, alpha=0.95, source=plot_sleep_schedule_cds)


plot_sleep_scatter = figure(
    plot_height=450,
    plot_width=450,
    x_range=(15,30),
    y_range=(3,10),
    tools="lasso_select, box_select, reset",
    toolbar_location='above',
    title="Early bird or night owl?",
    x_axis_label='Start hour',
    y_axis_label='Time asleep (hours)',
)

plot_sleep_scatter.circle(
    x='start_hour', 
    y='time_asleep', 
    size=7,
    alpha=0.5,
    color='grey',#'#3f8dff', #154ba6', #, '#3f8dff', '#7ec4ff', '#e73360'],
    source=plot_sleep_schedule_cds
)

plot_sleep_scatter.add_tools(HoverTool(
        tooltips=[
            ("Duration", "@time_asleep"),
            ("7day avg", "@7day_avg"),
            ("Date", "@date_str"),
            ("Start", "@start_time"),
            ("End", "@end_time"),
        ]
    ))

slope, intercept, r_value, p_value, std_err = stats.linregress(df_sleep['start_hour'], df_sleep['time_asleep'])

regline_cds = ColumnDataSource(data={'x':[0, 30], 'y':[intercept, 30*(slope)+10.42]})
plot_sleep_scatter.line(
    x='x', 
    y='y', 
    color='orange',#"#154ba6", 
    line_width=4,
    line_dash="8 4", 
    alpha=0.9, 
    source=regline_cds,
    legend_label='regression'
)

avgline_cds = ColumnDataSource(data={'x':[0, 30], 'y':[df_sleep['time_asleep'].mean(), df_sleep['time_asleep'].mean()]})
plot_sleep_scatter.line(
    x='x', 
    y='y', 
    color='grey',#"#154ba6", 
    line_width=4,
    line_dash="8 4", 
    alpha=0.9, 
    source=avgline_cds,
    legend_label='average'
)

legend = Legend()
plot_sleep_scatter.add_layout(legend, 'center')
plot_sleep_scatter.legend.orientation = 'vertical'
plot_sleep_scatter.legend.location = 'top_right'
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

select = Select(title="Movement", value="Bench Press", options=list(mvmt_name_mapper.keys()), width=200)
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
            var select_value = mvmt_name_mapper[cb_obj.value]
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
            var select_value = mvmt_name_mapper[select.value]
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


plot_sleep_schedule_cds.selected.js_on_change(
    'indices', 
    CustomJS(
        args={'s':plot_sleep_schedule_cds, 's2':regline_cds, 's3':avgline_cds},
        code="""
            
            const inds = s.selected.indices;
            const d = s.data;
            var ym = []
            var xm = []

            if (inds.length == 0) {
                return;
            }
            else if (inds.length == 1){
                s2.data['y'] = [d['time_asleep'][inds[0]], d['time_asleep'][inds[0]]]
                s3.data['y'] = [d['time_asleep'][inds[0]], d['time_asleep'][inds[0]]]
            }
            else if (inds.length > 1){
                for (var i = 0; i < inds.length; i++) {
                    ym.push(d['time_asleep'][inds[i]])
                    xm.push(d['start_hour'][inds[i]])
                }

                var soln = linearRegression(xm, ym)
                var m = soln[0]
                var b = soln[1]

                s2.data['y'] = [b, 30*m+b]
                s3.data['y'] = [average(ym), average(ym)]
            }
            
        s.change.emit();
        s2.change.emit();
        s3.change.emit();
            
        """
    )
)

plot_sleep_scatter.js_on_event('reset', CustomJS(
        args={'s':plot_sleep_schedule_cds, 's2':regline_cds, 's3':avgline_cds},
        code="""
        const d = s.data;
        var xm = [].slice.call(d['start_hour'])
        var ym = [].slice.call(d['time_asleep'])

        var soln = linearRegression(xm, ym)
        var m = soln[0]
        var b = soln[1]
        
        s2.data['y'] = [b, 30*m+b]        
        s3.data['y'] = [average(ym), average(ym)]

        s2.change.emit();
        s3.change.emit();
        """
))

#########################################################################################################
# Dashboard
#########################################################################################################

def space(width, height=0):
    return Div(text=htmltext.div_space.format(width=width, height=height))


dash = Column(
    Column(
        Div(text=htmltext.div_header), 
        Row(space('40'), date_slider),
        Row(space('40'), pcal)
    ),

    Row(
        space(2),
        Div(text=htmltext.div_intro),
        Div(text=htmltext.div_conclusion),
    ),

    Tabs(tabs=[
        Panel(
            child=Column(
                Div(text=htmltext.div_sleep),
                Row(space('30'), Column(plot_sleep_stages, plot_sleep_schedule), space('30'), plot_sleep_scatter), 
            ), 
            title="Sleep"
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
            title="WODs"
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
            title="Weight Lifting"
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
output_dir = '/Users/hasannagib/Documents/s3stage/dashboards/index.html'
output_file(output_dir, title="Hasan's Data Blog")
save(dash, template=htmltext.bokeh_template)
