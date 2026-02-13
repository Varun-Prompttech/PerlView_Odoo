# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api


class ShCashInOut(models.Model):
    _name = 'sh.cash.in.out'
    _description = "Cash In Out"

    sh_transaction_type = fields.Selection(
        [('cash_in', 'Cash In'), ('cash_out', 'Cash Out')], string="Transaction Type", required=True)
    sh_amount = fields.Float(string="Amount")
    sh_reason = fields.Char(string="Reason")
    sh_session = fields.Many2one('pos.session', string="Session")
    sh_date = fields.Datetime(
        string='Date', readonly=True, index=True, default=fields.Datetime.now)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    @api.model
    def try_cash_in_out(self, session, _type, amount, reason):
        if _type == 'in':
            self.env['sh.cash.in.out'].create(
                {'sh_amount': amount, 'sh_reason': reason, 'sh_session': session, 'sh_transaction_type': 'cash_in'})
        else:
            self.env['sh.cash.in.out'].create(
                {'sh_amount': amount, 'sh_reason': reason, 'sh_session': session, 'sh_transaction_type': 'cash_out'})

    @api.model
    def _load_pos_data_domain(self, data):
        return [('sh_session', '=',  data['pos.config']['data'][0]['current_session_id'])]
    
    @api.model
    def _load_pos_data_fields(self, config_id):
        return []
    
    def _load_pos_data(self, data):
        domain = self._load_pos_data_domain(data)
        fields = self._load_pos_data_fields(data['pos.config']['data'][0]['id'])
        return {
            'data': self.search_read(domain, fields, load=False) if domain is not False else [],
            'fields': fields,
        }