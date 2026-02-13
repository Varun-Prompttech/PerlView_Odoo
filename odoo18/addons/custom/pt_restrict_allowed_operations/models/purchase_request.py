from odoo import models,fields,api

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    @api.model
    def _default_picking_type(self):
        type_obj = self.env["stock.picking.type"]
        company_id = self.env.context.get("company_id") or self.env.company.id
        print("company_id", company_id)
        types = type_obj.search(
            [("code", "=", "incoming"), ("warehouse_id.company_id", "=", company_id)]
        )
        if not types:
            types = type_obj.search(
                [("code", "=", "incoming"), ("warehouse_id", "=", False)]
            )
        # return types[:1]
        return self.env.user.default_picking_type.id



    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Picking Type",
        required=True,
        default=_default_picking_type,
        domain=lambda self: self._get_domain_for_picking_type()

    )


    def _get_domain_for_picking_type(self):
        if self.env.user.allowed_operation_types.ids:
            return [("id", "in", self.env.user.allowed_operation_types.ids)]
        else:
            return []