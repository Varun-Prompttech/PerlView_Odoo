from odoo import models,fields,api

class ResUsers(models.Model):
    _inherit = 'res.users'

    allowed_operation_types = fields.Many2many('stock.picking.type',string = 'Allowed Operation Types')
    default_picking_type = fields.Many2one('stock.picking.type', string = 'Default Picking Type', domain = "[('id','in', allowed_operation_types)]")