import { ConfirmationPage } from "@pos_self_order/app/pages/confirmation_page/confirmation_page";
import { patch } from "@web/core/utils/patch";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";

/**
 * Patch ConfirmationPage to enable browser-based printing (window.print)
 * when no IoT Box / hardware printer device is configured.
 *
 * The native Odoo POS printHtml() silently skips printing if no device is set.
 * This override enables { webPrintFallback: true } so that window.print()
 * is triggered, which prints to the browser's local default printer.
 * This works for both local and remote server access.
 */
patch(ConfirmationPage.prototype, {
    async printOrderAfterTime() {
        try {
            if (this.confirmedOrder && Object.keys(this.confirmedOrder).length > 0) {
                const el = await this.printer.renderer.toHtml(OrderReceipt, {
                    data: this.selfOrder.orderExportForPrinting(this.confirmedOrder),
                    formatCurrency: this.selfOrder.formatMonetary.bind(this.selfOrder),
                });

                // Try hardware printer first, fall back to window.print()
                const result = await this.printer.printHtml(el, { webPrintFallback: true });

                if (!result && !this.printer.device) {
                    // If printHtml returned false and no device, use printWeb directly
                    this.printer.printWeb(el);
                }

                if (!this.selfOrder.has_paper) {
                    this.updateHasPaper(true);
                }
            } else {
                setTimeout(() => this.printOrderAfterTime(), 500);
            }
        } catch (e) {
            if (e.errorCode === "EPTR_REC_EMPTY") {
                this.dialog.add(
                    (await import("@pos_self_order/app/components/out_of_paper_popup/out_of_paper_popup")).OutOfPaperPopup,
                    {
                        title: `No more paper in the printer, please remember your order number: '${this.confirmedOrder.trackingNumber}'.`,
                        close: () => {
                            this.router.navigate("default");
                        },
                    }
                );
                this.updateHasPaper(false);
            } else {
                console.error("Print error:", e);
            }
        }
    },
});
