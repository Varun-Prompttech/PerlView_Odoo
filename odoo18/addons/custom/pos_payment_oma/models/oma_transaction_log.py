# -*- coding: utf-8 -*-
"""
OMA Transaction Log Model

Stores API request and response data for OMA payment transactions.
"""

from odoo import models, fields, api
import json


class OmaTransactionLog(models.Model):
    _name = 'oma.transaction.log'
    _description = 'OMA Transaction Log'
    _order = 'create_date desc'
    _rec_name = 'display_name'

    # Link to POS Order
    pos_order_id = fields.Many2one('pos.order', string='POS Order', ondelete='cascade', index=True)
    order_name = fields.Char(string='Order Reference', related='pos_order_id.name', store=True)
    
    # Transaction identifiers
    client_ref = fields.Char(string='Client Reference')
    mw_request_id = fields.Char(string='MW Request ID')
    invoice_no = fields.Char(string='Invoice Number')
    
    # API Type
    api_type = fields.Selection([
        ('initiate', 'Transaction Initiate'),
        ('inquiry', 'Transaction Inquiry'),
    ], string='API Type', required=True)
    
    # Request/Response data
    request_url = fields.Char(string='Request URL')
    request_headers = fields.Text(string='Request Headers')
    request_body = fields.Text(string='Request Body')
    response_body = fields.Text(string='Response Body')
    
    # Key response fields (for quick filtering)
    error_code = fields.Char(string='Error Code')
    error_message = fields.Char(string='Error Message')
    is_success = fields.Boolean(string='Is Success', compute='_compute_is_success', store=True)
    
    # Transaction details from response
    auth_code = fields.Char(string='Auth Code')
    rrn = fields.Char(string='RRN')
    card_type = fields.Char(string='Card Type')
    masked_pan = fields.Char(string='Masked PAN')
    amount = fields.Float(string='Amount')
    
    # Computed display name
    display_name = fields.Char(string='Name', compute='_compute_display_name', store=True)
    
    @api.depends('api_type', 'client_ref', 'create_date')
    def _compute_display_name(self):
        for rec in self:
            api_label = dict(self._fields['api_type'].selection).get(rec.api_type, rec.api_type)
            rec.display_name = f"{api_label} - {rec.client_ref or 'N/A'}"
    
    @api.depends('error_code')
    def _compute_is_success(self):
        for rec in self:
            rec.is_success = rec.error_code == '000'
    
    def get_request_body_formatted(self):
        """Return formatted JSON for display."""
        self.ensure_one()
        try:
            return json.dumps(json.loads(self.request_body), indent=2) if self.request_body else ''
        except:
            return self.request_body or ''
    
    def get_response_body_formatted(self):
        """Return formatted JSON for display."""
        self.ensure_one()
        try:
            return json.dumps(json.loads(self.response_body), indent=2) if self.response_body else ''
        except:
            return self.response_body or ''
