/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Dialog } from "@web/core/dialog/dialog";
import { Component, useState } from "@odoo/owl";
import { useBarcodeReader } from "@point_of_sale/app/barcode/barcode_reader_hook";
import { user } from "@web/core/user";

export class BarcodePopup extends Component {
  static template = "sh_pos_manager_validation.BarcodePopup";
  static components = { Dialog };

  setup() {
    super.setup();
    this.pos = usePos();
    this.notification = useService("notification");
    useBarcodeReader({
      authorize: this.sh_authorize,
    });
  }

  async sh_authorize(code) {
    if (code.type == "authorize" && this.pos.manager_barcode.includes(code.base_code)) {
      this.pos.submitted_validation = true;
      await this.notification.add("Authenticated", { type: "success" });
      this.props.close();
    } else {
      this.pos.submitted_validation = false;
      await this.notification.add("Invalid Barcode!", { type: "danger" });
    }
  }

  cancel() {
    this.pos.submitted_validation = false;
    this.props.close();
  }

}
