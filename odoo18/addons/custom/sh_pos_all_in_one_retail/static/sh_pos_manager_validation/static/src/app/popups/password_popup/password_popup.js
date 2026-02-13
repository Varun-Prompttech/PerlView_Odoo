/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { OnScreenKeyBoard } from "@sh_pos_all_in_one_retail/static/sh_pos_manager_validation/app/Keyboard/keyboard";
import { Dialog } from "@web/core/dialog/dialog";
import { Component, useState, onMounted } from "@odoo/owl";
import { user } from "@web/core/user";
import { useService } from "@web/core/utils/hooks";


export class passwordPopup extends Component {
  static template = "sh_pos_manager_validation.passwordPopup";
  static components = { Dialog , OnScreenKeyBoard };

  setup() {
    super.setup();
    this.pos = usePos();
    this.state = useState({
      input_password: "",
    });
    this.notification = useService("notification");
    onMounted(this.onMounted);

  }

  async confirm() {    
    if (this.pos.manager_password.includes(this.state.input_password)) {
        this.pos.submitted_validation = true;
        this.notification.add("Authenticated", { type: "success" });
        this.props.close();
    } else {
      this.pos.submitted_validation = false;
      this.notification.add("Invalid Password!", { type: "danger" });
    }
  }

  onMounted() {
    document.getElementById('password').focus();
    const self = this;
    
    const numlockElement = document.querySelector('.numlock');
    if (numlockElement) {
        numlockElement.addEventListener('click', function () {
            self.toggleNumLock();
            return false;
        });
    }
}
toggleNumLock() {
  document.querySelectorAll('.symbol span').forEach(span => {
      span.classList.toggle('off');
      span.classList.toggle('on');
  });
  this.numlock = (this.numlock === true ) ? false : true;

}


  open_keyboard(){
    if(this.pos.config.sh_virtual_keyboard){
      
      var self = this;
      // Get the keyboard_frame element and set the style
      const keyboardFrame = document.querySelector('.keyboard_frame');
      keyboardFrame.style.height = '230px';
      keyboardFrame.style.width = '100vw';
      keyboardFrame.style.display = 'block';

      const virtualKeyboard = document.querySelector('.keyboard');
      const inputField = document.getElementById('password');

      virtualKeyboard.onclick = function(event) {
        inputField.focus();
        
        const key = event.target;        
        // Check if the clicked element has the class 'space'
        if (key.classList.contains('space')) {
          inputField.value += ' ';
        }

        // Handle symbols or letters inside the virtual keyboard
        if (event.target.matches('li.symbol')) {          
          const offValue = key.querySelector('.off').textContent;
          const onValue = key.querySelector('.on').textContent;
          console.log("self.numlock",self.numlock);
          console.log("offValue",offValue);
          console.log("onValue",onValue);
          
          
          if (self.numlock){
              inputField.value += offValue;
          } else {
              inputField.value += offValue;
          }
          
          inputField.focus();
        } 
        
        // Handle delete key
        else if (event.target.matches('li.delete')) {
          inputField.value = inputField.value.slice(0, -1);
        }
      };
    }
}


  cancel() {
    this.pos.submitted_validation = false;
    this.props.close();
  }
}
