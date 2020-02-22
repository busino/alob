'''
Alob Project
2016
Author(s): R.Walker

'''
import logging

from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, ColumnDataSource
import numpy
from bokeh.models.layouts import Row

log = logging.getLogger('alob')


def pair_plot(src, dst_corrected,
              src_matches, dst_matches,
              src_ref_points, dst_ref_points_corrected,
              dst_orig_points, dst_ref_points,
              circle_radius=2, 
              plot_width=1200, plot_height=800, create_components=False):
    '''
    Pair Point Plot
    *Params*
     - `first`, `second`: list of points with [(x, y, id), ....]
     - `plot_width`, `plot_height`: Plot-Parameters
    '''

    #
    # Point Plot
    #
    plot = figure(plot_width=plot_width, plot_height=plot_height,
                  match_aspect=True, aspect_scale=1.,
                  tools=['pan, wheel_zoom, save'], 
                  toolbar_location='right',
                  active_scroll='wheel_zoom')
    plot.toolbar.logo = None

    plot.min_border_left = plot.min_border_right = plot.min_border_top = plot.min_border_bottom = 12
    
    hover = HoverTool(tooltips='@x, @y, @id', point_policy='snap_to_data')
    plot.add_tools(hover)
    
    MATCH_ALPHA = 0.7
    ALPHA = 0.3
    ALPHA_INACTIVE = 0.05
    
    # mark the special points
    #second['line_width'] =  second.type.apply(lambda v: {'wart': 1}.get(v, 3))
    #first['line_width'] =  first.type.apply(lambda v: {'wart': 1}.get(v, 3))
    
    # src warts
    data = dict(x=src[0], y=src[1], radius=[circle_radius]*src.shape[1],
                line_width=[1]*src.shape[1],
                fill_alpha=[ MATCH_ALPHA if i in src_matches else ALPHA for i in range(src.shape[1])],
                id=list(range(src.shape[1]))
                )
    source = ColumnDataSource(data=data)
    plot.circle(source=source, x='x', y='y', radius='radius', 
                line_color='blue', color='blue', line_width='line_width',
                fill_alpha='fill_alpha',
                legend='src/first')

    # dst warts
    data = dict(x=dst_corrected[0], y=dst_corrected[1], radius=[circle_radius]*dst_corrected.shape[1],
                line_width=[1]*dst_corrected.shape[1],
                fill_alpha=[ MATCH_ALPHA if i in dst_matches else ALPHA for i,_ in enumerate(dst_corrected[1])],
                id=list(range(dst_corrected.shape[1]))
                )
    source = ColumnDataSource(data=data)
    plot.circle(source=source, x='x', y='y', radius='radius', 
                line_color='red', color='red', line_width='line_width',
                fill_alpha='fill_alpha',
                legend='dst/second')

    # ref points
    plot.circle_cross(x=src_ref_points[0], y=src_ref_points[1], size=16,
                  line_color='red', color='red', line_width=1,
                  fill_alpha=0.2)
    plot.circle_cross(x=dst_ref_points_corrected[0], y=dst_ref_points_corrected[1], size=16,
                  line_color='blue', color='blue', line_width=1,
                  fill_alpha=0.2)

    # dst orig points
    source = ColumnDataSource(data=dict(x=dst_orig_points[0], 
                                        y=dst_orig_points[1], 
                                        id=list(range(dst_orig_points.shape[1])),
                                        radius=[circle_radius]*dst_orig_points.shape[1],
                                        ))    
    plot.circle(source=source, x='x', y='y', size=16,
                line_color='red', color='lightgray', line_width=1, radius='radius',
                fill_alpha=ALPHA, line_alpha=ALPHA,
                legend='dst/second/orig')
    plot.circle_cross(x=dst_ref_points[0], y=dst_ref_points[1], size=16,
                      line_color='red', color='lightgray', line_width=1,
                      fill_alpha=0.2)
    
    
    # 
    
    #if ref_ids.size:
    #    plot.patch(x=first[ref_ids.T[0]].x, y=first[ref_ids.T[0]].y, fill_color=None, line_color='blue')
    #    plot.patch(x=second[ref_ids.T[1]].x, y=second[ref_ids.T[1]].y, fill_color=None, line_color='red')

    if create_components:
        return components(plot)
    
    return plot



def image_hist_data_plot(data):
    
    #
    # Histogram
    #
    plot = figure(title="Result Histogram", tools="save")
    plot.toolbar.logo = None

    hist, edges = numpy.histogram(data, density=True, bins=20)
    plot.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], line_color='black')

    #
    # Plot
    #
    plot2 = figure(title='Result Data')
    plot.toolbar.logo = None
    plot2.scatter(x=numpy.arange(data.shape[0]), y=numpy.sort(data))
        
    layout = Row(children=[plot, plot2])
    return components(layout)
