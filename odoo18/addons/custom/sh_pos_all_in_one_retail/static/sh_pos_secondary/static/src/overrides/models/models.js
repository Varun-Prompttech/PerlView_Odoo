/** @odoo-module **/

import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { lt } from "@point_of_sale/utils";
import { accountTaxHelpers } from "@account/helpers/account_tax";
import { floatIsZero } from "@web/core/utils/numbers";
import { formatCurrency } from "@point_of_sale/app/models/utils/currency";

patch(PosOrder.prototype, {
    get taxTotals() {
        const currency = this.config.currency_id;
        const company = this.company;
        const orderLines = this.lines;
        const documentSign =
            this.lines.length === 0 ||
                !this.lines.every((l) => lt(l.qty, 0, { decimals: currency.decimal_places }))
                ? 1
                : -1;
        const baseLines = orderLines.map((line) => {
            return accountTaxHelpers.prepare_base_line_for_taxes_computation(
                line,
                line.prepareBaseLineForTaxesComputationExtraValues({
                    quantity: documentSign * line.get_primary_quantity() || line.qty,
                })
            );
        });
        accountTaxHelpers.add_tax_details_in_base_lines(baseLines, company);
        accountTaxHelpers.round_base_lines_tax_details(baseLines, company);
        // For the generic 'get_tax_totals_summary', we only support the cash rounding that round the whole document.
        const cashRounding =
            !this.config.only_round_cash_method && this.config.cash_rounding
                ? this.config.rounding_method
                : null;
        const taxTotals = accountTaxHelpers.get_tax_totals_summary(baseLines, currency, company, {
            cash_rounding: cashRounding,
        });

        taxTotals.order_sign = documentSign;
        taxTotals.order_total =
            taxTotals.total_amount_currency - (taxTotals.cash_rounding_base_amount_currency || 0.0);

        let order_rounding = 0;
        let remaining = taxTotals.order_total;
        const validPayments = this.payment_ids.filter((p) => p.is_done() && !p.is_change);
        for (const [payment, isLast] of validPayments.map((p, i) => [
            p,
            i === validPayments.length - 1,
        ])) {
            const paymentAmount = documentSign * payment.get_amount();
            if (isLast) {
                if (this.config.cash_rounding) {
                    const roundedRemaining = this.getRoundedRemaining(
                        this.config.rounding_method,
                        remaining
                    );
                    if (!floatIsZero(paymentAmount - remaining, this.currency.decimal_places)) {
                        order_rounding = roundedRemaining - remaining;
                    }
                }
            }
            remaining -= paymentAmount;
        }

        taxTotals.order_rounding = order_rounding;
        taxTotals.order_remaining = remaining;

        const remaining_with_rounding = remaining + order_rounding;
        if (floatIsZero(remaining_with_rounding, currency.decimal_places)) {
            taxTotals.order_has_zero_remaining = true;
        } else {
            taxTotals.order_has_zero_remaining = false;
        }

        return taxTotals;
    }
});

patch(PosStore.prototype, {
    async addLineToCurrentOrder(vals, opt = {}, configure = true) {
        var line = await super.addLineToCurrentOrder(vals, opt, configure);
        if (this.config.select_uom_type == "secondary" && line?.get_product() && line.get_product()?.sh_is_secondary_unit) {
            const selectedUOM = line.get_product().sh_secondary_uom
            let converted_qty = line.convert_qty_uom(line.qty, selectedUOM, line.get_current_uom())
            line.set_secondary_quantity(converted_qty);
            if (line.get_unit() == selectedUOM) {
                let primary_converted_qty = line.convert_qty_uom(line.qty, line.get_current_uom(), selectedUOM)
                console.log("converted_qty inside if: ", primary_converted_qty);
                line.set_primary_quantity(primary_converted_qty)
                line.change_current_uom(line.get_current_uom())
            } else {
                let primary_converted_qty = line.convert_qty_uom(line.qty, line.get_current_uom(), selectedUOM)                
                line.set_primary_quantity(primary_converted_qty)
                line.change_current_uom(selectedUOM)
            }
        }

        return line
    },
});



