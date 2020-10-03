from bokeh.io import show, output_notebook
from bokeh.models import ColumnDataSource, HoverTool, Legend
from bokeh.models.callbacks import CustomJS
from bokeh.plotting import figure
import itertools

    
def plotts(df_plot, 
            ys=None,
            units=None,
            hover_vars=None,
            ts_col='timestamp', 
            styles=['-'],
            palette=['#154ba6', '#3f8dff', '#7ec4ff', '#e73360'],
            bar_width=[24*60*60*900],
            circle_size=7.5,
            title=None,
            plot_height=350,
            plot_width=750,
            ylabel=None,
            xlabel=None,
            x_range=None,
            legend_location='below',
            legend_orientation='horizontal',
            ts_format='%Y-%m-%d %H:%M:%S',
            ymin=None,
            ymax=None,
            add_trace=False
           ):
    
    if ys==None:
        ys=df_plot.columns
    
    if units==None:
        units=['']*len(ys)
    
    df_plot = df_plot.reset_index().copy()
    df_plot['ts_str'] = df_plot[ts_col].dt.strftime(ts_format)
    cds = ColumnDataSource(data=df_plot)
    
    if title == None:
        title = df_plot[ts_col].dt.strftime('%Y-%m-%d %H:%M:%S')[0]
    
    p = figure(
        x_axis_type="datetime",
        plot_height=plot_height,
        plot_width=plot_width,
        x_range=x_range,
        title=title,
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
    if ymin == None:
        ymin = df_plot[ys].min().min()
        
    if ymax == None:
        ymax = df_plot[ys].max().max()
        

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
                size=circle_size,
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
    p.add_layout(legend, legend_location)
    p.legend.click_policy = 'hide'
    p.legend.orientation = legend_orientation
    
    hovers = [(y, f'@{y} {unit}') for y,unit in zip(ys, itertools.cycle(units))] + [['Time', '@ts_str']]
    
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

    if add_trace:
        rL = p.segment(x0='x', y0=ymin, x1='x', y1=ymax, color='grey', line_width=1, source=line_source)
        p.add_tools(
            HoverTool(
                tooltips=None,
                callback=CustomJS(
                    code=js,
                    args={'line_source': line_source}
                )
            )
        )

    p.yaxis.axis_label = ylabel
    p.xaxis.axis_label = xlabel
    
    show(p)
    return cds, p
