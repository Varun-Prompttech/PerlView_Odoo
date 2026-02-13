/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { _t } from "@web/core/l10n/translation";

patch(ControlButtons.prototype, {
    async onClickUOM() {
        var selectionList = [];
        var line = this.pos.get_order().get_selected_orderline();
        if (line && line.product_id) {
            var uom = line.product_id.uom_id
            if (uom) {
                selectionList.push({ id: uom.id, isSelected: true, label: uom.name, item: uom });
                var secondary_uom = line.product_id.sh_secondary_uom ? line.product_id.sh_secondary_uom : false;
                if (secondary_uom && secondary_uom != uom) {
                    selectionList.push({ id: secondary_uom.id, isSelected: false, label: secondary_uom.name, item: secondary_uom });
                }
            }
        }
        for(let each_uom of selectionList){
            if (each_uom.label === line.get_current_uom().name) {
                each_uom.isSelected = true;
            } else {
                each_uom.isSelected = false;
            }
        };
        const selectedUOM = await makeAwaitable(this.dialog, SelectionPopup, {
            title: _t("Select the UOM"),
            list: selectionList,
        });
        
        if (selectedUOM) {
            let converted_qty = line.convert_qty_uom(line.qty ,selectedUOM , line.get_current_uom())
            line.set_secondary_quantity(converted_qty);

            if(line.get_unit() == selectedUOM){
                let primary_converted_qty = line.convert_qty_uom(line.qty ,line.get_current_uom(), selectedUOM  )
                line.set_primary_quantity(converted_qty)
            }else{
                let primary_converted_qty = line.convert_qty_uom(line.qty ,line.get_current_uom(), selectedUOM  )
                line.set_primary_quantity(primary_converted_qty)
            }            
            // line.set_quantity(converted_qty);
            
            line.change_current_uom(selectedUOM);
           
        }
    }
});
