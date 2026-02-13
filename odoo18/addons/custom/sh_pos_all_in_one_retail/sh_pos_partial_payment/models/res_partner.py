# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    not_allow_partial_payment = fields.Boolean("Not Allow Partial Payment")

    @api.model
    def _load_pos_data_fields(self, config_id):
        return super()._load_pos_data_fields(config_id) + ["not_allow_partial_payment"]
    