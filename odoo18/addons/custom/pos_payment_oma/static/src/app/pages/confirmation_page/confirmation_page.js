import { ConfirmationPage } from "@pos_self_order/app/pages/confirmation_page/confirmation_page";
import { patch } from "@web/core/utils/patch";
import { useState } from "@odoo/owl";

/**
 * Patch the ConfirmationPage to customize the order reference display.
 *
 * Printing: We do NOT override printOrderAfterTime() here.
 * The native Odoo POS self-order flow handles printing automatically using
 * the printer service (this.printer.print(OrderReceipt, ...)) which renders
 * the receipt as HTML and prints via window.print() to the browser's default printer.
 * This works regardless of whether Odoo is accessed locally or remotely,
 * because window.print() always targets the local machine's printers.
 */
patch(ConfirmationPage.prototype, {
    setup() {
        super.setup(...arguments);
        this.state = useState({
            ...this.state,
        });
    },
});
