from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    analytic_account_id = fields.Many2many('account.analytic.account', string='Analytic Account',
                                           default=lambda self: self.env.user.default_analytic_account.ids)

    def action_post(self):
        res = super().action_post()
        self.move_id.analytic_account_id = [(6, 0, self.analytic_account_id.ids)]
        distribution_list = {}
        if self.move_id.analytic_account_id:
            account = self.env['account.analytic.account'].search([('id', 'in', self.move_id.analytic_account_id.ids)])
            for acc in account:
                find_account = self.env['account.analytic.account'].search([('id', '=', acc.id)])
                distribution_list[find_account.id] = 100
        for lines in self.move_id.line_ids:
            lines.analytic_distribution = distribution_list
        return res
