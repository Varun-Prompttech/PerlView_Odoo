# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models,api

class ShProductProdct(models.Model):
    _inherit = 'product.product'
   
    
    @api.model
    def _load_pos_data_fields(self, config_id):
        return super()._load_pos_data_fields(config_id) +   ['sh_secondary_uom', 'sh_is_secondary_unit']