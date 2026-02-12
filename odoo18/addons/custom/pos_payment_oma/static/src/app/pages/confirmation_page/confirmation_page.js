import { ConfirmationPage } from "@pos_self_order/app/pages/confirmation_page/confirmation_page";
import { patch } from "@web/core/utils/patch";
import { onMounted, useState } from "@odoo/owl";

const LOCAL_PRINT_AGENT_URL = "http://localhost:9632";

/**
 * Patch ConfirmationPage to enable TRULY direct printing without a preview dialog.
 *
 * Flow:
 * 1. Fetches raw ESC/POS bytes from the server.
 * 2. Sends them to the Local Print Agent running on the Windows PC (localhost:9632).
 * 3. The agent prints immediately to the default printer.
 *
 * This bypasses all browser print dialogs.
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
                // Wait for order data to be available
                setTimeout(() => this.directPrintToLocalAgent(), 1500);
            }
        });
    },

    /**
     * Fetch raw ESC/POS bytes and send to the local print agent for silent printing.
     */
    async directPrintToLocalAgent() {
        const token = this.props.orderAccessToken;
        if (!token) return;

        try {
            console.log("DirectPrint: Fetching raw ESC/POS data...");
            const response = await fetch(`/pos_payment_oma/receipt_raw/${token}`);
            if (!response.ok) throw new Error("Failed to fetch receipt data from server");

            const rawData = await response.arrayBuffer();
            console.log(`DirectPrint: Sending ${rawData.byteLength} bytes to local agent...`);

            const printResponse = await fetch(`${LOCAL_PRINT_AGENT_URL}/print`, {
                method: "POST",
                headers: { "Content-Type": "application/octet-stream" },
                body: rawData,
            });

            if (!printResponse.ok) {
                const errorData = await printResponse.json();
                throw new Error(errorData.error || "Local agent failed to print");
            }

            const result = await printResponse.json();
            if (result.success) {
                console.log("DirectPrint: Success!", result.message);
                this.state.printError = false;
            } else {
                throw new Error(result.error || "Unknown print error");
            }
        } catch (e) {
            console.warn("DirectPrint: Failed", e.message);
            this.state.printError = true;
            this.state.errorMessage = "Direct printing failed. Is the 'print_agent.py' running on this PC?";

            // If the user wants a fallback to browser print, we could call it here.
            // But the objective is "no browser print".
        }
    },

    /**
     * Manual retry - tries direct print again.
     */
    printInvoiceBrowser() {
        this.state.printError = false;
        this.state.errorMessage = "";
        this.directPrintToLocalAgent();
    },

    /**
     * Override native printOrderAfterTime to prevent double printing.
     */
    async printOrderAfterTime() {
        return;
    },
});
