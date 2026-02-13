/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { reactive } from "@odoo/owl";
import { ProductConfiguratorPopup } from "@point_of_sale/app/store/product_configurator_popup/product_configurator_popup"
import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";
import { ProductInfoPopup } from "@point_of_sale/app/screens/product_screen/product_info_popup/product_info_popup";

ProductConfiguratorPopup.components["ProductCard"] = ProductCard
patch(ProductConfiguratorPopup.prototype, { 
    get getAlternativeProduct(){        
        return this.props.product.sh_alternative_products || []
    },
    get getVarientProduct() {
        const allProducts = posmodel.models["product.product"].getAll().filter(product =>
            product.sh_product_tmpl_id === this.props.product.sh_product_tmpl_id
        );    
        return allProducts.filter(product => 
            product.attribute_line_ids?.every(attributeLine => 
                attributeLine.attribute_id.display_type === 'radio'
            )
        );
    },   
    async onProductInfoClick(product) {
        const info = await reactive(posmodel).getProductInfo(product, 1);
        posmodel.env.services.dialog.add(ProductInfoPopup, { info: info, product: product });
    },
    async addProductToOrder(product) {
        await reactive(posmodel).addLineToCurrentOrder({ product_id: product }, {} , false);
        if(posmodel.config.sh_close_popup_after_single_selection){
            this.close()
        }
    },
})
