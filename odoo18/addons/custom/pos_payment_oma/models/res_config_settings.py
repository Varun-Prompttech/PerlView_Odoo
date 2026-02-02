# -*- coding: utf-8 -*-
"""
OMA Integration Settings
"""

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    # No additional fields - OMA is available as a payment terminal option
