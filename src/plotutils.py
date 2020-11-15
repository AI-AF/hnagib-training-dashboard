from bokeh.io import show, output_notebook
from bokeh.models import Band, ColumnDataSource, HoverTool, Legend
from bokeh.models.callbacks import CustomJS
from bokeh.transform import transform
from bokeh.plotting import figure
from bokeh.models import DataRange1d, Range1d, Step, LinearColorMapper, SingleIntervalTicker
from bokeh.palettes import OrRd, Blues, Reds
import pandas as pd
import numpy as np
import itertools
from datetime import datetime

    
def plot_ts(df_plot, 
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


def calendar_array(dates, data):
    i, j = zip(*[d.isocalendar()[1:] for d in dates])
    i = np.array(i) - min(i)
    j = np.array(j) - 1
    ni = max(i) + 1

    calendar = np.nan * np.zeros((ni, 7))
    calendar[i, j] = data
    return i, j, calendar


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


def plot_cal(
    df, 
    date_column,
    color_column,
    mode='calendar',
    nan_color='white',
    color_low_value=None,
    color_high_value=None,
    hover_tooltips=None,
    major_label_text_color='grey',
    text_font='courier',
    palette=OrRd[9][::-1], #Blues[9][::-1], #['#7ec4ff', '#3f8dff', '#154ba6'], #'#e73360'], OrRd[9][::-1],
    weekdays=None,
    xaxis_major_label_orientation='horizontal',
    yaxis_major_label_orientation='horizontal',
    x_range=(0, 45),
    y_range=(0, 4),
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
    show_dates=True,
    date_text_color='#e73360'
):
    """
    Function making calendar heatmap plots using Bokeh.

    :param df: pandas DataFrame with date_column in datetime format
    :param date_column: name of the date column
    :param color_column: name of the column to use for heatmap colors
    :param mode: "github" for github contribution like calendar, "calendar" for standard calendar layout
    :param nan_color: color for NaN values of color_column
    :param palette: heatmap color palette
    :param color_low_value: low value to map to color palette
    :param color_high_value: high value to map to color palette
    :param hover_tooltips: bokeh hover tooltips
    :param text_color: text color for axis labels
    :param text_font: text font size for axis labels
    :param weekdays: weekday label ordering e.g. ['Mon', 'Tue'..., 'Sun']
    :param xaxis_major_label_orientation: "vertical" or "horizontal"
    :param yaxis_major_label_orientation: "vertical" or "horizontal"
    :param fig_args: Bokeh figure() args
    :param rect_args: Bokeh Rect() args
    :param show_dates: bool; show calendar dates on plot
    :return: plot obj, plot column data source obj
    """
    
    x = 'day'
    y = 'week'
    day_of_month_column = 'dom'
    
    df['date_str_abdY'] = df[date_column].dt.strftime('%a %b %d, %Y')
    df['date_str_Ymd'] = df[date_column].dt.strftime('%Y-%m-%d')
    df['month'] = df[date_column].dt.strftime('%b')
    df['year'] = df[date_column].dt.strftime('%y')
    df[x] = df[date_column].dt.strftime('%a')
    df[day_of_month_column] = df[date_column].dt.day
    
    if not color_low_value:
        color_low_value = df[color_column].min()
        
    if not color_high_value:
        color_high_value = df[color_column].min()
    
    mapper = LinearColorMapper(
        palette=palette, 
        low=df[color_column].min(), 
        high=df[color_column].max(),
        nan_color=nan_color
    )

    if mode == 'calendar':
        df[y] = (df[date_column].dt.weekday == 0).cumsum()
        
        if not weekdays:
            weekdays=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            
        range_args ={
            'x_range':weekdays,
            'y_range':Range1d(y_range[0]-0.5, y_range[1]+0.5)#Range1d(float(df[y].min())-0.5, float(df[y].max())+0.5)#list(reversed([i(i) for i in df[y].unique()]))
        }
        xy = {'x':x, 'y':y}

    elif mode == 'github':
        df[y] = (df[date_column].dt.weekday == 6).cumsum()
        
        if not weekdays:
            weekdays=list(reversed(['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']))

        range_args ={
            'x_range':Range1d(x_range[0]-0.5, x_range[1]+0.5),#Range1d(float(df[y].min())-0.5, float(df[y].max())+0.5), #Range1d(-1,53),  #[i(i) for i in df[y].unique()],
            'y_range':weekdays
        }
        xy = {'x':y, 'y':x}
    
    df[y] = df[y].max() - df[y]
    source = ColumnDataSource(df)
    p = figure(**{**fig_args, **range_args})

    rect_renderer = p.rect(
        **{**rect_args, **xy}, 
        source=source, 
        fill_color=transform(color_column, mapper)
    )

    if show_dates:
        text_renderer = p.text(
            **xy, 
            text=day_of_month_column,
            text_align='center',
            text_baseline='middle',
            text_color=date_text_color,
            text_font=text_font,
            source=source
        )
        text_renderer.nonselection_glyph.text_alpha=1

    if range_args['x_range'] != weekdays:
        p.xaxis.ticker = SingleIntervalTicker(interval=1)

    if range_args['y_range'] != weekdays:
        p.yaxis.ticker = SingleIntervalTicker(interval=1)

    labels = {}
    for k,v in dict(df.groupby(['month', 'year'])[y].min()).items():
        if k[0] == 'Jan':
            # Add year annotation for each January in data
            labels[int(v)]=f"'{k[1]} {k[0]}"
        else:
            labels[int(v)]=k[0]
    
    for i in df[y].unique():
        if i not in labels.keys():
            labels[int(i)] = ''
            
    p.axis.major_label_overrides = labels
    p.xaxis.major_label_orientation = xaxis_major_label_orientation 
    p.yaxis.major_label_orientation = yaxis_major_label_orientation 
    p.axis.major_label_text_color=major_label_text_color
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.outline_line_color = None
    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.minor_tick_line_color = None
    p.axis.major_label_standoff = 0
    p.hover.tooltips = [('Date','@date_str_abdY')] + hover_tooltips
    rect_renderer.nonselection_glyph.fill_alpha=1

    return p, source
