/** @odoo-module **/

import { OrderWidget } from "@pos_self_order/app/components/order_widget/order_widget";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(OrderWidget.prototype, {
    get hasOmaTerminal() {
        const paymentMethods = this.selfOrder.models["pos.payment.method"].getAll();
        return paymentMethods.some((pm) => pm.use_payment_terminal === "oma");
    },

    get omaPaymentMethod() {
        const paymentMethods = this.selfOrder.models["pos.payment.method"].getAll();
        return paymentMethods.find((pm) => pm.use_payment_terminal === "oma");
    },

    get buttonToShow() {
        const currentPage = this.router.activeSlot;
        const payAfter = this.selfOrder.config.self_ordering_pay_after;
        const kioskPayment = this.selfOrder.models["pos.payment.method"].getAll();
        const isNoLine = this.selfOrder.currentOrder.lines.length === 0;
        const hasNotAllLinesSent = this.selfOrder.currentOrder.unsentLines;
        const isMobilePayment = kioskPayment.find((p) => p.is_mobile_payment);

        let label = "";
        let disabled = false;

        if (currentPage === "product_list") {
            label = _t("Order");
            disabled = isNoLine || hasNotAllLinesSent.length == 0;
        } else if (
            payAfter === "meal" &&
            Object.keys(this.selfOrder.currentOrder.changes).length > 0
        ) {
            label = _t("Order");
            disabled = isNoLine;
        } else {
            // Check if OMA terminal is configured
            if (this.hasOmaTerminal) {
                label = _t("Pay by Card");
            } else {
                label = kioskPayment ? _t("Pay") : _t("Order");
            }
            disabled = !kioskPayment && !isMobilePayment;
        }

        return { label, disabled };
    },
});
