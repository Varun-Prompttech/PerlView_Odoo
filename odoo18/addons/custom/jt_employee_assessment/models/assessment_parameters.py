from odoo import fields, models, api, _


class EmployeeParameter(models.Model):
    _name = 'assessment.parameter'
    _description = 'Employee Assessment Parameters'
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
    ]

    name = fields.Char(string='Assessment Name')

    assessment_parameter_line_ids = fields.One2many(
        'assessment.parameter.line', 'assessment_parameter_id', string='Assessment Lines', copy=False)

    _sql_constraints = [
        ('constrains_rating_label', 'unique(name)', 'Rating Label already exists!!')]


class EmployeeParameterLine(models.Model):
    _name = 'assessment.parameter.line'
    _description = 'Employee Assessment Parameters Line'

    name = fields.Text(string="Description")
    assessment_parameter_id = fields.Many2one('assessment.parameter', string='Assessment')
    parameter_id = fields.Char(string='Parameter Name')
    is_true = fields.Boolean(string='True')
    is_false = fields.Boolean(string='False')
    display_type = fields.Selection(
        [("line_section", "Section"), ("line_note", "Note")],
        default=False,
        help="Technical field for UX purpose.",
    )

    @api.model
    def create(self, vals_list):
        if vals_list.get('display_type'):
            vals_list.update(parameter_id=False)
        return super().create(vals_list)

    @api.onchange('is_true')
    def _onchange_is_true(self):
        if self.is_true:
            self.is_false = False

    @api.onchange('is_false')
    def _onchange_is_false(self):
        if self.is_false:
            self.is_true = False
