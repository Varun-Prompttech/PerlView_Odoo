/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    updateSelectedPaymentline(amount = false)  {
        if(this.pos.config.sh_pos_manager_validation && this.pos.config.sh_validation_on_payment_method && this.pos.config.sh_select_method_ids){
            if(this.pos.get_order().number_buffer_reset){
                return false
            }
        }
        super.updateSelectedPaymentline(amount = false)                 
    }
});
