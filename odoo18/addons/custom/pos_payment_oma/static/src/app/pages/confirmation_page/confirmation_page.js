import { ConfirmationPage } from "@pos_self_order/app/pages/confirmation_page/confirmation_page";
import { patch } from "@web/core/utils/patch";

patch(ConfirmationPage.prototype, {
    setup() {
        super.setup(...arguments);
    },

    get invoiceUrl() {
        return `/pos_payment_oma/download_invoice/${this.props.orderAccessToken}`;
    },

    previewInvoice() {
        window.open(this.invoiceUrl, "_blank");
    },

    async printInvoice() {
        const iframe = document.createElement("iframe");
        iframe.style.display = "none";
        iframe.src = this.invoiceUrl;
        document.body.appendChild(iframe);
        iframe.onload = () => {
            iframe.contentWindow.focus();
            iframe.contentWindow.print();
        };
    }
});
