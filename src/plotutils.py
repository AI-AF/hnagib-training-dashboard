from bokeh.io import show, output_notebook
from bokeh.models import Band, ColumnDataSource, HoverTool, Legend
from bokeh.models.callbacks import CustomJS
from bokeh.transform import transform
from bokeh.plotting import figure
from bokeh.models import DataRange1d, Range1d, Step, LinearColorMapper
from bokeh.palettes import OrRd
import pandas as pd
import numpy as np
import itertools
from datetime import datetime

    
def plotts(df_plot, 
            ys=None,
            units=None,
            hover_vars=None,
            hide_hovers=[None],
            x_axis_type='datetime',
            xvar='timestamp',
            styles=['-'],
            palette=['#154ba6', '#3f8dff', '#7ec4ff', '#e73360'],
            bar_width=[24*60*60*900],
            circle_size=7.5,
            title=None,
            plot_height=325,
            plot_width=450,
            alphas=[0.75],
            line_width=3,
            bar_line_color='white',
            ylabel=None,
            xlabel=None,
            x_range=None,
            y_range=None,
            legend_position='below',
            legend_location='top_left',
            legend_orientation='horizontal',
            ts_format='%a %b %d %Y',
            bounded_bar_label='bounded',
            show_plot=True,
            tools='',
            active_scroll=None,
            toolbar_location='above'
           ):
    
    if ys is None:
        ys=df_plot.columns

    if units is None:
        units=['']*len(ys)
    
    df_plot = df_plot.reset_index().copy()

    if x_axis_type == 'datetime':
        df_plot['ts_str'] = df_plot[xvar].dt.strftime(ts_format)
        df_plot['dt_str'] = df_plot[xvar].dt.strftime('%Y-%m-%d')

    cds = ColumnDataSource(data=df_plot)

    if y_range: 
        y_range = Range1d(y_range[0], y_range[1])        

    p = figure(
        x_axis_type=x_axis_type,
        plot_height=plot_height,
        plot_width=plot_width,
        x_range=x_range,
        y_range=y_range,
        title=title,
        tools=tools,
        active_scroll=active_scroll,
        active_drag=None,
        toolbar_location=toolbar_location
    )

    # Define a DataSource
    line_source = ColumnDataSource(data=dict(x=[df_plot[xvar][0]]))
    js = '''
    var geometry = cb_data['geometry'];
    console.log(geometry);
    var data = line_source.data;
    var x = data['x'];
    console.log(x);
    if (isFinite(geometry.x)) {
      for (i = 0; i < x.length; i++) {
        x[i] = geometry.x;
      }
      line_source.change.emit();
    }
    '''

    plot_dict = {}
    
#     if styles == ['/']:
#         plot_dict['stack'] = [p.vbar_stack(
#             ys,
#             x=xvar,
#             color=palette,
#             width=bar_width,
#             alpha=0.5,
#             source=cds
#         )]
    
    for y, color, style, width, alpha in zip(ys, itertools.cycle(palette),
                                      itertools.cycle(styles), itertools.cycle(bar_width),
                                      itertools.cycle(alphas)):
        plot_dict[y] = []
        
        if style == "--":
            plot_dict[y].append(p.line(
                x=xvar,
                y=y,
                line_dash="4 4",
                line_width=line_width,
                alpha=alpha,
                color=color, 
                source=cds
            ))    
            
        if ('-' in style) and (style != '--'):
            plot_dict[y].append(p.line(
                x=xvar,
                y=y,
                line_width=line_width,
                alpha=alpha,
                color=color, 
                source=cds
            ))
            
        if ("o" in style) or ("*" in style):
            plot_dict[y].append(p.circle(
                x=xvar,
                y=y,
                size=circle_size,
                color=color,
                alpha=alpha,
                source=cds
            ))
            
        if "|" in style:
            plot_dict[y].append(p.vbar(
                x=xvar,
                top=y,
                fill_color=color,
                line_color=bar_line_color,
                width=width,
                alpha=alpha,
                source=cds
            ))

        if "L" in style:
            glyph = Step(x=xvar, y=y, line_color=color, line_width=line_width, mode="after")
            plot_dict[y].append(p.add_glyph(cds, glyph))

    if "b" in style:
        plot_dict = {}
        plot_dict[bounded_bar_label] = []
        plot_dict[bounded_bar_label].append(p.vbar(
            x=xvar,
            top=ys[0],
            bottom=ys[1],
            fill_color=palette[0],
            line_color=bar_line_color,
            width=width,
            alpha=alpha,
            source=cds
        ))

    legend = Legend(items=[(var, plots) for var, plots in plot_dict.items()])
    p.add_layout(legend, legend_position)
    p.legend.click_policy = 'hide'
    p.legend.orientation = legend_orientation
    p.legend.location = legend_location
    p.legend.background_fill_alpha = 0.15
    p.legend.border_line_alpha = 0

    hovers = [(y, f'@{y} {unit}') for y, unit in zip(list(set(ys)-set(hide_hovers)), itertools.cycle(units))]

    if x_axis_type == 'datetime':
        hovers += [['Date', '@ts_str']]
    elif x_axis_type == 'linear':
        hovers += [[xvar, f'@{xvar}']]

    if hover_vars is not None:
        hovers += [[h, f'@{h}'] for h in hover_vars]
    
    p.add_tools(
        HoverTool(
            renderers=[v[0] for k,v in plot_dict.items()],
            tooltips=hovers, 
            point_policy='snap_to_data',
            line_policy='nearest'
        )
    )

    p.yaxis.axis_label = ylabel
    p.xaxis.axis_label = xlabel

    if show_plot:
        show(p)

    return p, cds


