import { ConfirmationPage } from "@pos_self_order/app/pages/confirmation_page/confirmation_page";
import { patch } from "@web/core/utils/patch";
import { onMounted, useState } from "@odoo/owl";

/**
 * Patch ConfirmationPage to auto-print the receipt using the same format
 * as the raw ESC/POS receipt (monospace, 80mm thermal paper layout).
 *
 * Loads the receipt from /pos_payment_oma/receipt_html/<token> in a hidden
 * iframe. That page has onload="window.print()" which triggers the browser
 * print dialog, printing to the local default printer.
 *
 * Works for both local and remote server access.
 */
patch(ConfirmationPage.prototype, {
    setup() {
        super.setup(...arguments);
        this.state = useState({
            ...this.state,
            printError: false,
            errorMessage: "",
        });

        onMounted(() => {
            if (this.selfOrder.config.self_ordering_mode === "kiosk" && this.props.screenMode === "pay") {
                setTimeout(() => this.autoPrintReceipt(), 2000);
            }
        });
    },

    /**
     * Print the receipt using a hidden iframe that loads the HTML receipt
     * (same layout as raw ESC/POS) and triggers window.print().
     */
    async autoPrintReceipt() {
        const token = this.props.orderAccessToken;
        if (!token) {
            console.warn("Auto-print: No order access token available");
            return;
        }

        try {
            console.log("Auto-print: Loading receipt for printing...");
            const receiptUrl = `/pos_payment_oma/receipt_html/${token}`;

            // Remove any existing print iframe
            const existing = document.getElementById('receipt-print-iframe');
            if (existing) existing.remove();

            // Create hidden iframe
            const iframe = document.createElement('iframe');
            iframe.id = 'receipt-print-iframe';
            iframe.style.position = 'fixed';
            iframe.style.top = '-10000px';
            iframe.style.left = '-10000px';
            iframe.style.width = '80mm';
            iframe.style.height = '1px';
            iframe.style.border = 'none';
            iframe.style.visibility = 'hidden';

            // The receipt_html page has onload="window.print()" built in,
            // which auto-triggers the browser print dialog.
            iframe.src = receiptUrl;

            iframe.onload = () => {
                console.log("Auto-print: Receipt loaded, print dialog should appear.");
                this.state.printError = false;
            };

            iframe.onerror = () => {
                console.warn("Auto-print: Failed to load receipt");
                this.state.printError = true;
                this.state.errorMessage = "Failed to load receipt.";
            };

            document.body.appendChild(iframe);

        } catch (e) {
            console.error("Auto-print: Error", e);
            this.state.printError = true;
            this.state.errorMessage = `Print error: ${e.message}`;
        }
    },

    /**
     * Manual retry button handler.
     */
    printInvoiceBrowser() {
        const token = this.props.orderAccessToken;
        if (token) {
            window.open(`/pos_payment_oma/receipt_html/${token}`, '_blank');
        }
    },

    /**
     * Override native printOrderAfterTime to prevent double printing.
     */
    async printOrderAfterTime() {
        return;
    },
});
