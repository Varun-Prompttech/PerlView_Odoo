// /** @odoo-module */
import { patch } from "@web/core/utils/patch";

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { PosOrder } from "@point_of_sale/app/models/pos_order";

import { ShValidationTypePopup } from "@sh_pos_all_in_one_retail/static/sh_pos_manager_validation/app/popups/validation_type_popup/validation_type_popup";

import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";

patch(PosStore.prototype, {
  
  // For Payment validation boolean.
  async pay() {
    console.log(this.get_order().OTP);

    if (this.config.sh_payment_pw) {
      if (!this.get_order().OTP) {
        await makeAwaitable(this.dialog, ShValidationTypePopup, {
          title: "Select validation method",
        });
        if (this.submitted_validation) {
          this.submitted_validation = false;
          if (this.config.sh_one_time_password) {
            this.get_order().OTP = true;
          }
          await super.pay();
        }
      } else {
        await super.pay();
      }
    } else {
      await super.pay();
    }
  },

  // For Order Deletion boolean
  async onDeleteOrder(order) {
    if (this.config.sh_order_delete_pw) {
      if (!this.get_order().OTP) {
        await makeAwaitable(this.dialog, ShValidationTypePopup, {
          title: "Select validation method",
        });
        if (this.submitted_validation) {
          this.submitted_validation = false;
          if (this.config.sh_one_time_password) {
            this.get_order().OTP = true;
          }
          await super.onDeleteOrder(order);
        }
      } else {
        await super.onDeleteOrder(order);
      }
    } else {
      await super.onDeleteOrder(order);
    }
  },

  // For Cash In Cash Out boolean
  async cashMove() {
    if (this.config.sh_cash_move_validation) {
      if (!this.get_order().OTP) {
        await makeAwaitable(this.dialog, ShValidationTypePopup, {
          title: "Select validation method",
        });
        if (this.submitted_validation) {
          this.submitted_validation = false;
          if (this.config.sh_one_time_password) {
            this.get_order().OTP = true;
          }
          await super.cashMove();
        }
      } else {
        await super.cashMove();
      }
    } else {
      await super.cashMove();
    }
  },
});

// For Order refund validation
patch(ControlButtons.prototype, {
  async clickRefund() {
    if (this.pos.config.sh_refund_pw) {
      if (!this.pos.get_order().OTP) {
        await makeAwaitable(this.dialog, ShValidationTypePopup, {
          title: "Select validation method",
        });
        if (this.pos.submitted_validation) {
          this.pos.submitted_validation = false;
          if (this.pos.config.sh_one_time_password) {
            this.pos.get_order().OTP = true;
          }
          await super.clickRefund();
        }
      } else {
        await super.clickRefund();
      }
    } else {
      await super.clickRefund();
    }
  },
});

