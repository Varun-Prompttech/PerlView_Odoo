# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
     _inherit = 'res.config.settings'

     limited_products_loading = fields.Boolean(string="Limited Product Loading", related="pos_config_id.limited_products_loading", readonly=False)
     limited_product_count = fields.Integer(string="Number of Products Loaded", related="pos_config_id.limited_product_count", readonly=False)
     product_load_background = fields.Boolean(related="pos_config_id.product_load_background", readonly=False)