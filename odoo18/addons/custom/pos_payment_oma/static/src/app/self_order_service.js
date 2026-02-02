/** @odoo-module **/

import { SelfOrder } from "@pos_self_order/app/self_order_service";
import { patch } from "@web/core/utils/patch";

patch(SelfOrder.prototype, {
    filterPaymentMethods(pms) {
        // Include OMA alongside adyen and stripe for Kiosk mode
        return this.config.self_ordering_mode === "kiosk"
            ? pms.filter((rec) => ["adyen", "stripe", "oma"].includes(rec.use_payment_terminal))
            : [];
    },
});
