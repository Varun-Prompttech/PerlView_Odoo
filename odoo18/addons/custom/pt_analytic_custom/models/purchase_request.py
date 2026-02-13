from odoo import models, fields, api
from odoo.exceptions import UserError


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    analytic_account_id = fields.Many2many('account.analytic.account', string='Analytic Account',
                                           default=lambda self: self.env.user.default_analytic_account.ids)

    @api.onchange('analytic_account_id')
    def onchange_analytic_account_id(self):
        distribution_list = {}
        if self.analytic_account_id:
            account = self.env['account.analytic.account'].search([('id', 'in', self.analytic_account_id.ids)])
            for acc in account:
                find_account = self.env['account.analytic.account'].search([('id', '=', acc.id)])
                distribution_list[find_account.id] = 100
        for lines in self.line_ids:
            lines.analytic_distribution = distribution_list


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    @api.onchange('product_id')
    def onchange_product_template_id(self):
        if not self.request_id.analytic_account_id:
            raise UserError(
                "Analytic Account missing.")
        account = None
        distribution_list = {}
        if self.request_id.analytic_account_id:
            account = self.env['account.analytic.account'].search(
                [('id', 'in', self.request_id.analytic_account_id.ids)])
            for acc in account:
                find_account = self.env['account.analytic.account'].search([('id', '=', acc.id)])
                distribution_list[find_account.id] = 100
        for lines in self:
            lines.analytic_distribution = distribution_list
