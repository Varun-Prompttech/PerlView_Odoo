/** @odoo-module **/

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    async validateOrder(isForceValidate) {
        await super.validateOrder(isForceValidate);

        // Give Odoo a moment to finish syncing
        setTimeout(() => {
            // Hard reload (clears JS memory state)
            window.location.reload(true);
        }, 500);
    },
});
