from odoo import models, fields, api


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    is_complimentary = fields.Boolean('Is Complimentary')
    expense_account = fields.Many2one('account.account', domain=[('account_type', '=', 'expense')])
