from odoo import models,fields,api
from collections import defaultdict


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def onchange_without_tax_partner_id(self):
        without_tax = self.partner_id.without_tax
        if without_tax:
            for line in self.order_line:
                line.tax_id = None
        else:
            lines_by_company = defaultdict(lambda: self.env['sale.order.line'])
            cached_taxes = {}
            for line in self.order_line:
                if line.product_type == 'combo':
                    line.tax_id = False
                    continue
                lines_by_company[line.company_id] += line
            for company, lines in lines_by_company.items():
                for line in lines.with_company(company):
                    taxes = None
                    if line.product_id:
                        taxes = line.product_id.taxes_id._filter_taxes_by_company(company)
                    if not line.product_id or not taxes:
                        # Nothing to map
                        line.tax_id = False
                        continue
                    fiscal_position = line.order_id.fiscal_position_id
                    cache_key = (fiscal_position.id, company.id, tuple(taxes.ids))
                    cache_key += line._get_custom_compute_tax_cache_key()
                    if cache_key in cached_taxes:
                        result = cached_taxes[cache_key]
                    else:
                        result = fiscal_position.map_tax(taxes)
                        cached_taxes[cache_key] = result
                    # If company_id is set, always filter taxes by the company
                    line.tax_id = result


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id', 'company_id')
    def _compute_tax_id(self):
        res = super()._compute_tax_id()
        for line in self:
            without_tax = line.order_id.partner_id.without_tax
            if without_tax:
                line.tax_id = None
        return res







