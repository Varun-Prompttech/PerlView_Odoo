import { ConfirmationPage } from "@pos_self_order/app/pages/confirmation_page/confirmation_page";
import { patch } from "@web/core/utils/patch";
import { onMounted, useState } from "@odoo/owl";

const LOCAL_PRINT_AGENT_URL = "http://localhost:9632";

patch(ConfirmationPage.prototype, {
    setup() {
        super.setup(...arguments);
        this.state = useState({
            printError: false,
            errorMessage: "",
        });

        // Auto-print when confirmation page loads (kiosk mode only)
        onMounted(() => {
            if (this.selfOrder.config.self_ordering_mode === "kiosk" && this.props.screenMode === "pay") {
                setTimeout(() => this.autoPrintThermalInvoice(), 1500);
            }
        });
    },

    /**
     * Auto-print flow:
     * 1. Fetch raw ESC/POS bytes from the Odoo server
     * 2. POST them to the local print agent (localhost:9632/print)
     * 3. The local agent sends them to the thermal printer via `lp`
     *
     * If the local agent is not running, falls back to server-side `lp` (works on localhost only).
     */
    async autoPrintThermalInvoice() {
        const token = this.props.orderAccessToken;
        if (!token) {
            console.warn("Auto-print: No order access token available");
            return;
        }

        try {
            console.log("Auto-print: Fetching raw ESC/POS data from server...");

            // 1. Fetch raw ESC/POS bytes from Odoo server
            const rawResponse = await fetch(`/pos_payment_oma/receipt_raw/${token}`);
            if (!rawResponse.ok) {
                throw new Error(`Failed to fetch receipt data: ${rawResponse.status}`);
            }
            const rawData = await rawResponse.arrayBuffer();
            console.log(`Auto-print: Got ${rawData.byteLength} bytes of ESC/POS data`);

            // 2. Try sending to local print agent
            try {
                console.log("Auto-print: Sending to local print agent...");
                const printResponse = await fetch(`${LOCAL_PRINT_AGENT_URL}/print`, {
                    method: "POST",
                    headers: { "Content-Type": "application/octet-stream" },
                    body: rawData,
                });

                const result = await printResponse.json();
                if (result.success) {
                    console.log("Auto-print: Success via local print agent -", result.message);
                    this.state.printError = false;
                    return;
                } else {
                    console.warn("Auto-print: Local agent print failed -", result.error);
                    this.state.printError = true;
                    this.state.errorMessage = result.error;
                }
            } catch (agentError) {
                console.warn("Auto-print: Local print agent not available, trying server-side...", agentError.message);

                // 3. Fallback: try server-side lp (only works if printer is on the server)
                try {
                    const { rpc } = await import("@web/core/network/rpc");
                    const serverResult = await rpc(`/pos_payment_oma/print_invoice/${token}`, {});
                    if (serverResult.success) {
                        console.log("Auto-print: Success via server-side lp -", serverResult.message);
                        this.state.printError = false;
                        return;
                    } else {
                        this.state.printError = true;
                        this.state.errorMessage = "Printing failed. Please start the local print agent.";
                    }
                } catch (serverError) {
                    console.warn("Auto-print: Server-side print also failed", serverError);
                    this.state.printError = true;
                    this.state.errorMessage = "Printing failed. Please start the local print agent (python3 print_agent.py).";
                }
            }
        } catch (e) {
            console.error("Auto-print: Error", e);
            this.state.printError = true;
            this.state.errorMessage = `Print error: ${e.message}`;
        }
    },

    /**
     * Manual retry - try printing again.
     */
    printInvoiceBrowser() {
        this.state.printError = false;
        this.state.errorMessage = "";
        this.autoPrintThermalInvoice();
    },

    /**
     * Override native printOrderAfterTime to prevent double printing.
     */
    async printOrderAfterTime() {
        return;
    },
});
