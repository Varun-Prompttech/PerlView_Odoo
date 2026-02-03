# -*- coding: utf-8 -*-
"""
OMA Payment Controller

Handles ECR payment API calls for Kiosk self-order.
"""

import logging
import json
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

            _logger.info("Processing OMA payment for order %s (ID: %s), amount: %s", 
                        pos_order.name, pos_order.id, pos_order.amount_total)

            # Calculate amount
            amount = pos_order.amount_total

            if amount <= 0:
                return {'success': False, 'error': 'Order amount must be greater than 0'}

            # Call OMA ECR API
            ecr_result = self._call_oma_ecr_api(payment_method, amount, pos_order)

            if ecr_result.get('success'):
                # Create payment and complete order
                try:
                    self._create_payment_and_complete(pos_order, payment_method, amount, ecr_result)
                    # Ensure access token is generated for confirmation page (needed for printing)
                    order_access_token = pos_order._ensure_access_token()
                    return {
                        'success': True,
                        'order_access_token': order_access_token,
                        'message': 'Payment successful'
                    }
                except Exception as e:
                    _logger.exception("Order completion error for %s: %s", pos_order.name, str(e))
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
            _logger.info("Order data received: %s", order_data)
            
            # Find existing order by uuid if available
            if order_data.get('uuid'):
                existing_order = request.env['pos.order'].sudo().search([
                    ('uuid', '=', order_data['uuid']),
                    ('config_id', '=', pos_config.id),
                ], limit=1)
                if existing_order:
                    _logger.info("Found existing order: %s", existing_order.name)
                    return existing_order

            # Also check by access_token if provided
            if order_data.get('access_token'):
                existing_order = request.env['pos.order'].sudo().search([
                    ('access_token', '=', order_data['access_token']),
                    ('config_id', '=', pos_config.id),
                ], limit=1)
                if existing_order:
                    _logger.info("Found existing order by access_token: %s", existing_order.name)
                    return existing_order

            # Create new order from the self-order data
            session = pos_config.current_session_id
            if not session:
                _logger.error("No active session for POS config %s", pos_config.id)
                return None

            # Generate a proper order reference
            order_ref = request.env['ir.sequence'].sudo().next_by_code('pos.order') or f"POS-{pos_config.id}-{fields.Datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Prepare order values
            order_vals = {
                'name': order_ref,
                'pos_reference': order_ref,
                'config_id': pos_config.id,
                'session_id': session.id,
                'partner_id': order_data.get('partner_id') or False,
                'pricelist_id': pos_config.pricelist_id.id,
                'lines': [],
                'uuid': order_data.get('uuid') or False,
            }

            # Add order lines
            lines_data = order_data.get('lines', [])
            _logger.info("Processing %d order lines", len(lines_data))
            
            for line_data in lines_data:
                # Handle different line data formats
                if isinstance(line_data, (list, tuple)):
                    if len(line_data) >= 3:
                        line_vals = line_data[2]
                    elif len(line_data) >= 2:
                        line_vals = line_data[1]
                    else:
                        line_vals = line_data[0] if line_data else {}
                else:
                    line_vals = line_data

                product_id = line_vals.get('product_id')
                if isinstance(product_id, (list, tuple)):
                    product_id = product_id[0]
                
                if not product_id:
                    _logger.warning("Skipping line without product_id: %s", line_vals)
                    continue

                qty = float(line_vals.get('qty', 1))
                price_unit = float(line_vals.get('price_unit', 0))
                
                # Calculate subtotals if not provided
                price_subtotal_incl = float(line_vals.get('price_subtotal_incl', price_unit * qty))
                price_subtotal = float(line_vals.get('price_subtotal', price_subtotal_incl))

                order_vals['lines'].append((0, 0, {
                    'product_id': product_id,
                    'qty': qty,
                    'price_unit': price_unit,
                    'price_subtotal': price_subtotal,
                    'price_subtotal_incl': price_subtotal_incl,
                }))

            if not order_vals['lines']:
                _logger.error("No valid order lines found")
                return None

            _logger.info("Creating order with vals: %s", {k: v for k, v in order_vals.items() if k != 'lines'})
            pos_order = request.env['pos.order'].sudo().create(order_vals)
            _logger.info("Created order: %s (ID: %s), Total: %s", pos_order.name, pos_order.id, pos_order.amount_total)
            return pos_order

        except Exception as e:
            _logger.exception("Error creating order: %s", str(e))
            return None

    def _call_oma_ecr_api(self, payment_method, amount, pos_order):
        """
        Call OMA ECR API to process payment via OMAService.
        """
        from odoo.addons.pos_payment_oma.services.oma_service import OMAService

        try:
            # 1. Validation requirements
            required_fields = [
                payment_method.oma_api_endpoint,
                payment_method.oma_merchant_id,
                payment_method.oma_terminal_id,
                payment_method.oma_key_version,
                payment_method.oma_institute,
                payment_method.oma_serial_number,
                payment_method.oma_secret_key
            ]

            if not all(required_fields):
                _logger.warning("OMA terminal not fully configured for Payment Method %s", payment_method.name)
                return {
                    'success': False,
                    'error': 'ECR Terminal configuration missing.',
                    'detail': 'Check API Endpoint, Merchant ID, Terminal ID, Key Version, Institute, Serial Number, Secret Key.'
                }

            # Instantiate Service
            service = OMAService(
                api_endpoint=payment_method.oma_api_endpoint,
                merchant_id=payment_method.oma_merchant_id,
                terminal_id=payment_method.oma_terminal_id,
                key_version=payment_method.oma_key_version,
                institute=payment_method.oma_institute,
                serial_number=payment_method.oma_serial_number,
                secret_key=payment_method.oma_secret_key
            )

            # Initiate Transaction - use order name as client reference
            client_ref = pos_order.pos_reference or pos_order.name or f"ORDER-{pos_order.id}"
            invoice_no = str(pos_order.id).zfill(6)  # 6-digit invoice number
            
            _logger.info("Initiating OMA Transaction for Ref: %s, Invoice: %s, Amount: %s", 
                        client_ref, invoice_no, amount)
            
            result = service.initiate_transaction(amount, client_ref, invoice_no)

            # Handle Result
            if result.get('omaErrorCode') == '000':
                _logger.info("OMA Initiation Success. Polling for status...")
                mw_request_id = result.get('omaTxnMwRequestId')
                
                if not mw_request_id:
                    # Some implementations might return success immediately w/o MW ID
                    if result.get('omaIsTransactionSuccess') == 'true':
                        return {
                            'success': True,
                            'transaction_id': 'N/A',
                            'message': 'Payment approved',
                            'oma_response': result
                        }
                    else:
                        return {
                            'success': False,
                            'error': 'No transaction ID received from terminal'
                        }
                
                return self._poll_transaction_status(service, client_ref, mw_request_id)
            else:
                error_msg = result.get('omaErrorMessage') or 'Unknown Error'
                return {
                    'success': False,
                    'error': f"Initiation Failed: {error_msg}"
                }

        except Exception as e:
            _logger.exception("OMA ECR Error: %s", str(e))
            return {'success': False, 'error': f'System Error: {str(e)}'}

    def _poll_transaction_status(self, service, client_ref, mw_request_id):
        """Poll the inquiry API until success, failure, or timeout."""
        import time
        
        # Poll for up to 120 seconds (60 retries * 2 seconds)
        max_retries = 60
        
        for attempt in range(max_retries):
            time.sleep(2)
            try:
                status_result = service.check_status(client_ref, mw_request_id)
                _logger.info("OMA Poll Status (attempt %d): errorCode=%s, statusMsg=%s", 
                            attempt + 1,
                            status_result.get('omaErrorCode'),
                            status_result.get('omaTransactionStatusMsg'))

                error_code = status_result.get('omaErrorCode')
                
                if error_code == '000':
                    status_msg = status_result.get('omaTransactionStatusMsg', '')
                    is_success = status_result.get('omaIsTransactionSuccess')
                    
                    if status_msg == 'TRANSACTION_SUCCESS' or is_success == 'true':
                        _logger.info("Payment SUCCESS! Auth: %s, RRN: %s", 
                                    status_result.get('omaAuthCode'),
                                    status_result.get('omaRrn'))
                        return {
                            'success': True,
                            'transaction_id': mw_request_id,
                            'auth_code': status_result.get('omaAuthCode', ''),
                            'rrn': status_result.get('omaRrn', ''),
                            'card_type': status_result.get('omaCardName', ''),
                            'masked_pan': status_result.get('omaMaskedPan', ''),
                            'message': status_result.get('omaErrorMessage', 'Approved'),
                            'oma_response': status_result
                        }
                    elif status_msg in ['DECLINED', 'CANCELLED_BY_CLIENT', 'TIMEOUT', 'FAILED', 'TRANSACTION_FAILED']:
                        return {
                            'success': False,
                            'error': f'Transaction {status_msg}'
                        }
                    # Continue polling if status is pending or empty
                elif error_code != '000':
                    # Non-zero error code from inquiry
                    error_msg = status_result.get('omaErrorMessage', 'Unknown error')
                    if 'pending' not in error_msg.lower():
                        return {
                            'success': False,
                            'error': f'Terminal Error: {error_msg}'
                        }
                        
            except Exception as e:
                _logger.warning("Polling error (attempt %d): %s", attempt + 1, e)
                # Continue polling even if one request fails
        
        return {'success': False, 'error': 'Payment Timed Out (No response from terminal in 120 seconds)'}

    def _create_payment_and_complete(self, pos_order, payment_method, amount, ecr_result):
        """Create payment for the order and validate it."""
        try:
            _logger.info("Completing order %s with amount %s", pos_order.name, amount)
            _logger.info("Order state: %s, amount_total: %s, amount_paid: %s", 
                        pos_order.state, pos_order.amount_total, pos_order.amount_paid)

            # Build transaction details for storage
            transaction_id = ecr_result.get('transaction_id', '')
            card_type = ecr_result.get('card_type', 'OMA Card')
            
            # Create the payment
            payment_vals = {
                'pos_order_id': pos_order.id,
                'payment_method_id': payment_method.id,
                'amount': amount,
                'transaction_id': transaction_id,
                'payment_date': fields.Datetime.now(),
            }
            
            # Add card info if available
            if ecr_result.get('masked_pan'):
                payment_vals['card_no'] = ecr_result.get('masked_pan')
            if ecr_result.get('card_type'):
                payment_vals['card_type'] = ecr_result.get('card_type')
            
            _logger.info("Creating payment with vals: %s", payment_vals)
            payment = request.env['pos.payment'].sudo().create(payment_vals)
            _logger.info("Payment created: ID %s, amount %s", payment.id, payment.amount)
            
            # Refresh order to get updated amount_paid
            pos_order.invalidate_recordset(['amount_paid'])
            _logger.info("After payment - amount_paid: %s, amount_total: %s", 
                        pos_order.amount_paid, pos_order.amount_total)
            
            # Validate order if draft and fully paid
            if pos_order.state == 'draft':
                if pos_order.amount_paid >= pos_order.amount_total:
                    pos_order.action_pos_order_paid()
                    _logger.info("Order %s marked as paid", pos_order.name)
                else:
                    _logger.warning("Order %s not fully paid: paid=%s, total=%s", 
                                   pos_order.name, pos_order.amount_paid, pos_order.amount_total)
                    raise ValueError(f"Order {pos_order.name} is not fully paid (paid: {pos_order.amount_paid}, total: {pos_order.amount_total})")
            
            _logger.info("Order %s successfully processed", pos_order.name)

        except Exception as e:
            _logger.exception("Error completing order %s: %s", pos_order.name, str(e))
            raise
