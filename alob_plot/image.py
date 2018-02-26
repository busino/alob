'''
Alob Project
2016
Author(s): R.Walker

'''
import logging

from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, ColumnDataSource, Range1d
from bokeh.models.tools import PanTool, WheelZoomTool, SaveTool

log = logging.getLogger('alob')


def result_plot(results, plot_width=800, plot_height=400, create_components=False):

    plot = figure(plot_width=plot_width, plot_height=plot_height,
                  x_range=Range1d(0, len(results.result)), y_range=Range1d(0, max(results.result)*1.1),
                  tools=['pan, box_zoom, reset, wheel_zoom, save'], toolbar_location='right', logo=None)

    plot.min_border_left = plot.min_border_right = plot.min_border_top = plot.min_border_bottom = 12
    
    hover = HoverTool(tooltips='@result', point_policy='snap_to_data')
    plot.add_tools(hover)
    
    data = dict(x=range(len(results.result)), y=results.result)
    source = ColumnDataSource(data=data)
    plot.circle(source=source, x='x', y='y', size=12)
    
    if create_components:
        return components(plot)
    
    return plot

def image_plot(points, plot_width=800, plot_height=400, create_components=False):
    '''
    Image Point Plot
    *Params*
     - `points`: list of points with [(x, y, name, id), ....]
     - `plot_width`, `plot_height`: Plot-Parameters
    '''

    #
    # Point Plot
    #
    wz = WheelZoomTool()
    tools = [PanTool(), wz, SaveTool()]
    plot = figure(plot_width=plot_width, plot_height=plot_height,
                  match_aspect=True, aspect_scale=1.,
                  tools=tools, toolbar_location='right', logo=None)
    plot.toolbar.active_scroll = wz

    plot.min_border_left = plot.min_border_right = plot.min_border_top = plot.min_border_bottom = 12
    plot.background_fill_color = 'lightgray'
    
    # Hover Position of the Recorder
    hover = HoverTool(tooltips='@x, @y, @name', point_policy='snap_to_data')
    plot.add_tools(hover)
    data = dict(x=points.x, y=points.y, name=points.id, color=points.color)
    source = ColumnDataSource(data=data)
    plot.circle_cross(source=source, x='x', y='y', color='color', size=20, fill_color=None)
    
    if create_components:
        return components(plot)
    
    return plot


