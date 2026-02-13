from odoo import models, fields
from datetime import datetime

class WalkerZReport(models.TransientModel):
    _name = 'walkers.z.report'

    date_from = fields.Datetime('Date From', default=datetime.now())
    date_to = fields.Datetime('Date To', default=datetime.now())
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    config_id = fields.Many2many('pos.config', string='Point of Sale', required=True)

    def generate_z_report(self):
        self.ensure_one()
        data = {
            'date_start': self.date_from.strftime('%Y-%m-%d %H:%M:%S'),
            'date_stop': self.date_to.strftime('%Y-%m-%d %H:%M:%S'),
            'config_id': self.config_id.ids,
        }

        return {
            'wizard_id': self.id,
            'type': 'ir.actions.client',
            'tag': 'z_report_preview',
            'params': {
                'action_id': self.env.ref('pt_walkers_z_report.action_report_z').id,
                'data': data,
            }
        }

