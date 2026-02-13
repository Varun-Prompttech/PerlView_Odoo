from odoo import models, fields, api
from odoo.tools import frozendict, format_date, float_compare, format_list, Query
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    analytic_account_id = fields.Many2many('account.analytic.account', string='Analytic Account',
                                           default=lambda self: self.env.user.default_analytic_account.ids)
    analytic_split = fields.Boolean('Analytic Split')

    @api.depends('journal_id')
    def _compute_default_analytic_account(self):
        for record in self:
            if record.journal_id and record.journal_id.code == 'POSS':
                record.analytic_account_id = [(6, 0, [])]

    @api.onchange('analytic_account_id')
    def onchange_analytic_account_id(self):
        distribution_list = {}
        if self.analytic_account_id:
            if self.analytic_split:
                count = len(self.analytic_account_id)
                percent = 100 / count
                account = self.env['account.analytic.account'].search([('id', 'in', self.analytic_account_id.ids)])
                total = 0
                for acc in account:
                    total += float('%.2f' % percent)
                    find_account = self.env['account.analytic.account'].search([('id', '=', acc.id)])
                    distribution_list[find_account.id] = percent
                diff = 100 - total
                last_key = list(distribution_list.keys())[-1]
                distribution_list[last_key] += diff

            else:
                account = self.env['account.analytic.account'].search([('id', 'in', self.analytic_account_id.ids)])
                for acc in account:
                    find_account = self.env['account.analytic.account'].search([('id', '=', acc.id)])
                    distribution_list[find_account.id] = 100
        for lines in self.invoice_line_ids:
            lines.analytic_distribution = distribution_list
        for line in self.line_ids:
            line.analytic_distribution = distribution_list

    @api.onchange('analytic_split')
    def onchange_analytic_split(self):
        distribution_list = {}
        if self.analytic_account_id:
            if self.analytic_split:
                count = len(self.analytic_account_id)
                percent = 100 / count
                account = self.env['account.analytic.account'].search([('id', 'in', self.analytic_account_id.ids)])
                total = 0
                for acc in account:
                    total += float('%.2f' % percent)
                    find_account = self.env['account.analytic.account'].search([('id', '=', acc.id)])
                    distribution_list[find_account.id] = percent
                diff = 100 - total
                last_key = list(distribution_list.keys())[-1]
                distribution_list[last_key] += diff

            else:
                account = self.env['account.analytic.account'].search([('id', 'in', self.analytic_account_id.ids)])
                for acc in account:
                    find_account = self.env['account.analytic.account'].search([('id', '=', acc.id)])
                    distribution_list[find_account.id] = 100
        for lines in self.invoice_line_ids:
            lines.analytic_distribution = distribution_list
        for line in self.line_ids:
            line.analytic_distribution = distribution_list

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends('account_id', 'partner_id', 'product_id')
    def _compute_analytic_distribution(self):
        cache = {}
        for line in self:
            if line.display_type == 'product' or not line.move_id.is_invoice(include_receipts=True):
                arguments = frozendict({
                    "product_id": line.product_id.id,
                    "product_categ_id": line.product_id.categ_id.id,
                    "partner_id": line.partner_id.id,
                    "partner_category_id": line.partner_id.category_id.ids,
                    "account_prefix": line.account_id.code,
                    "company_id": line.company_id.id,
                })
                if arguments not in cache:
                    cache[arguments] = self.env['account.analytic.distribution.model']._get_distribution(arguments)
                if line.journal_id.code == 'POSS':
                    line.analytic_distribution = cache[arguments] or line.analytic_distribution

    @api.onchange('product_id', 'account_id')
    def onchange_product_template_id(self):
        # if not self.move_id.analytic_account_id:
        # raise UserError(
        #     "Analytic Account missing.")
        account = None
        distribution_list = {}
        if self.move_id.analytic_account_id:
            if self.move_id.analytic_split:
                count = len(self.move_id.analytic_account_id)
                percent = 100 / count
                account = self.env['account.analytic.account'].search([('id', 'in', self.move_id.analytic_account_id.ids)])
                total = 0
                for acc in account:
                    total += float('%.2f' % percent)
                    find_account = self.env['account.analytic.account'].search([('id', '=', acc.id)])
                    distribution_list[find_account.id] = percent
                diff = 100 - total
                last_key = list(distribution_list.keys())[-1]
                distribution_list[last_key] += diff
            else:
                account = self.env['account.analytic.account'].search(
                    [('id', 'in', self.move_id.analytic_account_id.ids)])
                for acc in account:
                    find_account = self.env['account.analytic.account'].search([('id', '=', acc.id)])
                    distribution_list[find_account.id] = 100
        for lines in self:
            lines.analytic_distribution = distribution_list


