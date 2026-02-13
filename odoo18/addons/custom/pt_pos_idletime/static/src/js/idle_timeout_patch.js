/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    get idleTimeout() {
        console.log("[IdleTimeoutPatch] Custom idleTimeout active");

        return [
            {
                timeout: 3600000, // 1 hour
                action: () => {
                    console.log("[IdleTimeoutPatch] 1h timeout fired");
                    if (this.mainScreen.component.name !== "PaymentScreen") {
                        this.showScreen("SaverScreen");
                    }
                },
            },
            {
                timeout: 120000, // 2 minutes
                action: () => {
                    console.log("[IdleTimeoutPatch] 2m login-timeout fired");
                    if (this.mainScreen.component.name === "LoginScreen") {
                        this.showScreen("SaverScreen");
                    }
                },
            },
        ];
    },
});
