// /** @odoo-module */
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
  async afterProcessServerData() {
    await super.afterProcessServerData(...arguments);
    let self = this;
    if(self.config.sh_pos_manager_validation){
      self.manager_pin = []
      self.manager_password = []
      self.manager_barcode = []
      for(let manager of self.config.sh_manager_ids){
        self.manager_pin.push(manager.sh_pin ? manager.sh_pin : null)
        self.manager_password.push(manager.sh_password ? manager.sh_password : null)
        self.manager_barcode.push(manager.sh_barcode ? manager.sh_barcode : null)
    }
    }
    this.submitted_validation = false;
  },
});