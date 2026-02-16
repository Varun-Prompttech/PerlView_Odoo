# -*- coding: utf-8 -*-
from odoo import models, fields

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    # These fields are required by third-party modules (sh_pos_z_report and jt_employee_assessment)
    # when loading the employee profile in Kiosk mode. We define them here in our custom 
    # module to ensure Kiosk compatibility regardless of third-party module updates.
    
    sh_is_allow_z_report = fields.Boolean(
        related='employee_id.sh_is_allow_z_report', 
        readonly=True,
        string="Allow to Generate Z-Report ?"
    )
    
    assessment_template_id = fields.Many2one(
        related='employee_id.assessment_template_id',
        readonly=True,
        string='Assessment Parameter'
    )
