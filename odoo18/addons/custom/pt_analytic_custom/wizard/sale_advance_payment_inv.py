from odoo import models, fields, api


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _create_invoices(self, sale_orders):
        invoices = super()._create_invoices(sale_orders)
        invoices.analytic_account_id = [(6, 0, sale_orders.analytic_account_id.ids)]
        return invoices
