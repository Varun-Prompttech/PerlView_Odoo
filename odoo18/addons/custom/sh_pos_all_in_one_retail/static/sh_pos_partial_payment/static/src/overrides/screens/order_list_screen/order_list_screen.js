/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { OrderListScreen } from "@sh_pos_all_in_one_retail/static/sh_pos_order_list/apps/screen/order_list_screen/order_list_screen";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(OrderListScreen.prototype, {
    setup() {
        this.dialog = useService("dialog");
        super.setup();
        this.pos = usePos();
    },
    sh_appy_search(search) {
        var self = this
        if (search == 'partial'){


            if (self.state.order_date) {
                // Date wise Condition.
                search = self.state.search_word;
                if (this.state.status != "all") {
                    return this.get_all_orders().filter(function (template) {
                        if ((template["sh_amount_residual"] > 0) && (template["date_order"].split(" ")[0] == self.state.order_date)) {
                            if (template.name.indexOf(search) > -1) {
                                return true;
                            }
                            if (template["pos_reference"] && template["pos_reference"].indexOf(search) > -1) {
                                return true;
                            }
                            if (template.partner_id) {
                                if (template.partner_id.name.indexOf(search) > -1 || template.partner_id.name.toLowerCase().indexOf(search) > -1) {
                                    return true;
                                }
                            }
                            if (template["date_order"] && template["date_order"].indexOf(search) > -1) {
                                return true;
                            }
                            if(!search){
                                return true;
                            }
                        }
                        return false;
                    })
                }else{
                    return this.get_all_orders().filter(function (template) {
                        if (template["date_order"].split(" ")[0] == self.state.order_date) {
                            if (template.name.indexOf(search) > -1) {
                                return true;
                            }
                            if (template["pos_reference"] && template["pos_reference"].indexOf(search) > -1) {
                                return true;
                            }
                            if (template.partner_id) {
                                if (template.partner_id.name.indexOf(search) > -1 || template.partner_id.name.toLowerCase().indexOf(search) > -1) {
                                    return true;
                                }
                            }
                            if (template["sh_amount_residual"] > 0) {
                                return true;
                            }
                            if (template["date_order"] && template["date_order"].indexOf(search) > -1) {
                                return true;
                            }
                            if(!search){
                                return true;
                            }
                        return false;
                        }
                    })
                }
                
            }else{
                search = self.state.search_word;
                if (this.state.status != "all") {
                    return this.get_all_orders().filter(function (template) {
                        if (template["sh_amount_residual"] > 0) {
                            if (template.name.indexOf(search) > -1) {
                                return true;
                            }
                            if (template["pos_reference"] && template["pos_reference"].indexOf(search) > -1) {
                                return true;
                            }
                            if (template.partner_id) {
                                if (template.partner_id.name.indexOf(search) > -1 || template.partner_id.name.toLowerCase().indexOf(search) > -1) {
                                    return true;
                                }
                            }
                            if (template["sh_amount_residual"] > 0) {
                                return true;
                            }
                            if (template["date_order"] && template["date_order"].indexOf(search) > -1) {
                                return true;
                            }
                            if(!search){
                                return true;
                            }
                        }
                        return false;
                    })
                }else{
                    return this.get_all_orders().filter(function (template) {
        
                            if (template.name.indexOf(search) > -1) {
                                return true;
                            }
                            if (template["pos_reference"] && template["pos_reference"].indexOf(search) > -1) {
                                return true;
                            }
                            if (template.partner_id) {
                                if (template.partner_id.name.indexOf(search) > -1 || template.partner_id.name.toLowerCase().indexOf(search) > -1) {
                                    return true;
                                }
                            }
                            if (template["sh_amount_residual"] > 0) {
                                return true;
                            }
                            if (template["date_order"] && template["date_order"].indexOf(search) > -1) {
                                return true;
                            }
                            if(!search){    
                                return true;
                            }
                        return false;
                    })
                }
    
            }
        }
        return super.sh_appy_search(search)
    },
    pay_pos_order(order_data) {
        var self = this;
        if (order_data) {
            if (self.pos.get_order().get_orderlines().length > 0) {
                self.pos.add_new_order()
            }
            var current_order = self.pos.get_order()
            var partial_product = self.pos.models["product.product"].find((product) => product.sh_is_partial_pay_product == true )    
            if (!partial_product){
                self.dialog.add(AlertDialog, {
                    title: _t("Not Found"),
                    body: _t(
                        "Partial product not found please check your configuration or product pos categories"
                    ),
                });
                return
            }
            if (current_order) {
                current_order.is_due_paid = true
                
                if (order_data.partner_id) {
                    current_order.set_partner(order_data.partner_id);
                }
                self.pos.addLineToCurrentOrder({
                    product_id: partial_product,
                    price_unit: order_data.sh_amount_residual,
                }, {}, false);
                if (order_data.sh_amount_residual) {
                    current_order.sh_due_amount = order_data.amount_paid
                } else {
                    current_order.sh_due_amount = 0.00
                }
                current_order.name = order_data.pos_reference;
                current_order.uuid = order_data.uuid;
                current_order.to_invoice = true;
                // current_order.id = order_data.id;
                // current_order.payment_ids = [];
                self.pos.pay()
            }
        }
    }
});
