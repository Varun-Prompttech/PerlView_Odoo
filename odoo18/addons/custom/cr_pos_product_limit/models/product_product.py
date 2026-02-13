# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ProductProduct(models.Model):
     _inherit = 'product.product'

     def pos_load_data(self, pos_session_id=False, offset=0, limit=None):
          if pos_session_id:
               response = {}
               pos_session_id = self.env['pos.session'].sudo().browse(pos_session_id)
               pos_config_id = pos_session_id.config_id

               fields = set(self._load_pos_data_fields(pos_config_id.id))
               taxes = self.env['account.tax'].search(self.env['account.tax']._check_company_domain(pos_config_id.company_id.id))
               product_fields = taxes._eval_taxes_computation_prepare_product_fields()
               fields = list(fields.union(product_fields))
               products = pos_config_id.with_context(display_default_code=False).get_products_loading_in_background(fields, offset, limit)
               self._process_pos_ui_product_product(products, pos_config_id)
               response['product.product'] = {'data': products, 'fields': fields}
               self.env['pos.session'].sudo()._load_pos_data_relations('product.product', response)
               return response
          else:
               return False