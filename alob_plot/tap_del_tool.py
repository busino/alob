from bokeh.core.properties import Instance, List
from bokeh.models import ColumnDataSource
from bokeh.models.renderers import Renderer
from bokeh.models.tools import Tap

JS_CODE = """
import * as p from "core/properties"
import {TapTool, TapToolView} from "models/tools/gestures/tap_tool"
import {SelectTool, SelectToolView} from "models/tools/gestures/select_tool"


export class TapDeleteToolView extends TapToolView

  _keyup: (e) ->
    if e.keyCode == 27
      for r in @computed_renderers
        ds = r.data_source
        sm = ds.selection_manager
        sm.clear()
    else if e.keyCode == 46
      if @model.source.selected['1d'].indices.length
        source = @model.source
        data = source.data
        index = source.selected['1d'].indices[0]
        if (['tail', 'nose', 'right_eye', 'left_eye'].indexOf(data.type[index]) >= 0)
            return;
        data.x.splice(index, 1)
        data.y.splice(index, 1)
        data.id.splice(index, 1)
        data.type.splice(index, 1)
        data.color.splice(index, 1)
        for r in @computed_renderers
          r.data_source.selection_manager.clear()
        source.change.emit()

export class TapDeleteTool extends TapTool
  
  default_view: TapDeleteToolView
  tool_name: "TapDeleteTool"
  event_type: "tap"
  icon: "bk-tool-icon-lasso-select"

  @define {
    source: [ p.Instance ]
  }
"""


class TapDeleteTool(Tap):

    __implementation__ = JS_CODE

    source = Instance(ColumnDataSource)

    renderers = List(Instance(Renderer))


