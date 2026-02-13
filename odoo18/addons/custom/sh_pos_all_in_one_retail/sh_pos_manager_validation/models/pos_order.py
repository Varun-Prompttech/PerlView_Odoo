# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api


class ShPosOrder(models.Model):
    _inherit = "pos.order"

    sh_backend_OTP = fields.Boolean()

    @api.model
    def _load_pos_data_fields(self, config_id):
        res = super()._load_pos_data_fields(config_id)
        return res

