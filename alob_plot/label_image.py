import numpy

from bokeh.plotting import figure
from bokeh.models.tools import TapTool, HoverTool, WheelZoomTool, PanTool, CrosshairTool
from bokeh import events
from bokeh.models.callbacks import CustomJS
from bokeh.models.markers import Cross, Square, SquareCross, CircleCross, Circle
from bokeh.models import ColumnDataSource, CDSView, BooleanFilter
from bokeh.models.widgets import Div
from bokeh.layouts import widgetbox, row, column
from bokeh.models.widgets.buttons import Button
from bokeh.embed import components

from alob_plot.tap_del_tool import TapDeleteTool
from bokeh.models.widgets.tables import DataTable, TableColumn, StringFormatter
from bokeh.models.glyphs import Line
from bokeh.models.filters import CustomJSFilter

from .colors import WART_COLOR


def image_label_plot(img, points, update_url, main_url, offset=[0,0], get_components=True):
    
    aimg = numpy.array(img)
    ydim, xdim, n = aimg.shape
    img = aimg.view(dtype=numpy.uint32).reshape(aimg.shape[:-1])
    img = img[::-1]
    
    #
    # Display the 32-bit RGBA image
    #
    plot = figure(plot_width=800, plot_height=600,
                  #x_range=[0,xdim], y_range=[0,ydim],
                  match_aspect=True, aspect_scale=1.,
                  tools='', logo=None,
                  title=None)
    # TODO: 
    # No ticks
    # tight range
    
    plot.image_rgba(image=[img], x=offset[0], y=offset[1], dw=xdim, dh=ydim)
    
    #
    # Data Source holding the Point Coordinates
    #
    source = ColumnDataSource(data=dict(x=points.x.tolist(),
                                        y=points.y.tolist(),
                                        id=points.index.tolist(),
                                        type=points.type.tolist(),
                                        color=points.color.tolist()))
    selection_source = ColumnDataSource(data=dict(id=[]))
    code = '''
    var indices = [];
    for (var i = 0; i <= source.data['type'].length; i++)
        if (['left_eye', 'right_eye'].indexOf(source.data['type'][i]) >= 0)
            indices.push(i)
    return indices;    
    '''
    eye_line_view = CDSView(source=source, filters=[CustomJSFilter(code=code)])
    code = '''
    var indices = [];
    for (var i = 0; i <= source.data['type'].length; i++)
        if (['tail', 'nose'].indexOf(source.data['type'][i]) >= 0)
            indices.push(i)
    return indices;    
    '''
    h_line_view = CDSView(source=source, filters=[CustomJSFilter(code=code)])

    #
    # DataTable
    #
    # TODO remove me: for testing only
    columns = [
        TableColumn(field="id", title="ID"),
        TableColumn(field="x", title="x"),
        TableColumn(field="y", title="y"),
        TableColumn(field="type", title="type"),
    ]
    #[setattr(v, 'formatter', StringFormatter(text_align='right')) for v in columns]
    data_table = DataTable(source=source, columns=columns, width=240, height=600)
    
    #
    # Double Click for Point Creation
    #
    dtap_cb = CustomJS(args=dict(source=source, dt=data_table),
                        code="""
    console.log('DoubleTap');
    var data = source.data;
    console.log(data);
    console.log(data['x']);
    data['x'].push(Math.round(cb_obj.x));
    data['y'].push(Math.round(cb_obj.y));
    data['id'].push(null);
    data['type'].push('wart');
    data['color'].push(%r);
    source.change.emit();
    dt.change.emit();
    """%WART_COLOR)
    plot.js_on_event(events.DoubleTap, dtap_cb)
    
    #
    # Show the position of the Point when moving selected point
    #
    move_cb = CustomJS(args=dict(source=source, selection_source=selection_source, dt=data_table),
                        code="""
    if (selection_source.data['id'].length & source.selected['1d'].indices.length) {
      console.log('Mouse Move');
      var index = source.selected['1d'].indices[0];
      var data = source.data;
      data['x'][index] = Math.round(cb_obj.x);
      data['y'][index] = Math.round(cb_obj.y);
      source.change.emit();
      dt.change.emit();
    }
    """)
    plot.js_on_event(events.MouseMove, move_cb)
    
    #
    # Select and Release Point on click
    # is a little bit hacky
    #
    sg_cb = CustomJS(args=dict(source=source, selection_source=selection_source, dt=data_table),
                        code="""
    console.log('SelectionGeometry');

    if (source.selected['1d'].indices.length) {
        // when releasing the selection the mousemove is stopped and the points stays on current position
        if (selection_source.data['id'].length) {
            console.log('Clear selection');
            selection_source.data['id'].length = 0;
            source.selection_manager.clear();
            source.change.emit();
            dt.change.emit();
        }
        // select the point
        else {
            console.log('Add new selection');
            selection_source.data['id'].length=0;
            selection_source.data['id'].push(source.selected['1d'].indices[0]);
            selection_source.change.emit();
        }
    }
    """)
    plot.js_on_event(events.SelectionGeometry, sg_cb)
    
    #
    # Glyph
    #
    GLYPH_CLASS = CircleCross#Square# Circle, Cross
    FILL_ALPHA = 0.0
    LINE_WIDTH = 1.2
    glyph = GLYPH_CLASS(size=24, x='x', y='y',
                        line_width=LINE_WIDTH, line_color='color',
                        fill_alpha=FILL_ALPHA)
    cr = plot.add_glyph(source, glyph)

    #
    # Define Selection and Hover of Glyph
    #
    cr.selection_glyph = GLYPH_CLASS(line_color='firebrick', line_width=LINE_WIDTH,
                                     fill_alpha=FILL_ALPHA)
    cr.nonselection_glyph = GLYPH_CLASS(line_width=LINE_WIDTH, line_color='color',
                                        fill_alpha=FILL_ALPHA)
    cr.hover_glyph = GLYPH_CLASS(line_color='orange', line_width=LINE_WIDTH,
                                 fill_alpha=FILL_ALPHA)

    glyph = Line(x='x', y='y', line_width=1.6, line_color='fuchsia')
    eye_l_r = plot.add_glyph(source, glyph, view=eye_line_view)
    glyph = Line(x='x', y='y', line_width=1.6, line_color='blue')
    h_l_r = plot.add_glyph(source_or_glyph=source, glyph=glyph, view=h_line_view)
    #h_l_r.selection_glyph = Line(line_width=1.6, line_color='blue', line_alpha=1.)
    #h_l_r.nonselection_glyph = Line(line_width=1.6, line_color='blue', line_alpha=1.)
    #h_l_r.hover_glyph = Line(line_width=1.6, line_color='blue', line_alpha=1.)
    #h_l_r.muted_glyph = Line(line_width=1.6, line_color='blue', line_alpha=1.)
    #
    # Plot Tools
    #
  
    # Create A New TapDeleteTool
    plot.add_tools(TapDeleteTool(renderers=[cr], source=source))
    #plot.add_tools(TapTool(behavior='select', renderers=[cr]))
    # Hover to inform the user that the glyph can be selected
    plot.add_tools(HoverTool(tooltips=None, renderers=[cr]))
    # Scroll
    wz = WheelZoomTool()
    plot.add_tools(wz)
    plot.toolbar.active_scroll = wz
    plot.add_tools(PanTool())
    plot.toolbar_location = None
    plot.axis.visible = False
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None
    plot.background_fill_color = "white"
    plot.min_border_left = None
    plot.min_border_right = 2
    plot.min_border_top = 0
    plot.min_border_bottom = 0
    plot.border_fill_color = 'white'
    plot.outline_line_color = 'white'
    
    #
    # Doc Div
    #
    div = Div(text='''
    <div style="margin-left: 32px;">
    <table style="border-spacing: 10px; border-collapse: separate; width: 400px;">
      <tr><td><b>New Point:</b></td><td>Double-Click</td></tr>
      <tr><td><b>Edit Point:</b></td><td>Select Point > Drag > Click</td></tr>
      <tr><td><b>Delete Point:</b></td><td>Select Point > Press Delete-Key</td></tr>
    </table><br>
    Mark Eyes:<br>
    <img src="/static/images/mark_eye.png"><br>
    Tail and Nose:
    <img src="/static/images/mark_tail_nose.png">
    </div>
    ''')

    # Reset Button
    reset = Button(label='Reset', button_type='default', width=60, 
                   callback=CustomJS(code="location.reload();"))
    close = Button(label='Close', button_type='default', width=80, 
                   callback=CustomJS(code="window.location.href={0!r}".format(main_url)))
    

    # Save button message
    message_div = Div(text='')
    
    # Save Button
    btn = Button(label='Save', button_type='success', width=80, css_classes=["btn-space"])
    btn_code = '''
    console.log('Save');
    var data = source.data;
    var data_json = JSON.stringify({x: data.x, y: data.y, id: data.id, type: data.type});
    // Send to Server
    // TODO: to be implemented
    var url = '%s';
    console.log(url);
    $.post({
        url: url,
        data: data_json,
        beforeSend : function(jqXHR, settings) {
            message_div.text = '';
            jqXHR.setRequestHeader("x-csrftoken", CSRF_TOKEN);
        },
        success: function( result ) {
            console.log(result);
            //location.reload();
            message_div.text = result.message;
        },
        error: function( jqXHR, textStatus, errorThrown ){
            console.log(jqXHR);
            console.log(textStatus);
            console.log(errorThrown);
        }// error
    });    
    '''%update_url
    btn.callback = CustomJS(args=dict(source=source, message_div=message_div), code=btn_code)
    
    
    #
    # Layout
    #
    layout = column(row(plot, 
                        column(data_table, message_div, row(column(btn), column(reset), column(close), width=320)), 
                        widgetbox(div, width=320)))
    
    if not get_components:
        return layout
    return components(layout)
