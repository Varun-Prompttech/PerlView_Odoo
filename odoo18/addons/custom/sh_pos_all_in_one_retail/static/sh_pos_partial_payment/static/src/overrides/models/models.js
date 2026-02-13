/** @odoo-module */

import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    is_paid() {
        if (this.config.enable_partial_payment && this.to_invoice && this?.get_partner()?.not_allow_partial_payment===false) {
            return true;
        } else {
            return super.is_paid(...arguments);
        }
    },
    get_change() {
        let { order_sign, order_remaining: remaining } = this.taxTotals;
        
        if(this.config.enable_partial_payment && remaining > 0){
            return 0
        }else{
            return super.get_change();
        }
    }
});
