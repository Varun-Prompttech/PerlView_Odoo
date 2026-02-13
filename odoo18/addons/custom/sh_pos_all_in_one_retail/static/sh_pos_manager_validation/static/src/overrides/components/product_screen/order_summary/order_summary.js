// /** @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { OrderSummary } from "@point_of_sale/app/screens/product_screen/order_summary/order_summary";
import { patch } from "@web/core/utils/patch";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { ShValidationTypePopup } from "@sh_pos_all_in_one_retail/static/sh_pos_manager_validation/app/popups/validation_type_popup/validation_type_popup";

patch(OrderSummary.prototype, {
   
    async _setValue(val) {
        if (this.pos.config.sh_pos_manager_validation) {
            if(!this.currentOrder.OTP){
                const selectedLine = this.currentOrder.get_selected_orderline();
                if(selectedLine){
                    let default_qty =  selectedLine.get_quantity()
                    console.log("default_qty",default_qty);
                    if(this.pos.numpadMode == "quantity" && this.pos.config.sh_qty_pw){
                        if(default_qty < val || val == null){
                        super._setValue(val)
                        }else{
                            await makeAwaitable(this.dialog, ShValidationTypePopup, {
                                title: "Select validation method",
                            });                            
                            if (this.pos.submitted_validation) {
                                super._setValue(val)
                                this.pos.submitted_validation = false;
                                if (this.pos.config.sh_one_time_password) {
                                  this.currentOrder.OTP = true;
                                }
                            }
                        }
                    }
                    else{
                        super._setValue(val)
                    }
                }
                else{
                    super._setValue(val)
                }
            }else{
                super._setValue(val)
            }

        }else{
            super._setValue(val)
        }
    },

});
