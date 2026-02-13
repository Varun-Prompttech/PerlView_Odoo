from odoo import models, fields, api


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _get_combine_receivable_vals(self, payment_method, amount, amount_converted):
        partial_vals = super()._get_combine_receivable_vals(payment_method, amount, amount_converted)
        complimentary_account = self.env['pos.payment.method'].search([('is_complimentary', '=', True)])

        if 'Complimentary Sales' in partial_vals['name']:
            partial_vals['account_id'] = complimentary_account.expense_account.id

        return partial_vals
