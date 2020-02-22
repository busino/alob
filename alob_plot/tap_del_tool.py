from bokeh.core.properties import Instance, List
from bokeh.models import ColumnDataSource
from bokeh.models.renderers import Renderer, GlyphRenderer
from bokeh.models.tools import Tap
from bokeh.util.compiler import TypeScript


class TapDeleteTool(Tap):

    __implementation__ = 'tap_del_tool.ts'

    source = Instance(ColumnDataSource)

    #renderers = List(Instance(Renderer))
    renderers = List(Instance(GlyphRenderer))
