# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    pos_enable_partial_payment = fields.Boolean(related='pos_config_id.enable_partial_payment',string="Allow Partial Payment", readonly=False)
    pos_sh_allow_to_pay_order = fields.Boolean(related='pos_config_id.sh_allow_to_pay_order',string="Allow To Pay Order", readonly=False)
    pos_sh_partial_pay_product_id = fields.Many2one('product.product', related='pos_config_id.sh_partial_pay_product_id', string="Partial Pay Product", readonly=False)

    @api.onchange('pos_sh_allow_to_pay_order')
    def _onchange_pos_sh_allow_to_pay_order(self):
        if self.pos_sh_allow_to_pay_order:
            product = self.env['product.product'].sudo().search([('sh_is_partial_pay_product', '=', True)], limit=1)
            if product:
                self.pos_sh_partial_pay_product_id = product.id
