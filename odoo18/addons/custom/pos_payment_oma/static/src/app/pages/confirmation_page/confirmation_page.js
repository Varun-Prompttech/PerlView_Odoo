import { ConfirmationPage } from "@pos_self_order/app/pages/confirmation_page/confirmation_page";
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";
import { onMounted } from "@odoo/owl";

patch(ConfirmationPage.prototype, {
    setup() {
        super.setup(...arguments);

        // Auto-print thermal invoice when confirmation page loads (kiosk mode only)
        onMounted(() => {
            if (this.selfOrder.config.self_ordering_mode === "kiosk" && this.props.screenMode === "pay") {
                // Small delay to ensure order/invoice data is fully committed on the server
                setTimeout(() => this.autoPrintThermalInvoice(), 1500);
            }
        });
    },

    /**
     * Automatically print the invoice to the connected thermal receipt printer
     * by calling the server-side print endpoint which uses `lp` to send raw ESC/POS data.
     */
    async autoPrintThermalInvoice() {
        const token = this.props.orderAccessToken;
        if (!token) {
            console.warn("Auto-print: No order access token available");
            return;
        }

        try {
            console.log("Auto-print: Sending invoice to thermal printer...");
            const result = await rpc(`/pos_payment_oma/print_invoice/${token}`, {});

            if (result.success) {
                console.log("Auto-print: Invoice printed successfully -", result.message);
            } else {
                console.error("Auto-print: Print failed -", result.error);
            }
        } catch (e) {
            console.error("Auto-print: Error calling print endpoint", e);
        }
    },

    /**
     * Override native printOrderAfterTime to prevent double printing.
     * The native method prints a POS receipt; we replace it with our thermal invoice auto-print.
     */
    async printOrderAfterTime() {
        // No-op: printing handled by autoPrintThermalInvoice()
        return;
    },
});
