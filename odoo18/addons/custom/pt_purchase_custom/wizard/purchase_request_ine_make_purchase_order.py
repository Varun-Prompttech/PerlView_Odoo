from odoo import models, fields, api


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order'

    @api.model
    def _prepare_item(self, line):
        res = super()._prepare_item(line)
        res['category_id'] = line.category_id.id
        return res

    @api.model
    def _prepare_purchase_order_line(self, po, item):
        res = super()._prepare_purchase_order_line(po,item)
        category = item.category_id
        res['category_id'] = category.id
        return res


class PurchaseRequestLineMakePurchaseOrderItem(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order.item'

    category_id = fields.Many2one('product.category', string='Category')
