import * as p from "core/properties";
import { TapTool, TapToolView } from "models/tools/gestures/tap_tool";
//import { SelectTool, SelectToolView} from "models/tools/gestures/select_tool";
import { ColumnDataSource} from "models/sources/column_data_source"
import { bk_tool_icon_lasso_select } from "styles/icons"
import { KeyEvent}  from "core/ui_events";
import {Keys} from "core/dom";
import * as arrayable from "core/util/arrayable"
//import {GlyphRenderer} from "models/renderers/glyph_renderer";


export class TapDeleteToolView extends TapToolView {

    model: TapDeleteTool;

    _keyup(ev: KeyEvent) {
        if (ev.keyCode == Keys.Esc) { // ESC --> stop edit
            this.model.source.selection_manager.clear();
        } else if (ev.keyCode == Keys.Delete) { // DELETE --> remove point
            const source = this.model.source;
            if ( source && source.selected['1d'].indices.length ) {
                const data = source.data;
                const index = source.selected['1d'].indices[0];
                if (['tail', 'nose', 'right_eye', 'left_eye'].indexOf(data.type[index]) >= 0) {
                    return;
                }
                data.x = arrayable.splice(data.x, index, 1);
                data.y = arrayable.splice(data.y, index, 1);
                data.id = arrayable.splice(data.id, index, 1);
                data.type = arrayable.splice(data.type, index, 1);
                data.color = arrayable.splice(data.color, index, 1);
                source.change.emit()
                source.selection_manager.clear();
            }
        }
    }

}

export namespace TapDeleteTool {
    
    export type Attrs = p.AttrsOf<Props>;
  
    export type Props = TapTool.Props & {
      source: p.Property<ColumnDataSource>
    };
}
  
export interface TapDeleteTool extends TapDeleteTool.Attrs {}


export class TapDeleteTool extends TapTool {

    properties: TapDeleteTool.Props;
    tool_name = "TapDeleteTool";
    event_type = "tap" as "tap";
    icon = bk_tool_icon_lasso_select;

    constructor(attrs?: Partial<TapDeleteTool.Attrs>) {
        super(attrs)
    }

    static __name__ = "TapDeleteTool";

    static init_TapDeleteTool(): void {
        
        this.prototype.default_view = TapDeleteToolView;
    
        this.define<TapDeleteTool.Props>({
            source:     [ p.Instance         ],
        })
    }

}
