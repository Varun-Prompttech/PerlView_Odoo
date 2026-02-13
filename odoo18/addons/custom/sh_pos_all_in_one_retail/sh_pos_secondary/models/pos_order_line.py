# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models,api,fields

class POSOrderLine(models.Model):
    _inherit = 'pos.order.line'

    secondary_qty = fields.Float("Secondary Qty")
    secondary_uom_id = fields.Many2one('uom.uom', string="Secondary UOM")
    primary_qty = fields.Float("Primary Quantity")
    
    @api.model
    def _load_pos_data_fields(self, config_id):
        return super()._load_pos_data_fields(config_id) +   ['secondary_qty', 'secondary_uom_id', 'primary_qty']
    
class POSOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def sync_from_ui(self, orders):
        if orders and len(orders) > 0:
            for each_order in orders:
                lines = each_order.get('lines')
                each_order['lines'] = []
                for each_line in lines:
                    if each_line[2]['primary_qty']:
                        each_line[2]['qty'] = each_line[2]['primary_qty']
                    each_order['lines'].append(each_line)
        return super().sync_from_ui(orders)

