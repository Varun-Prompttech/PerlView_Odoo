from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _default_picking_type(self):
        return self.env.user.default_picking_type.id if self.env.user.default_picking_type else False

    picking_type_id = fields.Many2one(
        'stock.picking.type',
        'Operation Type',
        required=True,
        index=True,
        default=_default_picking_type,
        domain=lambda self: self._get_domain_for_picking_type(),
        help="This will determine operation type of the picking.",
    )

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

    # @api.onchange('picking_type_id')
    # def _onchange_picking_type_domain(self):
    #     """Set domain dynamically for picking type based on user permissions."""
    #     if self.env.user.allowed_operation_types:
    #         return {
    #             'domain': {
    #                 'picking_type_id': [('id', 'in', self.env.user.allowed_operation_types.ids)],
    #             }
    #         }
    #     else:
    #         return {
    #             'domain': {
    #                 'picking_type_id': [],
    #             }
    #         }




# from odoo import models,fields,api
#
# class StockPicking(models.Model):
#     _inherit = "stock.picking"
#
#     @api.model
#     def _default_picking_type(self):
#         x = self.env.user.default_picking_type.id if self.env.user.default_picking_type else False
#         # return self._get_picking_type(self.env.context.get('company_id') or self.env.company.id)
#         print('1111111111111')
#         return x
#
#     # picking_type_id = fields.Many2one('stock.picking.type', 'Deliver Tos', required=True, default=_default_picking_type,
#     #                                   domain=lambda self: self._get_domain_for_picking_type(),
#     #                                   help="This will determine operation type of incoming shipment")
#
#     picking_type_id = fields.Many2one(
#         'stock.picking.type', 'Operation Type',
#         required=True, index=True,
#         default=_default_picking_type,
#         domain=lambda self: self._get_domain_for_picking_type())
#
#
#     def _get_domain_for_picking_type(self):
#         if self.env.user.allowed_operation_types:
#             print('222222222222222')
#             return [("id", "in", self.env.user.allowed_operation_types.ids)]
#         else:
#             return []
#
#     @api.onchange('company_id')
#     def _onchange_company_picking_type(self):
#         """Ensure picking type updates when the company changes."""
#         if self.env.user.default_picking_type:
#             print('333333333333333333')
#             self.picking_type_id = self.env.user.default_picking_type.id