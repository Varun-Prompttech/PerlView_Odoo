/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { GlobalDiscountPopupWidget } from "@sh_pos_all_in_one_retail/static/sh_pos_order_discount/apps/popups/GlobalDiscountPopupWidget/GlobalDiscountPopupWidget";
import { useService } from "@web/core/utils/hooks";

console.log("Custom POS DiscountLimitPatch loaded!");

patch(GlobalDiscountPopupWidget.prototype, {
    setup() {
        super.setup();
        this.notification = useService("notification");
    },

    async confirm() {
        const maxAllowedPercent = this.pos.user?.max_discount_percentage || 0;
        const enteredValue = parseFloat($(".sh_discount_value").val()) || 0;
        const isPercentage = document.getElementById("discount_percentage_radio")?.checked;
        const isFixed = document.getElementById("discount_fixed_radio")?.checked;

        // Validate Percentage Discount
        if (isPercentage && enteredValue > maxAllowedPercent) {
            $(".sh_discount_value").addClass("invalid_number");
            this.notification.add(_t(`Discount limit exceeded`));
            return;
        }

        // Validate Fixed Discount
        if (isFixed) {
            const order = this.pos.get_order();
            if (order) {
                const orderTotal = order.get_total_with_tax();
                if (orderTotal > 0) {
                    const discountPercentEquivalent = (enteredValue / orderTotal) * 100;
                    if (discountPercentEquivalent > maxAllowedPercent) {
                        $(".sh_discount_value").addClass("invalid_number");
                        this.notification.add(_t(`Discount limit exceeded`));
                        return;
                    }
                }
            }
        }

        // Proceed with original logic if validations pass
        await super.confirm?.();
    },
});
