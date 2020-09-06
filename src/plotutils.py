from bokeh.io import show, output_notebook
from bokeh.models import ColumnDataSource, HoverTool, Legend
from bokeh.models.callbacks import CustomJS
from bokeh.palettes import Spectral6, Dark2, inferno
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from bokeh.models import Range1d
import datetime
import itertools
import math

    
def plotts(df_plot, 
            ys=None, 
            hover_vars=None,
            ts_col='timestamp', 
            styles=['-'],
            palette=['#154ba6', '#3f8dff', '#7ec4ff', '#e73360'],
            bar_width=[24*60*60*5000],
            title=None,
            plot_height=300,
            plot_width=750,
            ylabel=None,
            xlabel=None,
            x_range=None,
            legend_location='bottom_left',
            legend_orientation='horizontal'
           ):
    
    if ys==None:
        ys=df_plot.columns
    
    df_plot = df_plot.reset_index().copy()
    df_plot['ts_str'] = df_plot[ts_col].dt.strftime('%H:%M:%S')
    cds = ColumnDataSource(data=df_plot)
    
    p = figure(
        x_axis_type="datetime",
        plot_height=plot_height,
        plot_width=plot_width,
        x_range=x_range,
        title=df_plot[ts_col].dt.strftime('%Y-%m-%d %H:%M:%S')[0],
    )
    
    # Define a DataSource
    line_source = ColumnDataSource(data=dict(x=[df_plot[ts_col][0]]))
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
    rL = p.segment(x0='x', y0=-50, x1='x', y1=200, color='grey', line_width=1, source=line_source)
    
    plot_dict = {}
    
    for y, color, style, width in zip(ys, itertools.cycle(palette), itertools.cycle(styles), itertools.cycle(bar_width)):
        plot_dict[y] = []
        
        if style == "--":
            plot_dict[y].append(p.line(
                x=ts_col,
                y=y,
                line_dash="4 4",
                color=color, 
                source=cds
            ))    
            
        if ('-' in style) and (style != '--'):
            plot_dict[y].append(p.line(
                x=ts_col,
                y=y, 
                color=color, 
                source=cds
            ))
            
        if ("o" in style) or ("*" in style):
            plot_dict[y].append(p.circle(
                x=ts_col,
                y=y, 
                color=color,
                alpha=0.5,
                source=cds
            ))
            
        if ("|" in style):
            plot_dict[y].append(p.vbar(
                x=ts_col,
                top=y,
                fill_color=color,
                width=width,
                alpha=0.5,
                source=cds
            ))
            
        #p.add_tools(HoverTool(renderers=[plot_dict[y]], mode='hline'))
    
    legend = Legend(items=[(var, plots) for var, plots in plot_dict.items()])
    p.add_layout(legend)
    p.legend.click_policy = 'hide'
    p.legend.location = legend_location
    p.legend.orientation = legend_orientation
    
    hovers = [(y, f'@{y} bpm') for y in ys] + [['Time', '@ts_str']]
    
    if hover_vars is not None:
        hovers += [[h, f'@{h}'] for h in hover_vars]
       
    p.add_tools(HoverTool(
        tooltips=None,
        callback=CustomJS(code=js, args={'line_source': line_source})))
    
    p.add_tools(HoverTool(
        renderers=[v[0] for k,v in plot_dict.items()],
        tooltips=hovers, 
        point_policy='snap_to_data',
        line_policy='nearest')
    )
            
    
    p.yaxis.axis_label = ylabel
    p.xaxis.axis_label = xlabel
    
    
    show(p)
    return p
