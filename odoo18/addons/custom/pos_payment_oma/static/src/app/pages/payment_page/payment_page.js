/** @odoo-module **/

import { PaymentPage } from "@pos_self_order/app/pages/payment_page/payment_page";
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";
import { useState } from "@odoo/owl";

patch(PaymentPage.prototype, {
    setup() {
        super.setup(...arguments);
        this.omaState = useState({
            processing: false,
            message: "Waiting for card...",
            timer: 120,  // 2 minutes timeout
            error: false,
            success: false,
        });
        this.timerInterval = null;
    },

    get omaPaymentMethod() {
        return this.selfOrder.models["pos.payment.method"].find(
            (pm) => pm.use_payment_terminal === "oma"
        );
    },

    get hasOmaTerminal() {
        return Boolean(this.omaPaymentMethod);
    },

    get isOmaProcessing() {
        return this.omaState.processing;
    },

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    },

    startTimer() {
        this.omaState.timer = 120;
        this.timerInterval = setInterval(() => {
            this.omaState.timer--;
            if (this.omaState.timer <= 0) {
                this.stopTimer();
                this.omaState.error = true;
                this.omaState.message = "Payment timeout - Terminal did not respond";
                this.omaState.processing = false;
                this.selfOrder.paymentError = true;
            }
        }, 1000);
    },

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    },

    selectMethod(methodId) {
        const method = this.selfOrder.models["pos.payment.method"].find(
            (p) => p.id === methodId
        );

        // If OMA method selected, start OMA payment flow
        if (method && method.use_payment_terminal === "oma") {
            this.state.selection = false;
            this.state.paymentMethodId = methodId;
            this.startOmaPayment();
        } else {
            // Default flow for other terminals
            super.selectMethod(methodId);
        }
    },

    async startOmaPayment() {
        this.omaState.processing = true;
        this.omaState.message = "Connecting to terminal...";
        this.omaState.error = false;
        this.omaState.success = false;
        this.selfOrder.paymentError = false;

        // Start the countdown timer
        this.startTimer();

        try {
            // Update message after connection
            await new Promise(resolve => setTimeout(resolve, 500));
            this.omaState.message = "Please insert or tap your card on the terminal";

            const response = await rpc(`/pos_payment_oma/pay/${this.selfOrder.config.id}`, {
                order: this.selfOrder.currentOrder.serialize({ orm: true }),
                access_token: this.selfOrder.access_token,
                payment_method_id: this.state.paymentMethodId,
            });

            this.stopTimer();

            if (response.success) {
                this.omaState.success = true;
                this.omaState.processing = false;
                this.omaState.message = "Payment Approved!";

                // Wait a moment to show success message
                await new Promise(resolve => setTimeout(resolve, 2000));

                // Navigate to confirmation page
                this.router.navigate("confirmation", {
                    orderAccessToken: response.order_access_token,
                    screenMode: "pay",
                });
            } else {
                // Show terminal error message
                this.omaState.error = true;
                this.omaState.processing = false;
                this.omaState.message = response.error || "Payment declined by terminal";
                this.selfOrder.paymentError = true;
            }
        } catch (error) {
            this.stopTimer();
            this.omaState.error = true;
            this.omaState.processing = false;

            // Show specific error message
            if (error.message) {
                this.omaState.message = `Terminal Error: ${error.message}`;
            } else {
                this.omaState.message = "Connection to terminal failed. Please try again.";
            }

            this.selfOrder.paymentError = true;
        }
    },

    retryOmaPayment() {
        this.omaState.error = false;
        this.omaState.success = false;
        this.omaState.message = "";
        this.selfOrder.paymentError = false;
        this.startOmaPayment();
    },

    cancelOmaPayment() {
        this.stopTimer();
        this.omaState.processing = false;
        this.omaState.error = false;
        this.omaState.success = false;
        this.omaState.message = "";
        this.state.selection = true;
        this.state.paymentMethodId = null;
        this.selfOrder.paymentError = false;
    },
});
