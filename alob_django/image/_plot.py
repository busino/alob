'''
Alob Project
2016
Author(s): R.Walker

'''
import logging

import numpy

from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, ColumnDataSource, Range1d


log = logging.getLogger('alob')


def result_plot(results, plot_width=800, plot_height=600, create_components=False):

    plot = figure(plot_width=plot_width, plot_height=plot_height,
                  x_range=Range1d(0, len(results.result)), y_range=Range1d(0, max(results.result)*1.1),
                  tools=['pan, box_zoom, reset, wheel_zoom, save'], toolbar_options=dict(logo=None, toolbar_location='right'))

    plot.min_border_left = plot.min_border_right = plot.min_border_top = plot.min_border_bottom = 12
    
    hover = HoverTool(tooltips='@result', point_policy='snap_to_data')
    plot.add_tools(hover)
    
    TEXT_OFFSET = 2
    data = dict(x=range(len(results.result)), y=results.result)
    source = ColumnDataSource(data=data)
    plot.circle(source=source, x='x', y='y', size=12)
    
    if create_components:
        return components(plot)
    
    return plot

def image_plot(points, plot_width=800, plot_height=600, create_components=False):
    '''
    Image Point Plot
    *Params*
     - `points`: list of points with [(x, y, name, id), ....]
     - `plot_width`, `plot_height`: Plot-Parameters
    '''

    #
    # Point Plot
    #
    plot = figure(plot_width=plot_width, plot_height=plot_height,
                  x_range=Range1d(0, 120), y_range=Range1d(-60, 60),
                  tools=['pan, box_zoom, reset, wheel_zoom, save'], toolbar_options=dict(logo=None, toolbar_location='right'))

    plot.min_border_left = plot.min_border_right = plot.min_border_top = plot.min_border_bottom = 12
    
    # Hover Position of the Recorder
    hover = HoverTool(tooltips='@x, @y, @name', point_policy='snap_to_data')
    plot.add_tools(hover)
    
    TEXT_OFFSET = 2
    data = dict(x=points.x, y=points.y, name=points.id)
    source = ColumnDataSource(data=data)
    plot.circle(source=source, x='x', y='y', size=20)
    
    if create_components:
        return components(plot)
    
    return plot


