from odoo import models,fields,api
from odoo.tools.misc import formatLang, frozendict


class BankRecWidgetLine(models.Model):
    _inherit = "bank.rec.widget.line"

    @api.depends('source_aml_id', 'account_id', 'partner_id')
    def _compute_analytic_distribution(self):
        cache = {}
        distribution_list = {}
        if self.source_aml_move_id.analytic_account_id:
            account = self.env['account.analytic.account'].search(
                [('id', 'in', self.source_aml_move_id.analytic_account_id.ids)])
            for acc in account:
                find_account = self.env['account.analytic.account'].search([('id', '=', acc.id)])
                distribution_list[find_account.id] = 100
        for line in self:
            if line.flag in ('liquidity', 'aml'):
                line.analytic_distribution = line.source_aml_id.analytic_distribution
            elif line.flag in ('tax_line', 'early_payment'):
                line.analytic_distribution = line.analytic_distribution
            else:
                arguments = frozendict({
                    "partner_id": line.partner_id.id,
                    "partner_category_id": line.partner_id.category_id.ids,
                    "account_prefix": line.account_id.code,
                    "company_id": line.company_id.id,
                })
                if arguments not in cache:
                    cache[arguments] = self.env['account.analytic.distribution.model']._get_distribution(arguments)
                    # line.analytic_distribution = cache[arguments] or line.analytic_distribution
                    line.analytic_distribution = distribution_list
