from odoo import fields,models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    # def _apply_inventory(self):
    #     res = super()._apply_inventory()
    #     print("moves",res)
    #
    #     return res