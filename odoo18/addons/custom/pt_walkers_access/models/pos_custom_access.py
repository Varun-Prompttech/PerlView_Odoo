# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api


class InheritPosPayment(models.Model):
    _inherit = 'pos.payment'

    user_check_pos = fields.Boolean(compute="_compute_user_check_pos", store=False)

    @api.depends()
    def _compute_user_check_pos(self):
        for record in self:
            # If the logged-in user is in the 'access pos payment method change' group, set user_check to True
            record.user_check_pos =  self.env.user.has_group('pt_walkers_access.group_pos_payment_manager')

class InheritResUsers(models.Model):
    _inherit = 'res.users'

    max_discount_percentage = fields.Float(string="Max Discount (%)")

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        fields += ['max_discount_percentage']
        return fields

