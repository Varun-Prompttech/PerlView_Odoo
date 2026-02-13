from odoo import fields, models, api


class HREmployee(models.Model):

    _inherit = 'hr.employee'

    assessment_ids = fields.One2many(
        'hr.assessments', 'employee_id', string='Assessments')
    assessment_template_id = fields.Many2one('assessment.parameter', string='Assessment Parameter')

    def _compute_has_officer_group(self):
        for emp in self:
            user = self.env.user
            emp.has_officer_group = user.has_group('hr.group_hr_user')

    has_officer_group = fields.Boolean(string='Has Officer Group?', compute='_compute_has_officer_group')

    def compute_count_assessments(self):
        for emp in self:
            emp.count_assessments = len(emp.assessment_ids.ids)

    count_assessments = fields.Integer(
        string='Total Assessments', compute='compute_count_assessments')

    def view_assessments(self):
        return {
            'name': 'Employee Assessment',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.assessments',
            'view_type': 'form',
            'view_mode': 'list,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        }
