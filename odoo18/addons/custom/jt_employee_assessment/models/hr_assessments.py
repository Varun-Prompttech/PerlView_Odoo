from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from pytz import timezone
import requests
import logging

_logger = logging.getLogger(__name__)


class HRAssessments(models.Model):
    _name = 'hr.assessments'
    _description = 'HR Employee Assessment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'

    name = fields.Char(string='Name')
    seq_number = fields.Char(string='Seq Number', readonly=True, store=True)
    complete_date = fields.Datetime(string='Completion Date', readonly=True, store=True)
    current_date = fields.Datetime(string='Current Date', readonly=True, store=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    store_id = fields.Many2one('assessment.store', string='Store Name', required=True)
    template_id = fields.Many2one('assessment.parameter', string='Parameter', tracking=True)
    ass_type = fields.Selection(
        [('daily', 'Daily'), ('monthly', 'Monthly')], copy=False,
        string='Assessment Type')
    assessment_line_ids = fields.One2many(
        'hr.assessments.line', 'assessment_id', string='Assessment Lines')
    total_points = fields.Float(
        string='Average Score',
        compute='_compute_total_points',
        store=True, digits=(3, 1)
    )
    total_average_points = fields.Float(
        string='Total Average Score',
        compute='_compute_total_average_points',
        store=True, digits=(3, 1)
    )
    year = fields.Char(string='Year')
    month = fields.Selection([
        ('01', 'January'),
        ('02', 'February'),
        ('03', 'March'),
        ('04', 'April'),
        ('05', 'May'),
        ('06', 'June'),
        ('07', 'July'),
        ('08', 'August'),
        ('09', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December')])
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('assigned', 'Assigned'),
            ('completed', 'Completed'),
        ],
        string='Status',
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        default='draft',
    )

    partner_latitude = fields.Float('Geo Latitude', digits=(10, 7))
    partner_longitude = fields.Float('Geo Longitude', digits=(10, 7))
    date_localization = fields.Date(string='Geolocation Date')

    def get_system_location(self):
        """Get the system's current location based on IP using an external geolocation service."""
        try:
            response = requests.get('http://ipinfo.io/json')
            if response.status_code != 200:
                _logger.error(f"Failed to fetch location: {response.status_code} - {response.text}")
                return 0.0, 0.0

            data = response.json()
            loc = data.get('loc', '').split(',')
            latitude = loc[0] if loc else 0.0
            longitude = loc[1] if len(loc) > 1 else 0.0
            return float(latitude), float(longitude)

        except requests.RequestException as e:
            _logger.error(f"Request error when fetching system location: {str(e)}")
        except ValueError as e:
            _logger.error(f"Value error when processing system location data: {str(e)}")
        except Exception as e:
            _logger.error(f"Unexpected error fetching system location: {str(e)}")
        return 0.0, 0.0

    def update_partner_location(self):
        latitude, longitude = self.get_system_location()
        self.write({
            'partner_latitude': latitude,
            'partner_longitude': longitude,
        })

        _logger.info(f"Updated partner location to lat: {latitude}, lon: {longitude}")

    @api.onchange('ass_type')
    def _onchange_ass_type(self):
        if self.ass_type == 'monthly':
            current_date = datetime.today()
            self.month = current_date.strftime('%m')
            self.year = str(current_date.year)
        elif self.ass_type == 'daily':
            self.current_date = fields.Datetime.now()

    @api.model
    def create(self, values):
        values['seq_number'] = self.env['ir.sequence'].next_by_code('employee.assessment')
        return super().create(values)

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        for rec in self:
            if rec.employee_id.assessment_template_id:
                rec.template_id = rec.employee_id.assessment_template_id.id

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            lines = [(5, 0, 0)]
            for param_line in self.template_id.assessment_parameter_line_ids:
                if param_line.display_type not in ['line_section', 'line_note']:
                    lines.append((0, 0, {
                        'name': param_line.parameter_id,
                        'is_assessment_true': False,
                        'is_assessment_false': False,
                        'parameter_line_id': param_line.id,
                    }))
            self.assessment_line_ids = lines
        else:
            self.assessment_line_ids = [(5, 0, 0)]

    def complete_assessment(self):
        for each in self:
            each.update_partner_location()
            # if each.store_id.partner_latitude != each.partner_latitude or each.store_id.partner_longitude != each.partner_longitude:
            #     raise ValidationError("You are not allowed to complete the assessment. Please complete your assessment at the same location.")
            for rec in each.assessment_line_ids:
                if each.state == 'assigned':
                    if not (rec.is_assessment_true or rec.is_assessment_false or rec.is_assessment_na):
                        raise ValidationError("You must select at least one option: Yes, No, or NA.")
            template = self.env.ref('jt_employee_assessment.mail_template_for_employee_assessment')
            if each.employee_id.work_email:
                emails = each.employee_id.work_email
                if emails:
                    template.send_mail(
                        self.id,
                        email_values={'email_to': emails},
                        force_send=True
                    )
            each.complete_date = fields.Datetime.now()
            each.state = 'completed'

    def assign_assessment(self):
        for each in self:
            each.state = 'assigned'

    def get_local_complete_date(self):
        user_tz = self.env.user.tz
        if user_tz and self.complete_date:
            user_time_zone = timezone(user_tz)
            local_dt = self.complete_date.astimezone(user_time_zone)
            return local_dt.strftime('%Y-%m-%d %H:%M:%S')
        return self.complete_date.strftime('%Y-%m-%d %H:%M:%S') if self.complete_date else ''

    @api.depends('employee_id.assessment_ids')
    def _compute_total_average_points(self):
        total_count = len(self.employee_id.assessment_ids)
        print("total_count", total_count)
        if total_count > 0:
            average_points = 0
            for each in self.employee_id.assessment_ids:
                average_points += each.total_points
                print("average_points", average_points)
            total_average_points = average_points / total_count
            self.total_average_points = total_average_points


    @api.depends('assessment_line_ids.is_assessment_true', 'assessment_line_ids.is_assessment_false',
                 'assessment_line_ids.is_assessment_na')
    def _compute_total_points(self):
        for rec in self:
            correct_answers = 0
            scored_questions = 0

            for line in rec.assessment_line_ids:
                param_line = line.parameter_line_id
                if param_line.display_type in ['line_section', 'line_note']:
                    continue

                if not param_line or line.is_assessment_na:
                    continue

                scored_questions += 1
                if (param_line.is_true and line.is_assessment_true) or (
                        param_line.is_false and line.is_assessment_false):
                    correct_answers += 1

            if scored_questions > 0:
                rec.total_points = (correct_answers / scored_questions) * 10
            else:
                rec.total_points = 0

            rec.total_points = round(rec.total_points, 1)


class HRAssessmentLines(models.Model):
    _name = 'hr.assessments.line'
    _description = 'HR Assessment Lines'

    assessment_id = fields.Many2one('hr.assessments', string='Assessment')
    parameter_line_id = fields.Many2one('assessment.parameter.line', string='Template Line')
    name = fields.Char(string='Parameter Name')
    note = fields.Text(string='Notes')
    is_assessment_true = fields.Boolean(string='Yes')
    is_assessment_false = fields.Boolean(string='No')
    is_assessment_na = fields.Boolean(string='NA')
    attachment_ids = fields.Many2many(
        'ir.attachment', 'id_attachment_rel',
        'id_ref', 'attach_ref', string="Attachment",
        help='Attach the copy of Identification document')

    @api.onchange('is_assessment_true')
    def _onchange_is_assessment_true(self):
        if self.is_assessment_true:
            self.is_assessment_false = False
            self.is_assessment_na = False

    @api.onchange('is_assessment_false')
    def _onchange_is_assessment_false(self):
        if self.is_assessment_false:
            self.is_assessment_true = False
            self.is_assessment_na = False

    @api.onchange('is_assessment_na')
    def _onchange_is_assessment_na(self):
        if self.is_assessment_na:
            self.is_assessment_true = False
            self.is_assessment_false = False
