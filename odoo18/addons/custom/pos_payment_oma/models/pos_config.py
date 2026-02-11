# -*- coding: utf-8 -*-
"""
POS Config extension to add thermal receipt printer name.
"""

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    thermal_printer_name = fields.Char(
        string='Thermal Printer Name',
        default='POS-80',
        help='CUPS printer name for the thermal receipt printer (e.g., POS-80). '
             'Run "lpstat -p" on the server to see available printers.'
    )
