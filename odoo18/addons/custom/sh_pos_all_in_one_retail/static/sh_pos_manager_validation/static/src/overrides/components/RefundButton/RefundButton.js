// /** @odoo-module */

// import { RefundButton } from "@point_of_sale/app/screens/product_screen/control_buttons/refund_button/refund_button";
// import { patch } from "@web/core/utils/patch";
// import { usePos } from "@point_of_sale/app/store/pos_hook";
// import { ShValidationTypePopup } from "@sh_pos_manager_validation/app/popups/validation_type_popup/validation_type_popup";

// patch(RefundButton.prototype, {
//     setup() {
//         super.setup()
//         this.pos = usePos();
//     },
//     async click() {
//         console.log("5tyui",this.pos.get_order().one_time_validation);
//         if (this.pos.config.sh_pos_manager_validation && this.pos.config.sh_refund_pw && this.pos.get_order().one_time_validation == false) {
//             let validation_type = this.pos.config.sh_validation_type
//             if (validation_type == 'pin') {
//                 let res = await this.pos.get_order().numberpopup()
//                 if (res) {
//                     super.click()
//                     if (this.pos.config.sh_one_time_password) {
//                         this.pos.get_order().one_time_validation = true
//                     }
//                 }
//                 else {
//                     return false
//                 }

//             }
//             else if (validation_type == 'password') {
//                 let res = await this.pos.get_order().passwordpopup()
//                 if (res) {
//                     super.click()
//                     if (this.pos.config.sh_one_time_password) {
//                         this.pos.get_order().one_time_validation = true
//                     }
//                 }
//                 else {
//                     return false
//                 }
//             }
//             else if (validation_type == 'barcode') {
//                 let res = await this.pos.get_order().barcodepopup()
//                 if (res) {
//                     super.click()
//                     if (this.pos.config.sh_one_time_password) {
//                         this.pos.get_order().one_time_validation = true
//                     }
//                 }
//                 else {
//                     return false
//                 }
//             }
//             else {
//                 console.log("sh_validation_type");
//                 const { confirmed, payload } = await this.env.services.popup.add(ShValidationTypePopup)
//                 if (confirmed) {
//                     super.click()
//                     if (this.pos.config.sh_one_time_password) {
//                         this.pos.get_order().one_time_validation = true
//                     }
//                 }
//                 else {
//                     return false
//                 }
//             }
//         }
//         super.click()
//     }
// })