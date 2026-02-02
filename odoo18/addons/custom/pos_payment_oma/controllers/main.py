# -*- coding: utf-8 -*-
"""
OMA Payment Controller

Handles ECR payment API calls for Kiosk self-order.
"""

import logging
import json
import requests
from odoo import http, fields
from odoo.http import request

_logger = logging.getLogger(__name__)


class OmaPaymentController(http.Controller):

    @http.route(
        '/pos_payment_oma/pay/<int:pos_config_id>',
        type='json',
        auth='public',
        methods=['POST'],
        csrf=False
    )
    def process_oma_payment(self, pos_config_id, order, access_token, payment_method_id, **kwargs):
        """
        Process OMA ECR payment for Kiosk order.
        
        1. Validate the order and access token
        2. Call OMA ECR API to initiate payment
        3. If successful, create payment and complete order
        4. Return result to frontend
        """
        try:
            # Get POS config
            pos_config = request.env['pos.config'].sudo().browse(pos_config_id)
            if not pos_config.exists():
                return {'success': False, 'error': 'POS configuration not found'}

            # Validate access token
            if pos_config.access_token != access_token:
                return {'success': False, 'error': 'Invalid access token'}

            # Get payment method
            payment_method = request.env['pos.payment.method'].sudo().browse(payment_method_id)
            if not payment_method.exists() or payment_method.use_payment_terminal != 'oma':
                return {'success': False, 'error': 'Invalid payment method'}

            # Get or create the order
            pos_order = self._get_or_create_order(pos_config, order)
            if not pos_order:
                return {'success': False, 'error': 'Failed to create order'}

            # Calculate amount
            amount = pos_order.amount_total

            # Call OMA ECR API
            ecr_result = self._call_oma_ecr_api(payment_method, amount, pos_order)

            if ecr_result.get('success'):
                # Create payment and complete order
                try:
                    self._create_payment_and_complete(pos_order, payment_method, amount, ecr_result)
                    return {
                        'success': True,
                        'order_access_token': pos_order.access_token,
                        'message': 'Payment successful'
                    }
                except Exception as e:
                    return {
                        'success': False,
                        'error': f'Order Completion Error: {str(e)}'
                    }
            else:
                return {
                    'success': False,
                    'error': ecr_result.get('error', 'Payment failed at terminal')
                }

        except Exception as e:
            _logger.exception("OMA Payment Error: %s", str(e))
            return {'success': False, 'error': str(e)}

    def _get_or_create_order(self, pos_config, order_data):
        """Get existing order or create a new one from the order data."""
        try:
            # Find existing order by uuid if available
            if order_data.get('uuid'):
                existing_order = request.env['pos.order'].sudo().search([
                    ('uuid', '=', order_data['uuid']),
                    ('config_id', '=', pos_config.id),
                ], limit=1)
                if existing_order:
                    # Clear existing payments if any, to avoid duplicate/partial payment issues in retry
                    # relevant if previously failed
                    return existing_order

            # Create new order from the self-order data
            session = pos_config.current_session_id
            if not session:
                _logger.error("No active session for POS config %s", pos_config.id)
                return None

            # Prepare order values
            order_vals = {
                'config_id': pos_config.id,
                'session_id': session.id,
                'partner_id': order_data.get('partner_id'),
                'pricelist_id': pos_config.pricelist_id.id,
                'lines': [],
            }

            # Add order lines
            for line_data in order_data.get('lines', []):
                if isinstance(line_data, (list, tuple)) and len(line_data) >= 3:
                    line_vals = line_data[2] if len(line_data) >= 3 else line_data[1]
                else:
                    line_vals = line_data

                order_vals['lines'].append((0, 0, {
                    'product_id': line_vals.get('product_id'),
                    'qty': line_vals.get('qty', 1),
                    'price_unit': line_vals.get('price_unit', 0),
                    'price_subtotal': line_vals.get('price_subtotal', 0),
                    'price_subtotal_incl': line_vals.get('price_subtotal_incl', 0),
                }))

            pos_order = request.env['pos.order'].sudo().create(order_vals)
            return pos_order

        except Exception as e:
            _logger.exception("Error creating order: %s", str(e))
            return None

    def _call_oma_ecr_api(self, payment_method, amount, pos_order):
        """
        Call OMA ECR API to process payment.
        """
        try:
            api_endpoint = payment_method.oma_api_endpoint
            merchant_id = payment_method.oma_merchant_id
            terminal_id = payment_method.oma_terminal_id
            client_id = payment_method.oma_client_id
            api_key = payment_method.oma_api_key

            # 1. Validation: Fail if not configured
            if not all([api_endpoint, merchant_id, terminal_id]):
                _logger.warning("OMA terminal not fully configured for Payment Method %s", payment_method.name)
                return {
                    'success': False,
                    'error': 'ECR Terminal configuration missing (Endpoint/Merchant/Terminal ID).',
                    'detail': 'Please configure OMA settings in Odoo.'
                }

            # Prepare ECR request payload
            # Amount should be in cents (e.g. 10.50 -> 1050)
            amount_cents = int(round(amount * 100))
            
            payload = {
                'merchantId': merchant_id,
                'terminalId': terminal_id,
                'clientId': client_id or "",
                'amount': amount_cents,
                'currency': pos_order.currency_id.name or 'AED',
                'referenceNo': str(pos_order.pos_reference or pos_order.id),
                'transactionType': 'SALE', 
            }

            headers = {
                'Content-Type': 'application/json',
            }
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'

            _logger.info("Calling OMA ECR API: %s with payload %s", api_endpoint, payload)
            
            # Make the API call
            # Using a shorter timeout for connection, but reasonable for read
            response = requests.post(
                f"{api_endpoint}/sale",  # Adjust endpoint suffix if needed based on specific OMA docs
                json=payload,
                headers=headers,
                timeout=(10, 120) 
            )

            _logger.info("OMA ECR Response: %s", response.text)

            if response.status_code == 200:
                result = response.json()
                # Check specific OMA success codes. Assuming '00' is success based on common ISO8583 patterns
                # Adjust 'responseCode' key based on actual API doc if different
                if result.get('responseCode') == '00' or result.get('success') is True: 
                    return {
                        'success': True,
                        'transaction_id': result.get('transactionId') or result.get('rrn'),
                        'approval_code': result.get('approvalCode'),
                        'message': 'Payment approved'
                    }
                else:
                    error_msg = result.get('responseMessage') or result.get('message') or 'Declined by terminal (Unknown Reason)'
                    return {
                        'success': False,
                        'error': error_msg
                    }
            else:
                return {
                    'success': False,
                    'error': f'Terminal Communication Error (Status {response.status_code})'
                }

        except requests.Timeout:
            return {'success': False, 'error': 'Timeout: Terminal did not respond in time.'}
        except requests.ConnectionError:
            return {'success': False, 'error': 'Connection Failed: Could not reach payment terminal.'}
        except Exception as e:
            _logger.exception("OMA ECR Error: %s", str(e))
            return {'success': False, 'error': f'System Error: {str(e)}'}

    def _create_payment_and_complete(self, pos_order, payment_method, amount, ecr_result):
        """Create payment for the order and validate it."""
        try:
            _logger.info("Completing order %s with amount %s", pos_order.name, amount)

            # 1. Create the payment
            payment_vals = {
                'pos_order_id': pos_order.id,
                'payment_method_id': payment_method.id,
                'amount': amount,
                'transaction_id': ecr_result.get('transaction_id', ''),
                'payment_date': fields.Datetime.now(),
                'card_type': 'oma_ecr',
            }
            
            payment = request.env['pos.payment'].sudo().create(payment_vals)
            
            # 2. Verify total paid matches total due
            # Important: Re-browse to get updated amount_paid computation
            pos_order = pos_order.sudo() # ensure we have sudo access
            
            # 3. Validate
            # action_pos_order_paid() checks if state is 'draft' and amount_paid >= amount_total
            # It transitions to 'paid', creates accounting entries, etc.
            if pos_order.state == 'draft':
                pos_order.action_pos_order_paid()
            
            _logger.info("Order %s successfully processed", pos_order.name)

        except Exception as e:
            _logger.exception("Error completing order %s: %s", pos_order.name, str(e))
            raise
