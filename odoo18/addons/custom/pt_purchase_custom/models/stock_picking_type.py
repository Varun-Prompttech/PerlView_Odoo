from odoo import fields,models

class StockingPickingType(models.Model):
    _inherit = 'stock.picking.type'

    return_bill = fields.Boolean('Return')
