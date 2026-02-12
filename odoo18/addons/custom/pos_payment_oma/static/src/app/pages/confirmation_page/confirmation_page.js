import { ConfirmationPage } from "@pos_self_order/app/pages/confirmation_page/confirmation_page";
import { patch } from "@web/core/utils/patch";
import { onMounted, useState } from "@odoo/owl";

/**
 * Patch ConfirmationPage to auto-print the receipt using the same format
 * as the raw ESC/POS receipt (monospace, 80mm thermal paper layout).
 *
 * This version uses the browser's native window.print() via a hidden iframe.
 * To make this "direct" (skip the print dialog), start Chrome with:
 * --kiosk-printing
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
                setTimeout(() => this.autoPrintReceipt(), 1500);
            }
        });
    },

    /**
     * Print the receipt using a hidden iframe that loads the HTML receipt
     * (bold monospace layout) and triggers window.print().
     * Works perfectly with Chrome's --kiosk-printing flag.
     */
    async autoPrintReceipt() {
        const token = this.props.orderAccessToken;
        if (!token) return;

        try {
            console.log("Auto-Print: Loading receipt...");
            const receiptUrl = `/pos_payment_oma/receipt_html/${token}`;

            // Remove existing iframe
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

            // triggers window.print() via onload in the endpoint
            iframe.src = receiptUrl;
            document.body.appendChild(iframe);

            this.state.printError = false;
        } catch (e) {
            console.error("Auto-Print: Error", e);
            this.state.printError = true;
            this.state.errorMessage = "Automatic printing failed.";
        }
    },

    /**
     * Manual retry
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
