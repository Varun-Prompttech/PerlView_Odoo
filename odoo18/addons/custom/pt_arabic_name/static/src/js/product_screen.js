/** @odoo-module */

import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { patch } from "@web/core/utils/patch";


// Patch Orderline to accept arabic_name inside props.line.shape
patch(Orderline, {
    props: {
        ...Orderline.props,
        line: {
            ...Orderline.props.line,
            shape: {
                ...Orderline.props.line.shape,
                arabic_name: { type: String, optional: true },  // Add arabic_name
            },
        },
    },
});

// Log to confirm Orderline shape update
console.log("Updated Orderline Props:", Orderline.props.line.shape);

patch(PosOrderline.prototype, {
    getDisplayData() {
        const displayData = super.getDisplayData();

        //Fetch `arabic_name` from `this`
        displayData.arabic_name = this.product_id.arabic_name || "No Arabic Name";

        console.log("Arabic Name in PosOrderline:", this.product_id);
        console.log("PosOrderline:", displayData);
        return displayData;
    },
});

// Log to check if patching works
console.log("Patching completed for Orderline and PosOrderline!");

patch(OrderWidget.prototype, {
     /**
     * Get the total number of items in the order.
     *
     * @returns {number} The total number of items in the order.
     */
    get ItemCount(){
       return this.props.lines.length
    },
     /**
     * Get the total quantity of items in the order.
     *
     * @returns {number} The total quantity of items in the order.
     */
    get TotalQuantity(){
        var totalQuantity = 0;
        this.props.lines.forEach(line => totalQuantity += line.qty);
        return totalQuantity
    },

});

patch(Orderline.prototype, {
    /**
    * Get the Arabic name of the products in the order lines.
    *
    * @returns {String} The arabic name of product.
    */
    get ArabicName() {
        console.log("Orderline props:", this.line.arabic_name);
        return this.line.arabic_name;
    },

});

