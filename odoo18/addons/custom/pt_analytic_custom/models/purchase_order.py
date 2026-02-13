from odoo import models, fields, api
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

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
        for lines in self.order_line:
            lines.analytic_distribution = distribution_list

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals.update({
            'analytic_account_id': [(6, 0, self.analytic_account_id.ids)],
        })
        return invoice_vals


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('product_id', 'order_id.partner_id')
    def _compute_analytic_distribution(self):
        for line in self:
            if not line.display_type:
                distribution = self.env['account.analytic.distribution.model']._get_distribution({
                    "product_id": line.product_id.id,
                    "product_categ_id": line.product_id.categ_id.id,
                    "partner_id": line.order_id.partner_id.id,
                    "partner_category_id": line.order_id.partner_id.category_id.ids,
                    "company_id": line.company_id.id,
                })
                # line.analytic_distribution = distribution or line.analytic_distribution

    @api.onchange('product_id')
    def onchange_product_template_id(self):
        if not self.order_id.analytic_account_id:
            raise UserError(
                "Analytic Account missing.")
        account = None
        distribution_list = {}
        if self.order_id.analytic_account_id:
            account = self.env['account.analytic.account'].search(
                [('id', 'in', self.order_id.analytic_account_id.ids)])
            for acc in account:
                find_account = self.env['account.analytic.account'].search([('id', '=', acc.id)])
                distribution_list[find_account.id] = 100
        for lines in self:
            lines.analytic_distribution = distribution_list