def calendar_array(dates, data):
    i, j = zip(*[d.isocalendar()[1:] for d in dates])
    i = np.array(i) - min(i)
    j = np.array(j) - 1
    ni = max(i) + 1

    calendar = np.nan * np.zeros((ni, 7))
    calendar[i, j] = data
    return i, j, calendar


def plot_hr_profile(df_ts, x='s', y='BPM'):
    p = figure(
        width=450,
        height=325,
        title=f'Workout heart rate profile',
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
    p.line(x, y, source=cds, color="black", alpha=0)

    band = Band(base='s', upper=y, source=cds, level='underlay',
                fill_alpha=0.90, fill_color='#ab383a') #e73360
    p.add_layout(band)
    return p, cds


def plot_sleep_stages(df_sleep, plot_window):
    stages = ["deep", "rem", "light", "awake"]
    colors = ['#154ba6', '#3f8dff', '#7ec4ff', '#e73360']
    data = ColumnDataSource(df_sleep)

    p = figure(
        x_range=DataRange1d(end=datetime.today()+pd.Timedelta('1 days'), follow='end', follow_interval=plot_window),
        x_axis_type="datetime",
        plot_height=400,
        plot_width=800,
        tools='xwheel_pan,pan,reset,box_zoom',
        active_scroll='xwheel_pan',
        toolbar_location='above',
        title="Sleep quality",
    )
    p.add_layout(Legend(), 'below')
    p.vbar_stack(stages, x='date', width=24*60*60*900, color=colors, source=data, legend_label=[s for s in stages])

    for t in [7,8,9]:
        p.line(x='date', y=f'{t}hr', source=data, color='white', line_width=2, line_dash="4 4")

    p.line(x='date', y='7day_avg', source=data, line_width=3, legend_label='7day_avg')
    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.add_tools(HoverTool(
            tooltips=[
                ("Awake", "@awake"),
                ("REM", "@rem"),
                ("Light", "@light"),
                ("Deep", "@deep"),
                ("7day avg", "@7day_avg"),
                ("Date", "@date_str")
            ]
        ))
    p.outline_line_color = None
    p.legend.click_policy = 'hide'
    p.legend.orientation = "horizontal"
    p.legend.border_line_alpha = 0
    p.yaxis.axis_label = 'Hours'

    return p, data


def gen_cal_plot_df(date, cals, wods, sleep, start, end):
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
        {'cals': 0, 'A': '', 'B': '', 'C': '', 'D': ''}
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
        'Week': [f"{i}" for i in cal[0]],
        'Cals': cal[2][~np.isnan(cal[2])],
    })

    return df


def plotcal(
    df, 
    x='Day',
    y='Week',
    text_color='grey',
    text_font='courier',
    palette=OrRd[9],
    weekdays=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    color_column='Cals',
    mode='calendar',
    fig_args={
        'plot_width':300,
        'plot_height':200,
        'toolbar_location':None,
        'tools':'hover',
        'x_axis_location':"above"
    },
    rect_args={
        'width':1,
        'height':1,
        'line_color':'white',
        'line_width':0,
    },

    hover_tooltips=[
        ("Date", "@Date"),
        ("Calories", f"@Cals"),
        ("", "@A{safe}"),
        ("", "@B{safe}"),
        ("", "@C{safe}"),
        ("", "@D{safe}")
    ],
    show_dates=True

    ):
    
    source = ColumnDataSource(df)
    mapper = LinearColorMapper(palette=palette, low=df[color_column].max(), high=df[color_column].min())

    if mode == 'calendar':
        range_args ={
            'x_range':weekdays,
            'y_range':list(reversed(list(df['Week'].unique())))
        }
        xy = {'x':x, 'y':y}

    elif mode == 'github':
        range_args ={
            'x_range':list(df['Week'].unique()),
            'y_range':weekdays
        }
        xy = {'x':y, 'y':x}
    
    p = figure(**{**fig_args, **range_args})

    rect_renderer = p.rect(
        **{**rect_args, **xy}, 
        source=source, 
        fill_color=transform(color_column, mapper)
    )

    if show_dates:
        text_renderer = p.text(
            **xy, text='dom',
            text_align='center',
            text_baseline='middle',
            text_color=text_color,
            text_font=text_font,
            source=source
        )

    if range_args['x_range'] != weekdays:
        p.xaxis.major_label_text_font_size = '0px'

    if range_args['y_range'] != weekdays:
        p.yaxis.major_label_text_font_size = '0pt'

    p.axis.major_label_text_color=text_color
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.outline_line_color = None
    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_standoff = 0
    
    p.hover.tooltips = hover_tooltips
    rect_renderer.nonselection_glyph.fill_alpha=1

    return p, source

