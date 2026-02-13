/** @odoo-module */

import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { patch } from "@web/core/utils/patch";
import { ShValidationTypePopup } from "@sh_pos_all_in_one_retail/static/sh_pos_manager_validation/app/popups/validation_type_popup/validation_type_popup";

patch(TicketScreen.prototype, {
    async  onDeleteOrder(order) {
        if (this.pos.config.sh_pos_manager_validation && this.pos.get_order().one_time_validation == false && this.pos.config.sh_order_delete_pw && order.one_time_validation == false) {
            let validation_type = this.pos.config.sh_validation_type
            if (validation_type == 'pin') {
                let res = await this.pos.get_order().numberpopup()
                if (res) {
                    super. onDeleteOrder(order)
                    if (this.pos.config.sh_one_time_password) {
                        this.pos.get_order().one_time_validation = true
                    }
                }
                else {
                    return false
                }
            }
            else if (validation_type == 'password') {
                let res = await this.pos.get_order().passwordpopup()
                if (res) {
                    super. onDeleteOrder(order)
                    if (this.pos.config.sh_one_time_password) {
                        this.pos.get_order().one_time_validation = true
                    }
                }
                else {
                    return false
                }
            }
            else if (validation_type == 'barcode') {
                let res = await this.pos.get_order().barcodepopup()
                if (res) {
                    super. onDeleteOrder(order)
                    if (this.pos.config.sh_one_time_password) {
                        this.pos.get_order().one_time_validation = true
                    }
                }
                else {
                    return
                }
            }
            else {
                const { confirmed, payload } =await this.env.services.popup.add(ShValidationTypePopup)
                if (confirmed) {
                    super. onDeleteOrder(order)
                    if (this.pos.config.sh_one_time_password) {
                        this.pos.get_order().one_time_validation = true
                    }
                }
                else {
                    return
                }
            }
            
        }
        else {
            super. onDeleteOrder(order)
        }
    }
});
