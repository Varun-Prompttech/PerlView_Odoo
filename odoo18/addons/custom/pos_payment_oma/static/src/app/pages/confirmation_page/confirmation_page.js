import { ConfirmationPage } from "@pos_self_order/app/pages/confirmation_page/confirmation_page";
import { patch } from "@web/core/utils/patch";
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
     * Automatically print the receipt via a hidden iframe.
     * Loads the HTML receipt endpoint which triggers window.print() on load,
     * allowing the browser to print to the locally attached default printer.
     */
    async autoPrintThermalInvoice() {
        const token = this.props.orderAccessToken;
        if (!token) {
            console.warn("Auto-print: No order access token available");
            return;
        }

        try {
            console.log("Auto-print: Loading receipt in hidden iframe for local printing...");
            const receiptUrl = `/pos_payment_oma/receipt_html/${token}`;

            // Remove any existing print iframe
            const existingIframe = document.getElementById('receipt-print-iframe');
            if (existingIframe) {
                existingIframe.remove();
            }

            // Create hidden iframe
            const iframe = document.createElement('iframe');
            iframe.id = 'receipt-print-iframe';
            iframe.style.position = 'fixed';
            iframe.style.top = '-10000px';
            iframe.style.left = '-10000px';
            iframe.style.width = '80mm';
            iframe.style.height = '0';
            iframe.style.border = 'none';
            iframe.style.visibility = 'hidden';

            // The receipt_html endpoint has onload="window.print()" which will
            // trigger the browser print dialog automatically when the iframe loads.
            // This prints to the user's local default printer.
            iframe.src = receiptUrl;

            iframe.onload = () => {
                console.log("Auto-print: Receipt iframe loaded, print dialog should appear.");
                this.state.printError = false;
            };

            iframe.onerror = () => {
                console.warn("Auto-print: Failed to load receipt iframe");
                this.state.printError = true;
                this.state.errorMessage = "Failed to load receipt for printing.";
            };

            document.body.appendChild(iframe);

        } catch (e) {
            console.error("Auto-print: Error setting up print iframe", e);
            this.state.printError = true;
            this.state.errorMessage = "Error while printing receipt.";
        }
    },

    /**
     * Manual fallback - open receipt in a new window for the user to print.
     */
    printInvoiceBrowser() {
        const token = this.props.orderAccessToken;
        if (token) {
            window.open(`/pos_payment_oma/receipt_html/${token}`, '_blank');
        }
    },

    /**
     * Override native printOrderAfterTime to prevent double printing.
     * The native method prints a POS receipt; we replace it with our auto-print.
     */
    async printOrderAfterTime() {
        // No-op: printing handled by autoPrintThermalInvoice()
        return;
    },
});
