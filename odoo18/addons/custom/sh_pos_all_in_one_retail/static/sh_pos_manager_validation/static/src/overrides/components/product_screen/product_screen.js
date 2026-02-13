// /** @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
// import { ShValidationTypePopup } from "@sh_pos_manager_validation/app/popups/validation_type_popup/validation_type_popup";
// import { BarcodePopup } from "@sh_pos_manager_validation/app/popups/barcode_popup/barcode_popup";
import { useBarcodeReader } from "@point_of_sale/app/barcode/barcode_reader_hook";

patch(ProductScreen.prototype, {
     setup() {
        super.setup(...arguments);
        // this.notification = useService("notification");
        useBarcodeReader({
          authorize: this.sh_authorize,
        });
    },
    async sh_authorize(code) {
        console.log('=authorize: ===> ',code);
        
    },
    // async _setValue(val) {
    //     if (this.pos.config.sh_pos_manager_validation) {
    //         if (this.pos.get_order().one_time_validation == false && this.pos.get_order().get_orderlines().length) {
    //             var def_qty = this.pos.get_order().selected_orderline.quantity
    //             var def_price = this.pos.get_order().selected_orderline.price
    //             let validation_type = this.pos.config.sh_validation_type
    //             if(this.pos.numpadMode == "quantity" && this.pos.config.sh_qty_pw){
    //                 console.log("===================", this.numberBuffer);
    //                 if(def_qty < val || val == null){
    //                     super._setValue(val)
    //                     if (this.pos.config.sh_one_time_password) {
    //                         this.pos.get_order().one_time_validation = true
    //                     }
    //                 }
    //                 else{
    //                     if(validation_type == 'pin'){
    //                         let res = await this.pos.get_order().numberpopup()
    //                         if(res){
    //                             super._setValue(val)
    //                             if (this.pos.config.sh_one_time_password) {
    //                                 this.pos.get_order().one_time_validation = true
    //                             }
    //                         }
    //                         else{
    //                             var qty = this.pos.get_order().selected_orderline.quantity;
    //                             if (this.pos.first_attempt) {
    //                                  this.numberBuffer.reset();;
    //                             }
    //                             super._setValue(qty)
    //                             this.numberBuffer.state.buffer = qty.toString();
    //                             // this.trigger('buffer-update', qty.toString());
    //                             this.pos.qty_value = true
    //                         }
    //                     }
    //                     else if(validation_type == 'password'){
    //                         let res = await this.pos.get_order().passwordpopup()
    //                         if(res){
    //                             super._setValue(val)
    //                             if (this.pos.config.sh_one_time_password) {
    //                                 this.pos.get_order().one_time_validation = true
    //                             }
    //                         }
    //                         else{
    //                             var qty = this.pos.get_order().selected_orderline.quantity;
    //                             if (this.pos.first_attempt) {
    //                                  this.numberBuffer.reset();;
    //                             }
    //                             super._setValue(qty)
    //                             this.numberBuffer.state.buffer = qty.toString();
    //                             // this.trigger('buffer-update', qty.toString());
    //                             this.pos.qty_value = true
    //                         }
    //                     }
    //                     else if(validation_type == 'barcode'){
    //                         const { confirmed } = await this.env.services.popup.add(BarcodePopup)
    //                         if(confirmed){
    //                             super._setValue(val)
    //                             if (this.pos.config.sh_one_time_password) {
    //                                 this.pos.get_order().one_time_validation = true
    //                             }
    //                         }
    //                         else{
    //                             var qty = this.pos.get_order().selected_orderline.quantity;
    //                             if (this.pos.first_attempt) {
    //                                  this.numberBuffer.reset();;
    //                             }
    //                             super._setValue(qty)
    //                             this.numberBuffer.state.buffer = qty.toString();
    //                             // this.trigger('buffer-update', qty.toString());
    //                             this.pos.qty_value = true
    //                         }
    //                     }   
    //                     else{
    //                         if(!this.pos.get_order().number_buffer_reset){
    //                             this.pos.get_order().number_buffer_reset = true
    //                             const { confirmed } = await this.env.services.popup.add(ShValidationTypePopup, {mode : 'quantity'})
    //                             if(confirmed){
    //                                 this.pos.get_order().number_buffer_reset = false
    //                                 super._setValue(val)
    //                                 if (this.pos.config.sh_one_time_password) {
    //                                     this.pos.get_order().one_time_validation = true
    //                                 }
    //                             }
    //                             else{
    //                                 this.pos.get_order().number_buffer_reset = false
    //                                 var qty = this.pos.get_order().selected_orderline.quantity;
    //                                 if (this.pos.first_attempt) {
    //                                      this.numberBuffer.reset();;
    //                                 }
    //                                 super._setValue(qty)
    //                                 this.numberBuffer.state.buffer = qty.toString();
    //                                 // this.trigger('buffer-update', qty.toString());
    //                                 this.pos.qty_value = true
    //                             }
    //                         }
    //                     }
    //                 }
    //             }
    //             else if(this.pos.config.sh_order_line_delete_pw){
    //                 if(def_qty == 0){
    //                     if(validation_type == 'pin'){
    //                         let res = await this.pos.get_order().numberpopup()
    //                         if(res){
    //                             let line = this.pos.get_order().get_selected_orderline()
    //                             this.pos.get_order().removeOrderline(line)
    //                             if (this.pos.config.sh_one_time_password) {
    //                                 this.pos.get_order().one_time_validation = true
    //                             }
    //                         }
    //                         else{
    //                             var qty = this.pos.get_order().selected_orderline.quantity;
    //                             if (this.pos.first_attempt) {
    //                                  this.numberBuffer.reset();;
    //                             }
    //                             super._setValue(qty)
    //                             this.numberBuffer.state.buffer = qty.toString();
    //                             // this.trigger('buffer-update', qty.toString());
    //                             this.pos.qty_value = true
    //                         }
    //                     }
    //                     else if(validation_type == 'password'){
    //                         let res = await this.pos.get_order().passwordpopup()
    //                         if(res){
    //                             let line = this.pos.get_order().get_selected_orderline()
    //                             this.pos.get_order().removeOrderline(line)
    //                             if (this.pos.config.sh_one_time_password) {
    //                                 this.pos.get_order().one_time_validation = true
    //                             }
    //                         }
    //                         else{
    //                             var qty = this.pos.get_order().selected_orderline.quantity;
    //                             if (this.pos.first_attempt) {
    //                                  this.numberBuffer.reset();;
    //                             }
    //                             super._setValue(qty)
    //                             this.numberBuffer.state.buffer = qty.toString();
    //                             // this.trigger('buffer-update', qty.toString());
    //                             this.pos.qty_value = true
    //                         }
    //                     }
    //                     else if(validation_type == 'barcode'){
    //                         const { confirmed } = await this.env.services.popup.add(BarcodePopup)
    //                         if(confirmed){
    //                             let line = this.pos.get_order().get_selected_orderline()
    //                                this.pos.get_order().removeOrderline(line)
    //                             if (this.pos.config.sh_one_time_password) {
    //                                 this.pos.get_order().one_time_validation = true
    //                             }
    //                         }
    //                         else{
    //                             var qty = this.pos.get_order().selected_orderline.quantity;
    //                             if (this.pos.first_attempt) {
    //                                  this.numberBuffer.reset();;
    //                             }
    //                             super._setValue(qty)
    //                             this.numberBuffer.state.buffer = qty.toString();
    //                             // this.trigger('buffer-update', qty.toString());
    //                             this.pos.qty_value = true
    //                         }
    //                     }   
    //                     else{
    //                         if(!this.pos.get_order().number_buffer_reset){
    //                             this.pos.get_order().number_buffer_reset = true
    //                             const { confirmed } = await await this.env.services.popup.add(ShValidationTypePopup, {mode : 'quantity'})
    //                             if(confirmed){
    //                                let line = this.pos.get_order().get_selected_orderline()
    //                                console.log("line ===>", line);
    //                                this.pos.get_order().removeOrderline(line)
    //                                 this.pos.get_order().number_buffer_reset = false
    //                                 if (this.pos.config.sh_one_time_password) {
    //                                     this.pos.get_order().one_time_validation = true
    //                                 }
    //                             }
    //                             else{
    //                                 this.pos.get_order().number_buffer_reset = false
    //                                 var qty = this.pos.get_order().selected_orderline.quantity;
    //                                 if (this.pos.first_attempt) {
    //                                      this.numberBuffer.reset();;
    //                                 }
    //                                 super._setValue(qty)
    //                                 this.numberBuffer.state.buffer = qty.toString();
    //                                 // this.trigger('buffer-update', qty.toString());
    //                                 this.pos.qty_value = true
    //                             }
    //                          }
    //                     }
    //                 }
    //                 else{
    //                     super._setValue(val)
    //                 }
    //             }
    //             else{
    //                 super._setValue(val)
    //             }
    //         }
    //         else {
    //             super._setValue(val)
    //         }
    //     }
    //     else {
    //         super._setValue(val)
    //     }
    // },
    // async onNumpadClick(buttonValue){
    //     if (this.pos.config.sh_pos_manager_validation && this.pos.get_order().one_time_validation == false && this.pos.get_order().get_orderlines().length) {
    //         console.log("buttonValue", buttonValue , this.pos.get_order().one_time_validation);
    //         let validation_type = this.pos.config.sh_validation_type
    //         if((buttonValue == "discount" && this.pos.config.sh_discount_pw) || (buttonValue == "price" && this.pos.config.sh_price_pw)){
    //                 if(validation_type == 'pin'){
    //                     let res = await this.pos.get_order().numberpopup()
    //                     if(res){
    //                         super.onNumpadClick(buttonValue)
    //                         if (this.pos.config.sh_one_time_password) {
    //                             this.pos.get_order().one_time_validation = true
    //                         }
    //                     }
    //                     else{
    //                         return false
    //                     }
    //                 }
    //                 else if(validation_type == 'password'){
    //                     let res = await this.pos.get_order().passwordpopup()
    //                     if(res){
    //                         super.onNumpadClick(buttonValue)
    //                         if (this.pos.config.sh_one_time_password) {
    //                             this.pos.get_order().one_time_validation = true
    //                         }
    //                     }
    //                     else{
    //                        return false
    //                     }
    //                 }
    //                 else if(validation_type == 'barcode'){
    //                     const { confirmed } =await this.env.services.popup.add(BarcodePopup)
    //                     if(confirmed){
    //                         super.onNumpadClick(buttonValue)
    //                         if (this.pos.config.sh_one_time_password) {
    //                             this.pos.get_order().one_time_validation = true
    //                         }
    //                     }
    //                     else{
    //                         return false
    //                     }
    //                 }   
    //                 else{
    //                     if(!this.pos.get_order().number_buffer_reset){
    //                     this.pos.get_order().number_buffer_reset = true
    //                     const { confirmed } = await await this.env.services.popup.add(ShValidationTypePopup, {mode : 'discount'})
    //                     if(confirmed){
    //                         this.pos.get_order().number_buffer_reset = false
    //                         super.onNumpadClick(buttonValue)
    //                         if (this.pos.config.sh_one_time_password) {
    //                             this.pos.get_order().one_time_validation = true
    //                         }
    //                     }
    //                     else{
    //                        return false
    //                     }
    //                 }
    //                 }
    //             }
    //             else{
    //                 super.onNumpadClick(buttonValue)
    //             }                 
    //     }
    //     else{
    //         super.onNumpadClick(buttonValue)
    //     }
    // }
});
