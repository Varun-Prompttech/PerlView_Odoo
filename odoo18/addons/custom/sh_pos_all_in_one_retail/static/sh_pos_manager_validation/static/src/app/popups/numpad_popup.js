// /** @odoo-module */
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";
import { user } from "@web/core/user";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";


patch(NumberPopup.prototype, {
  setup() {
    super.setup(...arguments);
    this.pos = usePos();
    this.notification = useService("notification");

  },
  confirm() {
    // Check if this is a manager validation context (manager_pin has values)
    if (this.pos.manager_pin && this.pos.manager_pin.length > 0) {
      if (this.pos.manager_pin.includes(parseFloat(this.state.buffer))) {
        this.pos.submitted_validation = true;
        this.notification.add("Authenticated", { type: "success" });
        super.confirm();
      } else {
        this.pos.submitted_validation = false;
        this.notification.add("Invalid Pin!", { type: "danger" });
        // Don't call super.confirm() here to keep popup open for retry
      }
    } else {
      // Not a manager validation context, just call super
      super.confirm();
    }
  }
});