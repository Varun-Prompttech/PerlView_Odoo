/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";
import { passwordPopup } from "@sh_pos_all_in_one_retail/static/sh_pos_manager_validation/app/popups/password_popup/password_popup";
import { BarcodePopup } from "@sh_pos_all_in_one_retail/static/sh_pos_manager_validation/app/popups/barcode_popup/barcode_popup";

export class ShValidationTypePopup extends Component {
  static template = "sh_pos_manager_validation.ShValidationTypePopup";
  static components = { Dialog };
  setup() {
    super.setup();
    this.pos = usePos();
    this.dialog = useService("dialog");
  }

  async open_barcodePopup() {
    console.log("barcode");
    await makeAwaitable(this.dialog, BarcodePopup, {
      title: "Barcode",
    });
    this.props.close();
  }

  async open_passwordPopup() {
    console.log("password");
    await makeAwaitable(this.dialog, passwordPopup, {
      title: "Password",
    });
    this.props.close();
  }

  async open_pin_numberPopup() {
    console.log("pin");
    await makeAwaitable(this.dialog, NumberPopup, {
      title: "Pin",
    });
    this.props.close();
  }

  cancel() {
    this.pos.submitted_validation = false;
    this.props.close();
  }
}
