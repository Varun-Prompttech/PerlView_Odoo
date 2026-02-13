# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models


class ShPosConfig(models.Model):
    _inherit = "pos.config"

    sh_pos_manager_validation = fields.Boolean(
        string="Validate and authenticate pos manager"
    )
    sh_manager_ids = fields.Many2many(
        "res.users", string="Manager", domain="[('share', '=', False)]"
    )
    sh_one_time_password = fields.Boolean(
        string="Only one time password this take whatever functionally firstly called its show password and not ask again."
    )
    sh_order_line_delete_pw = fields.Boolean(string=" Delete order line")
    sh_order_delete_pw = fields.Boolean(string="Delete order")
    sh_discount_pw = fields.Boolean(string="Discount validation")
    sh_price_pw = fields.Boolean(string="Price validation")
    sh_qty_pw = fields.Boolean(string="On Decrease Quantity")
    sh_payment_pw = fields.Boolean(string="Payment validation")
    sh_refund_pw = fields.Boolean(string="Order refund validation")
    sh_validation_type = fields.Selection(
        string="Validation Type",
        selection=[
            ("all", "All"),
            ("barcode", "Only Barcode"),
            ("password", "Only Password"),
            ("pin", "Only Pin"),
            ("pin_password", "PIN and Password"),
            ("pin_barcode", "PIN and Barcode"),
            ("password_barcode", "Password and Barcode"),
        ],
    )
    sh_validation_on_payment_method = fields.Boolean(
        string="Validation On Payment Methods"
    )
    sh_select_method_ids = fields.Many2many(
        "pos.payment.method", "name", string="Type of Payment"
    )
    sh_cash_move_validation = fields.Boolean(
        string="Add validation on cash out or cash in "
    )
    sh_virtual_keyboard = fields.Boolean(string="Open Virtual Keyboard")
