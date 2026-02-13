from odoo import models, fields, api,_


class Survey(models.Model):
    _inherit = 'survey.survey'

    def action_send_url(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'name': "Start Survey",
            'target': 'new',
            'url': '/survey/test/%s' % self.access_token,
        }

class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    survey_id = fields.Many2one('survey.survey', string='Quality Check', required=True, readonly=True, index=True, ondelete='cascade')

