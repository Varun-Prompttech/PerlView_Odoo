from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    default_analytic_account = fields.Many2many('account.analytic.account', string='Default Analytic Account')
