from odoo import models, fields, api


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        payment_vals.update({
            'analytic_account_id': [(6, 0, self.line_ids[0].move_id.analytic_account_id.ids)],
        })

        return payment_vals

    def _create_payment_vals_from_batch(self, batch_result):
        payment_vals = super()._create_payment_vals_from_batch(batch_result)
        payment_vals.update({
            'analytic_account_id': [(6, 0, self.line_ids[0].move_id.analytic_account_id.ids)],
        })
        return payment_vals
