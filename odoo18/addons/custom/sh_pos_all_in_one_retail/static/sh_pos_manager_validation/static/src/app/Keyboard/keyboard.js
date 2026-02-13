/** @odoo-module */

import { Component, xml } from "@odoo/owl";

export class OnScreenKeyBoard extends Component {
    static template = "sh_pos_manager_validation.OnScreenKeyBoard";

    setup(){
        super.setup()
    }
    clickEnter() {
        // Select the element with the class 'keyboard_frame'
        const keyboardFrame = document.querySelector('.keyboard_frame');
        
        // Set the CSS properties directly
        keyboardFrame.style.height = '0px';
        keyboardFrame.style.display = 'none';
    }
    
    shCloseKeyboard() {
        // Select the element with the class 'keyboard_frame'
        const keyboardFrame = document.querySelector('.keyboard_frame');
        
        // Set the CSS properties directly
        keyboardFrame.style.height = '0px';
        keyboardFrame.style.display = 'none';
    }
    
}
