import { ConfirmationPage } from "@pos_self_order/app/pages/confirmation_page/confirmation_page";
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";
import { onMounted, useState } from "@odoo/owl";

patch(ConfirmationPage.prototype, {
    setup() {
        super.setup(...arguments);
        this.state = useState({
            printError: false,
            errorMessage: "",
        });

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
                this.state.printError = false;
            } else {
                console.warn("Auto-print: Direct thermal print failed -", result.error);
                this.state.printError = true;
                this.state.errorMessage = result.error;

                // AUTOMATIC FALLBACK: If direct print failed, open browser print window immediately
                console.log("Auto-print: Triggering automatic browser fallback...");
                this.printInvoiceBrowser();
            }
        } catch (e) {
            console.error("Auto-print: Error calling print endpoint", e);
            this.state.printError = true;
            this.state.errorMessage = "Connection error while printing.";
            // Try fallback even on network error
            this.printInvoiceBrowser();
        }
    },

    /**
     * Manual fallback to print the invoice via the browser.
     * Opens the invoice PDF in a new window for the user to print manually.
     */
    printInvoiceBrowser() {
        const token = this.props.orderAccessToken;
        if (token) {
            window.open(`/pos_payment_oma/download_invoice/${token}`, '_blank');
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
