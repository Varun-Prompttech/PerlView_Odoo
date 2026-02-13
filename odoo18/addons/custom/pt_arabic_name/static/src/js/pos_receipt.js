/** @odoo-module */
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";
import { useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

patch(PosOrder.prototype, {
       setup(){
       super.setup(...arguments);
       },
       export_for_printing(baseUrl, headerData) {
           const result = super.export_for_printing(...arguments);
          result.count = this.lines.length
          this.receipt = result.count
          var sum = 0;
          if (result) {
            result.label_total = _t("TOTAL / اﻹجمالي");
            result.label_rounding = _t("Rounding / التقريب");
            result.label_change = _t("CHANGE / الباقي");
            result.label_discounts = _t("Discounts / الخصومات");
            }
          this.lines.forEach(function(t) {
                    sum += t.qty;
                })
                result.sum = sum
                return result;

       },
});