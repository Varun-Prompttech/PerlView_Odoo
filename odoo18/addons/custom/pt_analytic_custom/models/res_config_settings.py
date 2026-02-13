from odoo import models, fields, api
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    analytic_account_id = fields.Many2many('account.analytic.distribution.model', string='Analytic Account', store=True)

    @api.model
    def get_values(self):
        """Get the values from settings."""
        res = super(ResConfigSettings, self).get_values()
        icp_sudo = self.env['ir.config_parameter'].sudo()
        analytic_account_id = icp_sudo.get_param('res.config.settings.analytic_account_id')
        res.update(
            analytic_account_id=[(6, 0, literal_eval(analytic_account_id))] if analytic_account_id else False,
        )
        return res

    def set_values(self):
        """Set the values. The new values are stored in the configuration parameters."""
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'res.config.settings.analytic_account_id',
            self.analytic_account_id.ids)
        return res
