from odoo import models,fields,api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    without_tax = fields.Boolean('Tax Exempt')
    purchase_taxes_id = fields.Many2many('account.tax', 'partner_purchase_tax_id', 'partner_tax_id', 'tax_id',
                                         string="Purchase Taxes",
                                         help="Default taxes used when buying the product",
                                         domain=[('type_tax_use', '=', 'purchase')])


    def open_customer_statement(self):
        pass