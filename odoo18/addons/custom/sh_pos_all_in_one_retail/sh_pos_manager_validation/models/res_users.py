# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models , api


class ShResUsers(models.Model):
    _inherit = "res.users"

    sh_barcode = fields.Char(string="Barcode/QR code")
    sh_password = fields.Char(string="Password ")
    sh_pin = fields.Integer(string="Pin")

    @api.model
    def _load_pos_data_fields(self, config_id):
        return super()._load_pos_data_fields(config_id) + [
            "sh_barcode",
            "sh_password",
            "sh_pin",
            "groups_id",
            "name",
        ]

    @api.model
    def _load_pos_data_domain(self, data):
            return []