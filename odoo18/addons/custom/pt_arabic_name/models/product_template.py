# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    arabic_name = fields.Char(string="Arabic Name")

class ProductProduct(models.Model):
    _inherit = "product.product"

    arabic_name = fields.Char(
        string="Arabic Name",
        compute="_compute_arabic_name",  #Compute instead of related
        store=True  # Store in DB for performance
    )

    @api.depends("product_tmpl_id.arabic_name")
    def _compute_arabic_name(self):
        """Compute arabic_name from product.template"""
        for product in self:
            product.arabic_name = product.product_tmpl_id.arabic_name or " "
            _logger.info("Computed Arabic Name: %s -> %s", product.display_name, product.arabic_name)

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        fields += ['arabic_name']
        return fields


