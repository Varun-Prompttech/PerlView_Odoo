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
    oma_secret_key = fields.Char(
        string='Secret Key',
        help='OMA Secret Key for API authentication (omaSecretKey header)'
    )
    oma_key_version = fields.Char(
        string='Key Version',
        help='Version of the encryption key (e.g., 00e2f47b-2cfb...)'
    )
    oma_institute = fields.Char(
        string='Institute',
        help='Bank Name (e.g., Bank)'
    )
    oma_serial_number = fields.Char(
        string='Serial Number',
        help='Serial Number of the POS device'
    )
    oma_auto_confirm = fields.Boolean(
        string='Auto Confirm Payment (Test Mode)',
        default=False,
        help='When enabled, payments are auto-approved without contacting the OMA terminal. '
             'Use this for testing only. Disable for production/go-live.'
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
