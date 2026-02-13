from odoo import models,fields,api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _default_picking_type(self):
        x = self.env.user.default_picking_type.id if self.env.user.default_picking_type else False
        # return self._get_picking_type(self.env.context.get('company_id') or self.env.company.id)
        return x

    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver Tos', required=True,default=_default_picking_type,
                                      domain=lambda self: self._get_domain_for_picking_type(),
                                      help="This will determine operation type of incoming shipment")


    def _get_domain_for_picking_type(self):
        if self.env.user.allowed_operation_types:
            return [("id", "in", self.env.user.allowed_operation_types.ids)]
        else:
            return []

    @api.onchange('company_id')
    def _onchange_company_picking_type(self):
        """Ensure picking type updates when the company changes."""
        if self.env.user.default_picking_type:
            self.picking_type_id = self.env.user.default_picking_type.id