// For discount , price , qty boolean
patch(ProductScreen.prototype, {
  // prevent : when we increase quantity from tapping on product card in product screen
  // async addProductToOrder(product) {
  //   if (this.pos.config.sh_qty_pw) {
  //     if (!this.pos.get_order().OTP) {
  //       var existing = this.pos.models["pos.order.line"].getAll();
  //       var exist = false;
  //       for (let i = 0; i < existing.length; i++) {
  //         let element = existing[i];
  //         if (element.product_id.id == product.id) {
  //           exist = true;
  //           break;
  //         } else {
  //           exist = false;
  //         }
  //       }
  //       if (exist) {
  //         await makeAwaitable(this.dialog, ShValidationTypePopup, {
  //           title: "Select validation method",
  //         });
  //         if (this.pos.submitted_validation) {
  //           this.pos.submitted_validation = false;
  //           if (this.pos.config.sh_one_time_password) {
  //             this.pos.get_order().OTP = true;
  //           }
  //           await super.addProductToOrder(product);
  //         }
  //       } else {
  //         await super.addProductToOrder(product);
  //       }
  //     } else {
  //       await super.addNewPaymentLine(product);
  //     }
  //   } else {
  //     await super.addProductToOrder(product);
  //   }
  // },

  async onNumpadClick(buttonValue) {
    console.log("buttonValue : ", buttonValue);
    console.log(this.pos.submitted_validation);

    if (["quantity", "discount", "price"].includes(buttonValue)) {
      // discount boolean
      if (this.pos.config.sh_discount_pw && buttonValue == "discount") {
        console.log("discount called");
        if (!this.pos.get_order().OTP) {
          await makeAwaitable(this.dialog, ShValidationTypePopup, {
            title: "Select validation method",
          });
          if (this.pos.submitted_validation) {
            this.pos.submitted_validation = false;
            if (this.pos.config.sh_one_time_password) {
              this.pos.get_order().OTP = true;
            }
            await super.onNumpadClick(buttonValue);
          } else {
            return false;
          }
        } else {
          await super.onNumpadClick(buttonValue);
        }
      }
      // price boolean
      else if (this.pos.config.sh_price_pw && buttonValue == "price") {
        console.log("price called");
        if (!this.pos.get_order().OTP) {
          await makeAwaitable(this.dialog, ShValidationTypePopup, {
            title: "Select validation method",
          });
          if (this.pos.submitted_validation) {
            this.pos.submitted_validation = false;
            if (this.pos.config.sh_one_time_password) {
              this.pos.get_order().OTP = true;
            }
            await super.onNumpadClick(buttonValue);
          } else {
            return false;
          }
        } else {
          await super.onNumpadClick(buttonValue);
        }
      }

      // qty boolean : not workable when click on numpad & not add code for OTP
      // else if (this.pos.config.sh_qty_pw && buttonValue == "quantity") {
      //   console.log("qty called");
      //   this.pos.get_order().get_selected_orderline()
      //   if (!this.pos.get_order().OTP) {
      //     await makeAwaitable(this.dialog, ShValidationTypePopup, {
      //       title: "Select validation method",
      //     });
      //     if (this.pos.submitted_validation) {
      //       this.pos.submitted_validation = false;
      //       if (this.pos.config.sh_one_time_password) {
      //         this.pos.get_order().OTP = true;
      //       }
      //       await super.onNumpadClick(buttonValue);
      //       this.pos.submitted_validation = false;
      //     } else {
      //       return false;
      //     }
      //   } else {
      //     await super.onNumpadClick(buttonValue);
      //   }
      // } 
      else {
        await super.onNumpadClick(buttonValue);
      }
    }

    // Order line deletion
    if (this.pos.config.sh_order_line_delete_pw && buttonValue == "Backspace") {
      if (!this.pos.get_order().OTP) {
        let qty_of_selected = this.pos.get_order().get_selected_orderline().qty;
        console.log(qty_of_selected, this.pos.submitted_validation);
        if (qty_of_selected == 0) {
          await makeAwaitable(this.dialog, ShValidationTypePopup, {
            title: "Select validation method",
          });
          if (this.pos.submitted_validation) {
            this.pos.submitted_validation = false;
            if (this.pos.config.sh_one_time_password) {
              this.pos.get_order().OTP = true;
            }
            await super.onNumpadClick(buttonValue);
            this.pos.submitted_validation = false;
          } else {
            return false;
          }
        } else {
          await super.onNumpadClick(buttonValue);
        }
      } else {
        await super.onNumpadClick(buttonValue);
      }
    } else {
      this.numberBuffer.sendKey(buttonValue);
    }
  },
});

// payment line validation boolean
patch(PaymentScreen.prototype, {
  async addNewPaymentLine(paymentMethod) {
    if (this.pos.config.sh_select_method_ids) {
      if (!this.pos.get_order().OTP) {

        // code that check selected backend line with tapped line 
        let is_method_present = this.pos.config.sh_select_method_ids.some(
          (element) => {
            console.log("backend lines", paymentMethod.id, paymentMethod.name);
            if (element.id === paymentMethod.id) {
              console.log("current selected line : ", element.id, element.name);
              console.log(
                "matched with backend lines",
                paymentMethod.id,
                paymentMethod.name
              );
              return true;
            }
            return false;
          }
        );

        // check if tapped line match with backend open popup
        if (is_method_present) {
          await makeAwaitable(this.dialog, ShValidationTypePopup, {
            title: "Select validation method",
          });
          if (this.pos.submitted_validation) {
            this.pos.submitted_validation = false;
            if (this.pos.config.sh_one_time_password) {
              this.pos.get_order().OTP = true;
            }
            await super.addNewPaymentLine(paymentMethod);
            this.pos.submitted_validation = false;
          }
          return;
        }
      }
    }
    await super.addNewPaymentLine(paymentMethod);
  },
});

patch(PosOrder.prototype, {
  async setup(vals) {
    await super.setup(...arguments);
    // when we reload site OTP variable become false
    // OTP must not be false after realod the site
    this.OTP = false;
  },
});
