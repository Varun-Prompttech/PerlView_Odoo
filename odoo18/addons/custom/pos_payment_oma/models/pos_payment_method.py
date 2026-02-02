# -*- coding: utf-8 -*-
"""
OMA Payment Method Configuration

Extends pos.payment.method to add OMA payment terminal option and configuration.
Also enables OMA for Kiosk self-order.
"""

from odoo import api, fields, models


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    # Add OMA to payment terminal selection
    def _get_payment_terminal_selection(self):
        """Add OMA to the list of available payment terminals."""
        result = super()._get_payment_terminal_selection()
        result.append(('oma', 'OMA'))
        return result

    # OMA Configuration Fields
    oma_api_endpoint = fields.Char(
        string='API Endpoint',
        help='OMA RPS API base URL (e.g., https://rps.omaemirates.ae)'
    )
    oma_merchant_id = fields.Char(
        string='Merchant ID (MID)',
        help='Merchant ID assigned by the bank'
    )
    oma_terminal_id = fields.Char(
        string='Terminal ID (TID)',
        help='Terminal ID of the ECR device'
    )
    oma_client_id = fields.Char(
        string='Client ID',
        help='Client ID for ECR identification'
    )
    oma_api_key = fields.Char(
        string='API Key',
        help='API Key from OSH portal'
    )
    oma_aes_key = fields.Char(
        string='AES Key',
        help='AES-256 encryption key for payload encryption'
    )

    @api.model
    def _load_pos_self_data_domain(self, data):
        """Override to include OMA terminal for Kiosk mode."""
        if data['pos.config']['data'][0]['self_ordering_mode'] == 'kiosk':
            # Include OMA alongside adyen and stripe terminals
            return [
                ('use_payment_terminal', 'in', ['adyen', 'stripe', 'oma']),
                ('id', 'in', data['pos.config']['data'][0]['payment_method_ids'])
            ]
        else:
            return [('id', '=', False)]
