/** @odoo-module **/

import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { patch } from "@web/core/utils/patch";

patch(Orderline, {
    props: {
        ...Orderline.props,
        line: {
            ...Orderline.props.line,
            shape: {
                ...Orderline.props.line.shape,
                secondary_price: {type: [Boolean, String, Number],optional: true,},
                secondary_unit_price: {type: String,optional: true,},
                secondary_unit_name: {type: String,optional: true,},
                get_current_uom: {type: String,optional: true,},
                display_secondary_receipt_changes: {type: Boolean,optional: true,},
                display_secondary_cart: {type: Boolean,optional: true,},
                unit_price: {type: Number,optional: true,},
                primary_qty: {type: Number,optional: true,},
            },
        },
    },
});
