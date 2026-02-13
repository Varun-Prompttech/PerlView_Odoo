from odoo import models,fields,api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('partner_id')
    def onchange_without_tax_partner_id(self):
        without_tax = self.partner_id.without_tax
        purchase_taxes = self.partner_id.purchase_taxes_id
        if purchase_taxes:
            if without_tax:
                for line in self.order_line:
                    line.taxes_id = None
            else:
                for line in self.order_line:
                    line.taxes_id = purchase_taxes.ids
        else:
            for line in self.order_line:
                line = line.with_company(line.company_id)
                fpos = line.order_id.fiscal_position_id or line.order_id.fiscal_position_id._get_fiscal_position(
                    line.order_id.partner_id)
                # filter taxes by company
                taxes = line.product_id.supplier_taxes_id._filter_taxes_by_company(line.company_id)
                line.taxes_id = fpos.map_tax(taxes)



class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    category_id = fields.Many2one('product.category', string='Category')
    unitprice_vat = fields.Monetary(compute="_compute_unitprice_vat", readonly=True)
    average_cost = fields.Monetary(compute="_compute_unitprice_vat", readonly=True)

    def _compute_tax_id(self):
        res = super()._compute_tax_id()
        for line in self:
            partner = line.order_id.partner_id
            line.taxes_id = None if partner.without_tax else partner.purchase_taxes_id.ids
        return res

    @api.depends('price_unit')
    def _compute_unitprice_vat(self):
        for line in self:
            line.unitprice_vat = line.price_unit + line.price_unit * 0.05
            line.average_cost = line.product_id.standard_price if line.product_id else 0