patch(PosOrderline.prototype, {
    getDisplayData() {
        let res = super.getDisplayData(...arguments)
        if (this.current_uom) {
            if($('.product-screen').length){
                res["unit"] = this.current_uom.name
            }else{
                res["unit"] = this.config.display_uom_in_receipt ? this.current_uom.name : this.get_product().uom_id.name
            }
//            if(!$('.product-screen').length){
//                res['qty'] = this.config.display_uom_in_receipt ? this.sh_qty : this.get_primary_quantity()
//            }
            if(!$('.product-screen').length){
            let qty_val = this.config.display_uom_in_receipt ? this.get_secondary_qty() : this.get_primary_quantity()
            res['qty'] = String(qty_val);
            }
            res["secondary_price"] = this.get_secondary_unit_price()
            res["unitPrice"] = String(this.get_secondary_unit_price())
            res["primary_qty"] = this.get_primary_quantity()
        }
        return res
    },
    set_current_uom(uom_id) {
        this.current_uom = uom_id;
    },
    get_secondary_unit_price() {
        var amount = this.prepareBaseLineForTaxesComputationExtraValues({
            quantity: this.get_current_uom().factor_inv
        })

        if (this.get_tax()) {
            var price = amount.price_unit * this.get_current_uom().factor_inv

            console.log('price', this.get_secondary_unit_tax());

            return formatCurrency(price, this.currency)
        } else {
            return amount.price_unit * this.get_current_uom().factor_inv
        }

    },

    get_secondary_unit_tax(){
        const tax_amount = this.get_all_prices(1).tax
        return tax_amount
    },

    set_quantity(quantity, keep_price) {
        var set_qty = super.set_quantity(...arguments);

        var primary_uom = this.get_product().uom_id;
        if (!this.refunded_orderline_id) {
            if (this.config.select_uom_type != 'secondary') {
                var secondary_uom = primary_uom;
                console.log('lines ', this.order_id);

                if (this.order_id.lines.includes(this)) {
                    this.is_secondary = true
                    secondary_uom = this.get_secondary_unit();
                }
            } else {
                this.is_secondary = true
                var secondary_uom = this.get_secondary_unit();
            }
            if (this.get_current_uom() == undefined) {
                this.set_current_uom(secondary_uom);
            }
            // Initialization of qty when product added
            var current_uom = this.get_current_uom() || primary_uom;

            if (current_uom == primary_uom) {
                this.set_current_uom(primary_uom);
                this.set_primary_quantity(this.get_quantity());
                var converted_qty = this.convert_qty_uom(this.qty, secondary_uom, current_uom);
                this.set_secondary_quantity(converted_qty);
            } else {
                var converted_qty = this.convert_qty_uom(this.qty, primary_uom, current_uom);
                this.set_primary_quantity(converted_qty);
                this.set_secondary_quantity(this.get_quantity());
                this.set_current_uom(secondary_uom);
            }
        }

        return set_qty
    },
    get_current_uom() {
        return this.current_uom || this.get_unit();
    },
    get_secondary_unit() {
        return this.product_id.sh_secondary_uom;
    },
    is_secondary_unit() {
        if (this.get_unit() == this.current_uom) {
            this.set_primary_uom(this.get_unit())
            return false
        } else {
            this.set_secondary_uom(this.current_uom)
            return true
        }
    },
    set_primary_uom(primary_uom) {
        this.primary_uom = primary_uom
    },
    set_secondary_uom(secondary_uom) {
        this.secondary_uom = secondary_uom
    },
    get_primary_uom() {
        return this.primary_uom
    },
    get_secondary_uom() {
        this.secondary_uom
    },
    get_all_prices(qty = this.get_quantity()) {
        if (this.is_secondary_unit()) {
            qty = this.get_primary_quantity() || qty

            return super.get_all_prices(qty)
        } else {
            return super.get_all_prices(...arguments)
        }
    },
    change_current_uom(uom_id) {
        this.current_uom = uom_id;
    },
    set_secondary_uom(uom) {
        this.secondary_uom_id = uom
    },
    convert_qty_uom(quantity, to_uom, from_uom) {
        var to_uom = to_uom;
        var from_uom = from_uom;
        var from_uom_factor = from_uom.factor;
        var amount = quantity / from_uom_factor;
        if (to_uom && to_uom.factor_inv > from_uom.factor_inv) {
            var to_uom_factor = to_uom.factor;
            amount = amount * to_uom_factor;
        }
        return amount;
    },
    set_secondary_quantity(secondary_quantity) {
        var quant = parseFloat(secondary_quantity) || 0;
        this.secondary_qty = quant;
    },
    get_secondary_qty() {
        return this.secondary_qty
    },
    set_primary_quantity(primary_quantity) {
        this.primary_qty = primary_quantity
    },
    get_primary_quantity() {
        return this.primary_qty
    }
});
