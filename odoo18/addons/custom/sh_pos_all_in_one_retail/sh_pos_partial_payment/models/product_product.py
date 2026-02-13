# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    sh_is_partial_pay_product = fields.Boolean('Partial Pay Product')

    @api.model
    def _load_pos_data_fields(self, config_id):
          return super()._load_pos_data_fields(config_id) + ['sh_is_partial_pay_product']
