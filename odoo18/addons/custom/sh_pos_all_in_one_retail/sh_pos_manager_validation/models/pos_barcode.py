from odoo import fields, models

class Barcode(models.Model):
    _inherit = "barcode.rule"

    type = fields.Selection(
        selection_add=[("authorize", "Authorize")], ondelete={"authorize": "cascade"}
    )
