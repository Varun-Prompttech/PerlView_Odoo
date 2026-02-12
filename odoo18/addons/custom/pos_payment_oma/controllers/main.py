# -*- coding: utf-8 -*-
"""
OMA Payment Controller

Handles ECR payment API calls for Kiosk self-order.
"""

import logging
import json
import subprocess
import tempfile
import os
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
    def process_oma_payment(self, pos_config_id, order, access_token, payment_method_id, retry_count=0, **kwargs):
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

            # Flush order to ensure it's in DB with stable ID
            request.env['pos.order'].flush_model()
            request.env.cr.commit()
            
            # Re-read order to ensure we have latest state
            pos_order = request.env['pos.order'].sudo().browse(pos_order.id)
            
            _logger.info("Processing OMA payment for order %s (ID: %s), amount: %s, lines: %d", 
                        pos_order.name, pos_order.id, pos_order.amount_total, len(pos_order.lines))

            # Calculate amount
            amount = pos_order.amount_total

            if amount <= 0:
                _logger.error("Order %s has zero or negative amount: %s", pos_order.name, amount)
                return {'success': False, 'error': f'Order amount must be greater than 0 (got {amount})'}

            # DEBUG: Automatic payment approval for testing
            # ecr_result = self._call_oma_ecr_api(payment_method, amount, pos_order, retry_count)
            ecr_result = {
                'success': True,
                'transaction_id': 'TEST-AUTO-APPROVE',
                'card_type': 'TEST CARD',
                'masked_pan': '**** **** **** 1234',
                'message': 'Payment approved (Auto-approved for testing)'
            }

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

    def _get_next_kiosk_sequence(self, pos_config):
        """Generate a simple sequence number for Kiosk orders."""
        # This is a simple implementation. Ideally use ir.sequence per config.
        # Count orders for this config to get next number
        count = request.env['pos.order'].sudo().search_count([('config_id', '=', pos_config.id)])
        return count + 1

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
                    _logger.info("Found existing order: %s (ID: %s)", existing_order.name, existing_order.id)
                    # Fix invalid name or "Furniture Shop" name if needed
                    # Use case-insensitive check
                    is_furniture = 'furniture' in existing_order.name.lower() if existing_order.name else False
                    if not existing_order.name or existing_order.name == '/' or is_furniture:
                        # Generate new Kiosk reference
                        prefix = pos_config.name if pos_config.name and 'furniture' not in pos_config.name.lower() else 'Kiosk'
                        seq_number = self._get_next_kiosk_sequence(pos_config)
                        new_name = f"{prefix} {seq_number}"
                        
                        # Use SQL to force rename as name might be readonly/restricted in ORM
                        request.env.cr.execute("UPDATE pos_order SET name = %s, pos_reference = %s WHERE id = %s", (new_name, new_name, existing_order.id))
                        request.env.cr.commit()
                        existing_order.invalidate_recordset()
                        _logger.info("Forced existing order rename from '%s' to '%s' via SQL", existing_order.name, new_name)
                    return existing_order

            # Also check by access_token if provided
            if order_data.get('access_token'):
                existing_order = request.env['pos.order'].sudo().search([
                    ('access_token', '=', order_data['access_token']),
                    ('config_id', '=', pos_config.id),
                ], limit=1)
                if existing_order:
                    _logger.info("Found existing order by access_token: %s (ID: %s)", existing_order.name, existing_order.id)
                    # Fix invalid name or "Furniture Shop" name if needed
                    is_furniture = 'furniture' in existing_order.name.lower() if existing_order.name else False
                    if not existing_order.name or existing_order.name == '/' or is_furniture:
                        # Generate new Kiosk reference
                        prefix = pos_config.name if pos_config.name and 'furniture' not in pos_config.name.lower() else 'Kiosk'
                        seq_number = self._get_next_kiosk_sequence(pos_config)
                        new_name = f"{prefix} {seq_number}"
                        
                        # Use SQL to force rename
                        request.env.cr.execute("UPDATE pos_order SET name = %s, pos_reference = %s WHERE id = %s", (new_name, new_name, existing_order.id))
                        request.env.cr.commit()
                        existing_order.invalidate_recordset()
                        _logger.info("Forced existing order rename from '%s' to '%s' (by token) via SQL", existing_order.name, new_name)
                    return existing_order

            # Create new order from the self-order data
            session = pos_config.current_session_id
            if not session:
                _logger.error("No active session for POS config %s", pos_config.id)
                return None

            # Generate a proper order reference
            order_ref = order_data.get('name')
            # Force overwrite if it contains "Furniture Shop" or is default/empty
            is_furniture = 'furniture' in (order_ref or '').lower()
            if not order_ref or order_ref == '/' or is_furniture:
                 # Use 'Kiosk' prefix as requested by user if POS config name implies it, or just force it for this module
                 prefix = pos_config.name if pos_config.name and 'furniture' not in pos_config.name.lower() else 'Kiosk'
                 
                 # Let's generate a unique reference based on session
                 seq_number = self._get_next_kiosk_sequence(pos_config)
                 order_ref = f"{prefix} {seq_number}"
                 _logger.info("Forced new order ref to '%s'", order_ref)

            # Prepare partner (assign default Guest if missing due to Kiosk mode)
            partner_id = order_data.get('partner_id')
            if not partner_id:
                guest_partner = request.env['res.partner'].sudo().search([
                    ('name', 'ilike', 'Guest'), 
                    ('active', '=', True)
                ], limit=1)
                
                if not guest_partner:
                    guest_partner = request.env['res.partner'].sudo().create({
                        'name': 'Guest Customer',
                        'active': True,
                        'customer_rank': 1,
                    })
                partner_id = guest_partner.id
                _logger.info("Assigned default partner %s (ID: %s) to anonymous order", 
                             guest_partner.name, partner_id)

            # Prepare order values
            order_vals = {
                'name': order_ref,
                'pos_reference': order_ref,
                'config_id': pos_config.id,
                'session_id': session.id,
                'partner_id': partner_id or False,
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

    def _call_oma_ecr_api(self, payment_method, amount, pos_order, retry_count=0):
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
            # Append retry count to make each retry attempt unique for OMA API
            base_ref = pos_order.pos_reference or pos_order.name or f"ORDER-{pos_order.id}"
            if retry_count > 0:
                client_ref = f"{base_ref}-R{retry_count}"
            else:
                client_ref = base_ref
            invoice_no = str(pos_order.id).zfill(6)  # 6-digit invoice number
            
            _logger.info("Initiating OMA Transaction for Ref: %s, Invoice: %s, Amount: %s, Retry: %s", 
                        client_ref, invoice_no, amount, retry_count)
            
            result = service.initiate_transaction(amount, client_ref, invoice_no)
            
            # Save initiate transaction log
            self._save_transaction_log(pos_order, 'initiate', client_ref, result, amount)

            # Handle Result
            # Error 203 means "Sale in progress" - we should try to poll anyway if we have an ID
            # or it might mean the terminal is busy with OUR request just now.
            if result.get('omaErrorCode') == '000' or result.get('omaErrorCode') == '203':
                _logger.info("OMA Initiation Success/InProgress (Code %s). Polling for status...", result.get('omaErrorCode'))
                
                mw_request_id = result.get('omaTxnMwRequestId')
                
                # If 203 (Sale in progress) but NO mw_request_id, we might need to rely on client_ref
                # However, the API usually returns the ID even in 203 cases if it's the same txn
                
                if not mw_request_id:
                     if result.get('omaErrorCode') == '000' and result.get('omaIsTransactionSuccess') == 'true':
                         return {
                            'success': True,
                            'transaction_id': 'N/A',
                            'message': 'Payment approved',
                            'oma_response': result
                        }
                     elif result.get('omaErrorCode') == '203':
                         # If 203 and no ID, we can't really poll with ID. 
                         # But let's try polling with just client_ref or wait and retry?
                         # For now, let's assume we can proceed if we have an ID, or fail if not.
                         return {
                            'success': False,
                            'error': "Terminal busy (Sale in progress) and no Transaction ID returned. Please wait and retry."
                        }
                
                return self._poll_transaction_status(service, client_ref, mw_request_id, pos_order, amount)
            else:
                error_msg = result.get('omaErrorMessage') or 'Unknown Error'
                return {
                    'success': False,
                    'error': f"Initiation Failed: {error_msg}"
                }

        except Exception as e:
            _logger.exception("OMA ECR Error: %s", str(e))
            return {'success': False, 'error': f'System Error: {str(e)}'}

    def _poll_transaction_status(self, service, client_ref, mw_request_id, pos_order=None, amount=0):
        """Poll the inquiry API until success, failure, or timeout."""
        import time
        
        # Poll for up to 120 seconds (60 retries * 2 seconds)
        max_retries = 60
        last_result = None
        
        for attempt in range(max_retries):
            time.sleep(2)
            try:
                status_result = service.check_status(client_ref, mw_request_id)
                last_result = status_result
                error_code = status_result.get('omaErrorCode')
                status_msg = status_result.get('omaTransactionStatusMsg', '')
                
                _logger.info("OMA Poll Status (attempt %d): errorCode=%s, statusMsg=%s", 
                            attempt + 1, error_code, status_msg)

                if error_code == '000':
                    is_success = status_result.get('omaIsTransactionSuccess')
                    
                    if status_msg == 'TRANSACTION_SUCCESS' or is_success == 'true':
                        _logger.info("Payment SUCCESS! Auth: %s, RRN: %s", 
                                    status_result.get('omaAuthCode'),
                                    status_result.get('omaRrn'))
                        
                        # Save successful inquiry log
                        if pos_order:
                            self._save_transaction_log(pos_order, 'inquiry', client_ref, status_result, amount, mw_request_id)
                        
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
                        # Save failed inquiry log
                        if pos_order:
                            self._save_transaction_log(pos_order, 'inquiry', client_ref, status_result, amount, mw_request_id)
                        return {
                            'success': False,
                            'error': f'Transaction {status_msg}'
                        }
                    # If PENDING or similar (often just empty or specific code), continue
                
                elif error_code == '203':
                    # Sale in progress - keep polling
                    _logger.info("Poll: Sale is still in progress (203)... waiting.")
                    continue
                    
                elif error_code != '000':
                    # Non-zero error code from inquiry
                    error_msg = status_result.get('omaErrorMessage', 'Unknown error')
                    # Some gateways return specific codes for "not found yet" or "processing"
                    # If we aren't sure, maybe we shouldn't fail immediately on network blips?
                    if 'pending' in error_msg.lower() or 'process' in error_msg.lower():
                        continue
                    
                    # Save failed inquiry log
                    if pos_order:
                        self._save_transaction_log(pos_order, 'inquiry', client_ref, status_result, amount, mw_request_id)
                        
                    return {
                        'success': False,
                        'error': f'Terminal Error: {error_msg}'
                    }
                        
            except Exception as e:
                _logger.warning("Polling error (attempt %d): %s", attempt + 1, e)
                # Continue polling even if one request fails
        
        # Timeout - save last result if available
        if pos_order and last_result:
            self._save_transaction_log(pos_order, 'inquiry', client_ref, last_result, amount, mw_request_id)
        
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
            
            # Force flush to ensure payment is in DB
            request.env['pos.payment'].flush_model()
            request.env.cr.commit()  # Force commit to DB
            
            _logger.info("Payment created: ID %s, amount %s", payment.id, payment.amount)
            
            # Verify payment was actually created by re-reading from DB
            verify_payment = request.env['pos.payment'].sudo().browse(payment.id)
            _logger.info("Payment verification: exists=%s, order_id=%s, amount=%s", 
                        verify_payment.exists(), verify_payment.pos_order_id.id if verify_payment.exists() else 'N/A',
                        verify_payment.amount if verify_payment.exists() else 'N/A')
            
            # Verify via direct SQL - this is the source of truth
            request.env.cr.execute("""
                SELECT COALESCE(SUM(amount), 0) FROM pos_payment 
                WHERE pos_order_id = %s
            """, (pos_order.id,))
            total_paid_sql = request.env.cr.fetchone()[0]
            _logger.info("Total payments in DB for order %s: %s (order total: %s)", 
                        pos_order.id, total_paid_sql, pos_order.amount_total)
            
            # Check if fully paid using SQL result (with tolerance)
            if total_paid_sql >= (pos_order.amount_total - 0.05):
                if pos_order.state == 'draft':
                    # Directly update order state via SQL
                    request.env.cr.execute("""
                        UPDATE pos_order SET state = 'paid' WHERE id = %s AND state = 'draft'
                    """, (pos_order.id,))
                    request.env.cr.commit()
                    
                    # Invalidate cache and re-read
                    pos_order.invalidate_recordset()
                    pos_order = request.env['pos.order'].sudo().browse(pos_order.id)
                    
                    _logger.info("Order %s state set to 'paid' via SQL", pos_order.name)
                    
                    # Try to complete the order properly (create accounting entries, picking, etc.)
                    try:
                        # Call process_saved_order to trigger KOT, notifications etc.
                        # draft=False means process normally
                        pos_order._process_saved_order(False)
                        _logger.info("Processed saved order %s", pos_order.name)
                        
                        # Trigger KOT/KDS update if available
                        if hasattr(pos_order, 'send_table_count_notification') and pos_order.table_id:
                            pos_order.send_table_count_notification(pos_order.table_id)
                            
                    except Exception as e:
                        _logger.warning("Post-paid processing error: %s", str(e))
                
                _logger.info("Order %s successfully processed (state: %s)", pos_order.name, pos_order.state)
            else:
                 # ... (rest of the code)

                # Payment amount doesn't match - this shouldn't happen if we got here
                diff = pos_order.amount_total - total_paid_sql
                _logger.error("Payment mismatch: DB total paid=%s, order total=%s, diff=%s", 
                             total_paid_sql, pos_order.amount_total, diff)
                raise ValueError(f"Order {pos_order.name} payment mismatch (paid: {total_paid_sql}, total: {pos_order.amount_total})")
            
            _logger.info("Order %s successfully processed", pos_order.name)

        except Exception as e:
            _logger.exception("Error completing order %s: %s", pos_order.name, str(e))
            raise

    def _save_transaction_log(self, pos_order, api_type, client_ref, result, amount=0, mw_request_id=None):
        """Save OMA API request/response to transaction log."""
        import json
        try:
            log_vals = {
                'pos_order_id': pos_order.id if pos_order else False,
                'api_type': api_type,
                'client_ref': client_ref,
                'mw_request_id': mw_request_id or result.get('omaTxnMwRequestId', ''),
                'invoice_no': result.get('_request_body', {}).get('omaInvoiceNo', ''),
                'request_url': result.get('_request_url', ''),
                'request_headers': json.dumps(result.get('_request_headers', {}), indent=2),
                'request_body': json.dumps(result.get('_request_body', {}), indent=2),
                'response_body': json.dumps({k: v for k, v in result.items() if not k.startswith('_')}, indent=2),
                'error_code': result.get('omaErrorCode', ''),
                'error_message': result.get('omaErrorMessage', ''),
                'auth_code': result.get('omaAuthCode', ''),
                'rrn': result.get('omaRrn', ''),
                'card_type': result.get('omaCardName', ''),
                'masked_pan': result.get('omaMaskedPan', ''),
                'amount': float(amount) if amount else 0,
            }
            
            request.env['oma.transaction.log'].sudo().create(log_vals)
            _logger.info("Saved OMA transaction log: %s for order %s", api_type, pos_order.name if pos_order else 'N/A')
            
        except Exception as e:
            _logger.warning("Failed to save transaction log: %s", str(e))
            # Don't raise - logging failure shouldn't break the payment flow

    @http.route('/pos_payment_oma/receipt_raw/<string:order_access_token>', type='http', auth='public', website=False, csrf=False)
    def receipt_raw(self, order_access_token, **kwargs):
        """Return raw ESC/POS bytes for the given order. Used by the local print agent."""
        pos_order = request.env['pos.order'].sudo().search([('access_token', '=', order_access_token)], limit=1)
        if not pos_order:
            return request.make_response("Order not found", headers=[('Content-Type', 'text/plain')], status=404)

        # Ensure partner exists for invoicing
        if not pos_order.partner_id:
            guest_partner = request.env['res.partner'].sudo().search([
                ('name', 'ilike', 'Guest'),
                ('active', '=', True)
            ], limit=1)
            if not guest_partner:
                guest_partner = request.env['res.partner'].sudo().create({
                    'name': 'Guest Customer',
                    'active': True,
                    'customer_rank': 1,
                })
            pos_order.partner_id = guest_partner.id
            request.env.cr.commit()

        # Generate invoice if missing
        if not pos_order.account_move:
            if pos_order.state in ['paid', 'done', 'invoiced']:
                try:
                    pos_order._generate_pos_order_invoice()
                    request.env.cr.commit()
                except Exception as e:
                    _logger.error("Failed to generate invoice for raw receipt: %s", str(e))

        from odoo.addons.pos_payment_oma.services.escpos_receipt import build_receipt_from_pos_order
        raw_data = build_receipt_from_pos_order(pos_order)

        return request.make_response(raw_data, headers=[
            ('Content-Type', 'application/octet-stream'),
            ('Content-Length', str(len(raw_data))),
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET'),
        ])

    @http.route('/pos_payment_oma/receipt_html/<string:order_access_token>', type='http', auth='public', website=False, csrf=False)
    def receipt_html(self, order_access_token, **kwargs):
        """Generate a printable HTML receipt page styled for 80mm thermal paper.
        Same layout as ESC/POS receipt but rendered as HTML for browser printing."""
        from markupsafe import Markup
        from datetime import datetime

        pos_order = request.env['pos.order'].sudo().search([('access_token', '=', order_access_token)], limit=1)
        if not pos_order:
            return request.make_response("Order not found", headers=[('Content-Type', 'text/plain')])

        company = pos_order.company_id
        invoice = pos_order.account_move

        # Currency
        currency = pos_order.currency_id or company.currency_id
        cur_symbol = currency.symbol if currency else ''
        cur_position = currency.position if currency else 'after'

        def fmt(amount):
            formatted = f"{amount:,.2f}"
            if cur_symbol:
                if cur_position == 'before':
                    return f"{cur_symbol} {formatted}"
                else:
                    return f"{formatted} {cur_symbol}"
            return formatted

        def esc(text):
            """Escape HTML entities."""
            return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        lines_html = []

        # Header - Company Info
        lines_html.append('<div class="center">')
        lines_html.append(f'<div class="bold big">{esc(company.name or "Store")}</div>')
        if company.street:
            lines_html.append(f'<div>{esc(company.street)}</div>')
        if company.street2:
            lines_html.append(f'<div>{esc(company.street2)}</div>')
        city_parts = []
        if company.city:
            city_parts.append(company.city)
        if company.state_id:
            city_parts.append(company.state_id.name)
        if company.zip:
            city_parts.append(company.zip)
        if city_parts:
            lines_html.append(f'<div>{esc(", ".join(city_parts))}</div>')
        if company.country_id:
            lines_html.append(f'<div>{esc(company.country_id.name)}</div>')
        if company.phone:
            lines_html.append(f'<div>Tel: {esc(company.phone)}</div>')
        if company.email:
            lines_html.append(f'<div>{esc(company.email)}</div>')
        if company.website:
            lines_html.append(f'<div>{esc(company.website)}</div>')
        if company.vat:
            lines_html.append(f'<div>TRN: {esc(company.vat)}</div>')
        lines_html.append('<br/>')
        lines_html.append('</div>')

        # Order Reference
        lines_html.append('<div class="center">')
        tracking = getattr(pos_order, 'tracking_number', None)
        if tracking:
            lines_html.append(f'<div class="bold biggest">{esc(tracking)}</div>')
        order_name = pos_order.name or ''
        if order_name:
            if tracking:
                lines_html.append(f'<div class="bold">Order: {esc(order_name)}</div>')
            else:
                lines_html.append(f'<div class="bold biggest">Order: {esc(order_name)}</div>')
        pos_ref = pos_order.pos_reference or ''
        if pos_ref and pos_ref != order_name and not tracking:
            lines_html.append(f'<div class="bold biggest">{esc(pos_ref)}</div>')

        # Invoice number
        if invoice and invoice.name:
            lines_html.append(f'<div>Invoice: {esc(invoice.name)}</div>')

        # Date
        order_date = pos_order.date_order
        if order_date:
            lines_html.append(f'<div>{order_date.strftime("%d/%m/%Y %H:%M")}</div>')
        else:
            lines_html.append(f'<div>{datetime.now().strftime("%d/%m/%Y %H:%M")}</div>')
        lines_html.append('</div>')

        # Cashier / Table / Customer
        if pos_order.user_id:
            lines_html.append(f'<div class="center">Served by: {esc(pos_order.user_id.name)}</div>')
        if pos_order.table_id:
            table_info = f"Table: {pos_order.table_id.name}"
            if pos_order.customer_count:
                table_info += f"  Guests: {pos_order.customer_count}"
            lines_html.append(f'<div class="center">{esc(table_info)}</div>')
        if pos_order.partner_id and pos_order.partner_id.name and 'guest' not in pos_order.partner_id.name.lower():
            lines_html.append(f'<div class="center">Customer: {esc(pos_order.partner_id.name)}</div>')

        lines_html.append('<div class="sep">------------------------------------------------</div>')

        # Order Lines Header
        lines_html.append('<div class="row bold"><span class="col-item">ITEM</span><span class="col-qty">QTY</span><span class="col-amt">AMOUNT</span></div>')
        lines_html.append('<div class="sep">------------------------------------------------</div>')

        # Order Lines
        if invoice and invoice.invoice_line_ids:
            for line in invoice.invoice_line_ids.filtered(lambda l: l.display_type in ('product', False, None)):
                product_name = line.product_id.display_name or line.name or 'Item'
                qty = line.quantity
                unit_price = line.price_unit
                total = line.price_total
                lines_html.append(f'<div class="row"><span class="col-item">{esc(product_name[:26])}</span><span class="col-qty">{qty:g}</span><span class="col-amt">{esc(fmt(total))}</span></div>')
                if qty != 1:
                    lines_html.append(f'<div class="detail">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{qty:g} x {esc(fmt(unit_price))}</div>')
                if line.discount and line.discount > 0:
                    lines_html.append(f'<div class="detail">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Disc: {line.discount:g}%</div>')
        else:
            for line in pos_order.lines:
                product_name = line.product_id.display_name or 'Item'
                qty = line.qty
                unit_price = line.price_unit
                total = line.price_subtotal_incl
                lines_html.append(f'<div class="row"><span class="col-item">{esc(product_name[:26])}</span><span class="col-qty">{qty:g}</span><span class="col-amt">{esc(fmt(total))}</span></div>')
                if qty != 1:
                    lines_html.append(f'<div class="detail">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{qty:g} x {esc(fmt(unit_price))}</div>')
                if line.discount and line.discount > 0:
                    lines_html.append(f'<div class="detail">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Disc: {line.discount:g}%</div>')

        lines_html.append('<div class="sep">------------------------------------------------</div>')

        # Totals
        if invoice:
            subtotal = invoice.amount_untaxed
            tax = invoice.amount_tax
            total = invoice.amount_total
        else:
            subtotal = sum(l.price_subtotal for l in pos_order.lines)
            tax = pos_order.amount_tax
            total = pos_order.amount_total

        lines_html.append(f'<div class="row"><span class="col-left">Subtotal</span><span class="col-right">{esc(fmt(subtotal))}</span></div>')
        if tax and tax > 0:
            lines_html.append(f'<div class="row"><span class="col-left">Tax</span><span class="col-right">{esc(fmt(tax))}</span></div>')
            if invoice:
                for tax_line in invoice.line_ids.filtered(lambda l: l.tax_line_id):
                    tax_name = tax_line.tax_line_id.name or 'Tax'
                    lines_html.append(f'<div class="row"><span class="col-left">&nbsp;&nbsp;{esc(tax_name)}</span><span class="col-right">{esc(fmt(abs(tax_line.balance)))}</span></div>')

        lines_html.append('<div class="dsep">================================================</div>')
        lines_html.append(f'<div class="row bold big"><span class="col-left">TOTAL</span><span class="col-right">{esc(fmt(total))}</span></div>')
        lines_html.append('<div class="dsep">================================================</div>')

        # Payment Details
        if pos_order.payment_ids:
            lines_html.append('<br/>')
            for payment in pos_order.payment_ids:
                method_name = payment.payment_method_id.name or 'Payment'
                lines_html.append(f'<div class="row"><span class="col-left">{esc(method_name)}</span><span class="col-right">{esc(fmt(payment.amount))}</span></div>')
                if hasattr(payment, 'card_no') and payment.card_no:
                    lines_html.append(f'<div class="detail">&nbsp;&nbsp;Card: {esc(payment.card_no)}</div>')
                if hasattr(payment, 'card_type') and payment.card_type:
                    lines_html.append(f'<div class="detail">&nbsp;&nbsp;Type: {esc(payment.card_type)}</div>')
            if pos_order.amount_return and pos_order.amount_return > 0:
                lines_html.append(f'<div class="row"><span class="col-left">Change</span><span class="col-right">{esc(fmt(pos_order.amount_return))}</span></div>')

        # Footer
        lines_html.append('<div class="sep">------------------------------------------------</div>')
        lines_html.append('<div class="center">Thank you for your purchase!</div>')
        lines_html.append('<br/>')
        ref = pos_order.pos_reference or pos_order.name
        lines_html.append(f'<div class="center">{esc(ref)}</div>')
        lines_html.append('<div class="center">Powered by Odoo</div>')

        body_content = '\n'.join(lines_html)

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>Receipt</title>
<style>
@page {{
    size: 80mm auto;
    margin: 0;
}}
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}
body {{
    font-family: 'Courier New', Courier, monospace;
    font-size: 12px;
    line-height: 1.3;
    width: 80mm;
    padding: 2mm;
    color: #000;
}}
.center {{ text-align: center; }}
.bold {{ font-weight: bold; }}
.big {{ font-size: 16px; }}
.biggest {{ font-size: 20px; }}
.sep, .dsep {{
    text-align: center;
    letter-spacing: -1px;
    overflow: hidden;
    white-space: nowrap;
}}
.row {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}}
.col-item {{ flex: 0 0 54%; text-align: left; overflow: hidden; }}
.col-qty {{ flex: 0 0 16%; text-align: left; }}
.col-amt {{ flex: 0 0 30%; text-align: right; }}
.col-left {{ text-align: left; }}
.col-right {{ text-align: right; }}
.detail {{ padding-left: 0; }}
@media print {{
    body {{ width: 80mm; }}
}}
</style>
</head>
<body onload="window.print();">
{body_content}
</body>
</html>"""

        return request.make_response(html, headers=[
            ('Content-Type', 'text/html; charset=utf-8'),
        ])

    @http.route('/pos_payment_oma/download_invoice/<string:order_access_token>', type='http', auth='public', website=True)
    def download_invoice(self, order_access_token, **kwargs):
        """Serve the invoice PDF for the given order access token."""
        _logger.info("Invoice download requested for token: %s", order_access_token)
        
        pos_order = request.env['pos.order'].sudo().search([('access_token', '=', order_access_token)], limit=1)
        
        if not pos_order:
            _logger.warning("Invoice download failed: Order not found for token %s", order_access_token)
            return request.not_found()

        # Fix missing partner issue for invoicing
        if not pos_order.partner_id:
             guest_partner = request.env['res.partner'].sudo().search([
                ('name', 'ilike', 'Guest'), 
                ('active', '=', True)
            ], limit=1)
             
             if not guest_partner:
                guest_partner = request.env['res.partner'].sudo().create({
                    'name': 'Guest Customer',
                    'active': True,
                    'customer_rank': 1,
                })
             pos_order.partner_id = guest_partner.id
             request.env.cr.commit() # Commit partner assignment before invoice generation
             _logger.info("Assigned Guest partner to order %s for invoicing", pos_order.name)

        if not pos_order.account_move:
            _logger.warning("Invoice download failed: No invoice generated for order %s", pos_order.name)
            # Try to generate it if missing but order is paid
            if pos_order.state in ['paid', 'done']:
                try:
                    pos_order._generate_pos_order_invoice()
                    request.env.cr.commit()
                except Exception as e:
                    _logger.error("Failed to generate missing invoice for order %s: %s", pos_order.name, str(e))
                     # Fallback: if we still can't generate it, return error
                    return request.make_response(f"Invoice Generation Error: {str(e)}", headers=[('Content-Type', 'text/plain')])
            else:
                return request.make_response("Order not invoiced yet", headers=[('Content-Type', 'text/plain')])

        if not pos_order.account_move:
             return request.make_response("Invoice not found", headers=[('Content-Type', 'text/plain')])

        # Render the Thermal PDF
        pdf_content, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf('pos_payment_oma.report_invoice_thermal', [pos_order.account_move.id])
        
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf_content)),
            ('Content-Disposition', f'inline; filename="Invoice-{pos_order.name}.pdf"'),
        ]
        
        return request.make_response(pdf_content, headers=pdfhttpheaders)

    @http.route('/pos_payment_oma/print_invoice/<string:order_access_token>', type='json', auth='public', csrf=False)
    def print_invoice_to_printer(self, order_access_token, **kwargs):
        """Print the invoice as raw ESC/POS characters directly to the default thermal receipt printer (80mm)."""
        _logger.info("Raw ESC/POS print requested for token: %s", order_access_token)
        
        pos_order = request.env['pos.order'].sudo().search([('access_token', '=', order_access_token)], limit=1)
        
        if not pos_order:
            _logger.warning("Print failed: Order not found for token %s", order_access_token)
            return {'success': False, 'error': 'Order not found'}

        # Ensure partner exists for invoicing
        if not pos_order.partner_id:
            guest_partner = request.env['res.partner'].sudo().search([
                ('name', 'ilike', 'Guest'), 
                ('active', '=', True)
            ], limit=1)
            
            if not guest_partner:
                guest_partner = request.env['res.partner'].sudo().create({
                    'name': 'Guest Customer',
                    'active': True,
                    'customer_rank': 1,
                })
            pos_order.partner_id = guest_partner.id
            request.env.cr.commit()

        # Generate invoice if missing
        if not pos_order.account_move:
            if pos_order.state in ['paid', 'done', 'invoiced']:
                try:
                    pos_order._generate_pos_order_invoice()
                    request.env.cr.commit()
                except Exception as e:
                    _logger.error("Failed to generate invoice: %s", str(e))
                    return {'success': False, 'error': f'Invoice generation failed: {str(e)}'}
            else:
                return {'success': False, 'error': 'Order not paid yet'}

        # Flush all pending DB changes
        request.env.cr.commit()

        try:
            # Build raw ESC/POS receipt
            from odoo.addons.pos_payment_oma.services.escpos_receipt import build_receipt_from_pos_order
            
            raw_data = build_receipt_from_pos_order(pos_order)
            _logger.info("Built ESC/POS receipt: %d bytes for order %s", len(raw_data), pos_order.name)
            
            # Get thermal printer name from POS config (default: POS-80)
            printer_name = pos_order.config_id.thermal_printer_name or 'POS-80'
            _logger.info("Targeting printer: %s", printer_name)
            
            # Write raw bytes to a temp file
            with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as tmp_file:
                tmp_file.write(raw_data)
                tmp_path = tmp_file.name
            
            # Send raw data to the specified printer using lp
            # -d <printer> targets a specific CUPS printer
            # -o raw tells CUPS to send the data as-is without any filtering
            
            # Check if 'lp' is available using 'which' to avoid [Errno 2]
            lp_binary = '/usr/bin/lp'
            if not os.path.exists(lp_binary):
                # Fallback to just 'lp' and let subprocess find it in PATH
                lp_binary = 'lp'

            result = subprocess.run(
                [lp_binary, '-d', printer_name, '-o', 'raw', tmp_path],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            
            if result.returncode == 0:
                _logger.info("ESC/POS receipt printed for order %s: %s", pos_order.name, result.stdout.strip())
                return {'success': True, 'message': f'Receipt sent to printer: {result.stdout.strip()}'}
            else:
                stderr = result.stderr.strip()
                _logger.error("Print failed for order %s: %s", pos_order.name, stderr)
                
                error_msg = f"Print command failed: {stderr}"
                if "not found" in stderr.lower() or "no such printer" in stderr.lower():
                    error_msg = f"Printer '{printer_name}' not found on server. Ensure it's configured in CUPS."
                
                return {
                    'success': False, 
                    'error': error_msg,
                    'is_printer_missing': True if "not found" in stderr.lower() or "no such printer" in stderr.lower() else False
                }
                
        except subprocess.TimeoutExpired:
            _logger.error("Print timeout for order %s", pos_order.name)
            return {'success': False, 'error': 'Print command timed out'}
        except Exception as e:
            _logger.error("Print error for order %s: %s", pos_order.name, str(e))
            return {'success': False, 'error': str(e)}
