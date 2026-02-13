# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class PosPayment(models.Model):
    _inherit = 'pos.payment'

    @api.constrains('amount')
    def _check_amount(self):
        for payment in self:
            if self.pos_order_id.config_id.enable_partial_payment and self.pos_order_id.config_id.sh_allow_to_pay_order:
                if payment.pos_order_id.state in ['done']:
                    raise ValidationError(_('You cannot edit a payment for a posted order.'))
            else:
                if payment.pos_order_id.state in ['invoiced', 'done']:
                    raise ValidationError(_('You cannot edit a payment for a posted order.'))

class PosConfig(models.Model):
    _inherit = 'pos.config'
    
    enable_partial_payment = fields.Boolean("Allow Partial Payment")
    sh_allow_to_pay_order = fields.Boolean(string="Allow To Pay Order")

    sh_partial_pay_product_id = fields.Many2one('product.product', string="Partial Pay Product")

    @api.onchange('sh_allow_to_pay_order')
    def _onchange_sh_allow_to_pay_order(self):
        if self.sh_allow_to_pay_order:
            product = self.env['product.product'].sudo().search([('sh_is_partial_pay_product', '=', True)], limit=1)
            if product:
                self.sh_partial_pay_product_id = product.id

    def _get_available_product_domain(self):
        res =  super()._get_available_product_domain()
        return res
