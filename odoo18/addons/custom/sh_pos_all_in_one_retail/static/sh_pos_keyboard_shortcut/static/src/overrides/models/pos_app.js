/** @odoo-module */

import { Chrome } from "@point_of_sale/app/pos_app";
import { patch } from "@web/core/utils/patch";
import { PartnerList } from "@point_of_sale/app/screens/partner_list/partner_list";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";


patch(Chrome.prototype, {
     setup() {
         super.setup(...arguments)
document.addEventListener("keydown", (event) => {
    if(self && self.posmodel && self.posmodel.keysPressed){
        self.posmodel.keysPressed[event.key] = true;
    }
});

document.addEventListener("keyup", (event) => {
    if(self && self.posmodel && self.posmodel.keysPressed){
        delete self.posmodel.keysPressed[event.key];
    }
});

document.addEventListener("keydown", async(event) => {
    
    if (self && self.posmodel && self.posmodel.config && self.posmodel.config.sh_enable_shortcut &&  self.posmodel.keysPressed) {
        self.posmodel.keysPressed[event.key] = true;
        self.posmodel.pressedKeyList = [];
        self.posmodel.product_selection;
        
        for (let key in self.posmodel.keysPressed) {
            console.log("key ", key);
            
            if (self.posmodel.keysPressed[key]) {
                self.posmodel.pressedKeyList.push(key);
            }
        }
        if (self.posmodel.pressedKeyList.length > 0) {
            let pressed_key = "";
            for (let i = 0; i < self.posmodel.pressedKeyList.length > 0; i++) {
                if (self.posmodel.pressedKeyList[i]) {
                    if (pressed_key != "") {
                        pressed_key = pressed_key + "+" + self.posmodel.pressedKeyList[i];
                    } else {
                        pressed_key = self.posmodel.pressedKeyList[i];
                    }
                }
            };
            
            if (posmodel.get_order() && posmodel.get_order().get_screen_data() && posmodel.get_order().get_screen_data().name  == "PaymentScreen") {
                if (self.posmodel.screen_by_key[pressed_key]) {
                    event.preventDefault();
                        let payment_methods = self.posmodel.models["pos.payment.method"].getAllBy("id");
                        if(payment_methods){
                            let payment_method = payment_methods[self.posmodel.screen_by_key[pressed_key]]
                            if (payment_method) {
                                posmodel.get_order().add_paymentline(payment_method);
                            }
                        }
                }
            }
            
            for (let key in self.posmodel.key_screen_by_id) {
                if (self.posmodel.key_screen_by_id[key] == pressed_key) {
                    if (!document.querySelector(".border-0.mx-2:focus") && !document.querySelector("textarea:focus")) {
                        if (key == "select_up_orderline") {
                            event.preventDefault();
                            event.stopPropagation();
                            if (posmodel.get_order() && posmodel.get_order().get_screen_data() && posmodel.get_order().get_screen_data().name  == "ProductScreen") {
                                const selectedItem = document.querySelector("div.product-screen .order-container li.selected");
                                const previousOrderLine = selectedItem ? selectedItem.previousElementSibling : null;
                                if (previousOrderLine && previousOrderLine.classList.contains('orderline')) {
                                    previousOrderLine.click();
                                }

                            }
                        } else if (key == "select_down_orderline") {
                            event.preventDefault();
                            event.stopPropagation();
                            if (posmodel.get_order() && posmodel.get_order().get_screen_data() && posmodel.get_order().get_screen_data().name  == "ProductScreen") {
                                let selectedItem = document.querySelector("div.product-screen .order-container li.selected");
                                let nextOrderLine = selectedItem ? selectedItem.nextElementSibling : null;
                                if (nextOrderLine && nextOrderLine.classList.contains('orderline')) {
                                    nextOrderLine.click();
                                }
                            }
                        } 
                        else if (key == "go_payment_screen") {                            
                            event.preventDefault();
                            event.stopPropagation();
                            if (posmodel.get_order() && posmodel.get_order().get_screen_data() && posmodel.get_order().get_screen_data().name  == "ProductScreen") {
                                const payElements = document.querySelectorAll('.pay');
                                if (payElements.length > 0) {
                                    payElements[0].click();
                                }
                                self.posmodel.keysPressed = {};
                            }
                        } else if (key == "go_customer_Screen") {
                            event.preventDefault();
                            event.stopPropagation();
                            if (posmodel.get_order() && posmodel.get_order().get_screen_data() && posmodel.get_order().get_screen_data().name  == "ProductScreen") {                                
                                self.posmodel.selectPartner()
                            }
                            if (posmodel.get_order() && posmodel.get_order().get_screen_data() && posmodel.get_order().get_screen_data().name  == "PaymentScreen") {                                
                                self.posmodel.selectPartner()
                            }
                        } else if (key == "validate_order") {
                            event.preventDefault();
                            event.stopPropagation();
                            if (posmodel.get_order() && posmodel.get_order().get_screen_data() && posmodel.get_order().get_screen_data().name  == "PaymentScreen") {
                                const nextButton = document.querySelector(".next");
                                if (nextButton && nextButton.classList.contains("highlight")) {
                                    nextButton.click();
                                }
                            }
                        } else if (key == "next_order") {
                            event.preventDefault();
                            event.stopPropagation();
                            if (posmodel.get_order() && posmodel.get_order().get_screen_data() && posmodel.get_order().get_screen_data().name  == "ReceiptScreen") {
                                posmodel.add_new_order();
                            }
                        } else if (key == "go_to_previous_screen") {
                            event.preventDefault();
                            event.stopPropagation();
                            if (posmodel.get_order() && posmodel.get_order().get_screen_data() && posmodel.get_order().get_screen_data().name  == "PaymentScreen") {
                                posmodel.onClickBackButton()
                            }
                            if (posmodel.isTicketScreenShown) {
                                posmodel.closeScreen()
                            }
                        } else if (key == "select_quantity_mode") {
                            if (posmodel.get_order() && posmodel.get_order().get_screen_data() && posmodel.get_order().get_screen_data().name  == "ProductScreen") { 
                                posmodel.numpadMode = "quantity"
                            }
                        } else if (key == "select_discount_mode") {
                            if (posmodel.get_order() && posmodel.get_order().get_screen_data() && posmodel.get_order().get_screen_data().name  == "ProductScreen") { 
                               posmodel.numpadMode = "discount"
                            }
                        } else if (key == "select_price_mode") {
                            if (posmodel.get_order() && posmodel.get_order().get_screen_data() && posmodel.get_order().get_screen_data().name  == "ProductScreen") { 
                                posmodel.numpadMode = "price"
                            }
                        } else if (key == "search_product") {
                            event.preventDefault();
                            event.stopPropagation();
                            if (!posmodel.isTicketScreenShown) {
                                if (posmodel.get_order() && posmodel.get_order().get_screen_data() && posmodel.get_order().get_screen_data().name  == "ProductScreen") { 
                                    let  inputSearchProduct = document.querySelector('input[placeholder="Search products..."]');
                                    inputSearchProduct.focus();                                
                                }
                            }
                        } else if (key == "add_new_order") {
                            event.preventDefault();
                            event.stopPropagation();
                            self.posmodel.add_new_order()
                            self.posmodel.showScreen("ProductScreen");
                        } else if (key == "destroy_current_order") {
                            event.preventDefault();
                            event.stopPropagation();
                            let deleteButton = document.querySelector("div.ticket-screen div.orders div.order-row.highlight div.delete-button");
                            if (deleteButton) {
                                deleteButton.click();
                            }
                        } else if (key == "delete_orderline") {
                            if (posmodel.get_order() && posmodel.get_order().get_screen_data() && posmodel.get_order().get_screen_data().name  == "ProductScreen") { 
                                if (self.posmodel.get_order().get_selected_orderline()) {
                                    self.posmodel.get_order().removeOrderline(self.posmodel.get_order().get_selected_orderline());
                                }
                            }
                        } else if (key == "create_customer") {
                            event.preventDefault();
                            event.stopPropagation();
                            let partnerListScreen = document.querySelector(".partner-list");
                            if (partnerListScreen && partnerListScreen.offsetParent !== null) {
                               self.posmodel.editPartner()
                            }
                        }  else if (key == "edit_customer") {
                                event.preventDefault();
                                event.stopPropagation();
                                let partnerListScreen = document.querySelector(".partner-list");
                                if (partnerListScreen && partnerListScreen.offsetParent !== null) {
                                    if(self && self.posmodel && self.posmodel.get_order() && self.posmodel.get_order().get_partner()){
                                        self.posmodel.editPartner(self.posmodel.get_order().get_partner())
                                    }else{
                                        self.posmodel.editPartner()
                                    }
                                  
                                }
                        } else if (key == "select_up_payment_line") {                            
                            if (posmodel.get_order() && posmodel.get_order().get_screen_data() && posmodel.get_order().get_screen_data().name  == "PaymentScreen") {
                                if (document.querySelectorAll("div.paymentline.selected").length > 0) {
                                    let highlighted_payment_line = document.querySelector("div.paymentline.selected");
                                    let prevLine = highlighted_payment_line.previousElementSibling;
                                    if (prevLine && prevLine.classList.contains("paymentline")) {
                                        highlighted_payment_line.classList.remove("selected","bg-200");
                                        prevLine.classList.add("selected" ,"bg-200");
                                    }
                                } else {
                                    let paymentLines = document.querySelectorAll("div.paymentline");
                                
                                    if (paymentLines.length > 0) {
                                        paymentLines[paymentLines.length - 1].classList.add("selected","bg-200");
                                    }
                                }
                                
                            }
                        } 
                        else if (key == "select_down_payment_line") {
                            if (posmodel.get_order() && posmodel.get_order().get_screen_data() && posmodel.get_order().get_screen_data().name  == "PaymentScreen") {
                                if (document.querySelectorAll("div.paymentline.selected").length > 0) {
                                    let highlighted_payment_line = document.querySelector("div.paymentline.selected");                                    
                                    let prevLine = highlighted_payment_line.nextElementSibling;
                                    if (prevLine && prevLine.classList.contains("paymentline")) {
                                        highlighted_payment_line.classList.remove("selected","bg-200");
                                        prevLine.classList.add("selected" ,"bg-200");
                                    }
                                } else {
                                    let paymentLines = document.querySelectorAll("div.paymentline"); 
                                    if (paymentLines.length > 0) {
                                        paymentLines[paymentLines.length - 1].classList.add("selected","bg-200");
                                    }
                                }
                            }
                        }
                         else if (key == "delete_payment_line") {
                            if (posmodel.get_order() && posmodel.get_order().get_screen_data() && posmodel.get_order().get_screen_data().name  == "PaymentScreen") {
                                if(posmodel.get_order() && posmodel.get_order().get_selected_paymentline()){
                                    posmodel.get_order().remove_paymentline(posmodel.get_order().get_selected_paymentline())
                                }
                            }
                        } else if (key == "+10") {
                            if (posmodel.get_order() && posmodel.get_order().get_screen_data() && posmodel.get_order().get_screen_data().name  == "PaymentScreen") {
                                let buttons = document.querySelectorAll("button");
                                let btn = Array.from(buttons).find(button => button.textContent.includes('+10'));
                                if (btn) {
                                    btn.click();
                                }

                            }                        
                        } else if (key == "+20") {
                            if (posmodel.get_order() && posmodel.get_order().get_screen_data() && posmodel.get_order().get_screen_data().name  == "PaymentScreen") {
                                let buttons = document.querySelectorAll("button");
                                let btn = Array.from(buttons).find(button => button.textContent.includes('+20'));
                                if (btn) {
                                    btn.click();
                                }
                            }
                        } else if (key == "+50") {
                            if (posmodel.get_order() && posmodel.get_order().get_screen_data() && posmodel.get_order().get_screen_data().name  == "PaymentScreen") {
                                let buttons = document.querySelectorAll("button");
                                let btn = Array.from(buttons).find(button => button.textContent.includes('+50'));
                                if (btn) {
                                    btn.click();
                                }
                            }
                        } else if (key == "go_order_Screen") {
                            if (posmodel.get_order() && posmodel.get_order().get_screen_data() && (posmodel.get_order().get_screen_data().name  == "ProductScreen" || posmodel.get_order().get_screen_data().name  == "PaymentScreen" )) {
                                self.posmodel.showScreen("TicketScreen")
                            }
                        } else if (key == "search_order") {
                            event.preventDefault();
                            event.stopPropagation();
                            if (posmodel.isTicketScreenShown) {
                                let inputSearchOrder = document.querySelector('input[placeholder="Search Orders..."]');
                                if (inputSearchOrder) {
                                    inputSearchOrder.focus();
                                }

                            }
                        } else if (key == "select_up_order") {
                            if (posmodel.isTicketScreenShown) {
                                let orderRows = document.querySelectorAll("div.ticket-screen div.orders div.order-row");
                                
                                
                                if (Array.from(orderRows).some(row => row.classList.contains("highlight"))) {
                                    let highlighted_order = Array.from(orderRows).find(row => row.classList.contains("highlight"));
                                    let prevRow = highlighted_order.previousElementSibling;
                                    
                                    if (prevRow && prevRow.classList.contains("order-row")) {
                                        console.log("orderRows",prevRow);
                                        prevRow.classList.add("highlight", "bg-primary", "text-white");
                                        highlighted_order.classList.remove("highlight", "bg-primary", "text-white");
                                    }
                                } else {
                                    if (orderRows.length > 0) {
                                        orderRows[orderRows.length - 1].classList.add("highlight", "bg-primary", "text-white");
                                    }
                                }

                            }
                        } else if (key == "select_down_order") {
                            if (posmodel.isTicketScreenShown) {
                                let orderRows = document.querySelectorAll("div.ticket-screen div.orders div.order-row");
                                let highlighted_order = Array.from(orderRows).find(row => row.classList.contains("highlight"));
                                console.log("highlighted_order",highlighted_order);
                                
                                if (highlighted_order) {
                                    let nextRow = highlighted_order.nextElementSibling;
                                    if (nextRow && nextRow.classList.contains("order-row")) {
                                        nextRow.classList.add("highlight", "bg-primary", "text-white");
                                        highlighted_order.classList.remove("highlight", "bg-primary", "text-white");
                                    }
                                } else {
                                    if (orderRows.length > 0) {
                                        orderRows[0].classList.add("highlight", "bg-primary", "text-white");
                                    }
                                }

                            }
                        } else if (key == "select_order") {
                            if (posmodel.isTicketScreenShown) {
                                let highlightedOrder = document.querySelector("div.ticket-screen div.orders div.order-row.highlight");
                                if (highlightedOrder) {
                                    highlightedOrder.click();
                                }
                            }
                        }else if (key == "select_product") {
                            
                            if (posmodel.get_order().get_screen_data().name  == "ProductScreen") {
                                if (!self.posmodel.product_selection) {
                                    self.posmodel.product_selection=document.querySelector("article");
                                    self.posmodel.product_selection.classList.add("sh_selected_product")
                                }else{
                                    self.posmodel.product_selection.classList.remove("sh_selected_product")
                                    self.posmodel.product_selection=self.posmodel.product_selection.nextElementSibling;
                                    self.posmodel.product_selection.classList.add("sh_selected_product")
                                } 
                            }
                        }else if (key == "add_product_cart") {
                            if (posmodel.get_order().get_screen_data().name  == "ProductScreen") {
                                if (self.posmodel.product_selection) {
                                    self.posmodel.product_selection.click()
                                }
                            }
                        }else if (key == "close_register") {
                            if (self.posmodel) {
                                self.posmodel.closeSession()
                            }
                        }else if (key == "change_cashier") {
                            if (self.posmodel) {
                                if (self.posmodel.config.module_pos_hr) {
                                    let cashier_button=document.querySelector('.cashier-name')
                                    if (cashier_button) {
                                        cashier_button.click()
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
});

document.addEventListener("keyup", (event) => {
    if(self && self.posmodel ){
        self.posmodel.keysPressed = {};
        delete self.posmodel.keysPressed[event.key];
    }
});


    }
})