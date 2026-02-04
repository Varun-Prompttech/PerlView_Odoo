# -*- coding: utf-8 -*-
"""
OMA Payment Service

Handles API communication with OMA RPS for payment processing.
No longer uses encryption - sends plain JSON payloads with static secret key header.
"""
import json
import logging
import requests

_logger = logging.getLogger(__name__)


class OMAService:
    def __init__(self, api_endpoint, merchant_id, terminal_id, key_version, institute, serial_number, secret_key=None):
        self.api_endpoint = api_endpoint.rstrip('/') if api_endpoint else ''
        self.merchant_id = merchant_id
        self.terminal_id = terminal_id
        self.key_version = key_version
        self.institute = institute
        self.serial_number = serial_number
        self.secret_key = secret_key  # Static secret key from config

    def initiate_transaction(self, amount, order_ref, order_id=None):
        """
        Initiate Sale Transaction (T001).
        
        Args:
            amount: Transaction amount (in major units, e.g., 17.00)
            order_ref: Order reference number (omaTxnClientRefNumber)
            order_id: Order ID (omaInvoiceNo), defaults to order_ref if not provided
        """
        if not self.api_endpoint:
            return {'omaErrorCode': '999', 'omaErrorMessage': 'API Endpoint not configured'}
            
        url = f"{self.api_endpoint}/api/client/txn"
        
        try:
            headers = {
                'omaMid': str(self.merchant_id),
                'omaKeyVersion': str(self.key_version),
                'omaSecretKey': str(self.secret_key) if self.secret_key else '',
                'omaInstitute': str(self.institute),
                'omaTerminalid': str(self.terminal_id),  # Note: lowercase 'id' as per sample
                'omaSerialNumber': str(self.serial_number),
                'Content-Type': 'application/json'
            }
            
            # Amount in minor units (cents) - e.g., 9.00 AED = "900"
            # Fix floating point precision issues (e.g. 17.83 * 100 might be 1782.999 -> 1782)
            amount_minor = str(int(round(float(amount) * 100)))
            
            # Plain JSON payload as per user sample
            body = {
                "omaAmount": amount_minor,
                "omaInvoiceNo": str(order_id) if order_id else str(order_ref),
                "omaMerchantId": str(self.merchant_id),
                "omaPayload": "",  # Empty as per sample
                "omaRRN": "",  # Empty or can be generated
                "omaTerminalId": str(self.terminal_id),
                "omaTipAmount": "0",  # User requested 0
                "omaTxnClientRefNumber": str(order_ref),
                "omaTxnType": "T001",
                "omaSerialNumber": str(self.serial_number),
                "omaclientid": ""  # Empty as per sample
            }
            
            _logger.info(f"OMA API Request: {url}")
            _logger.info(f"OMA Headers: omaMid={self.merchant_id}, omaKeyVersion={self.key_version}, omaInstitute={self.institute}")
            _logger.info(f"OMA Body: {body}")
            
            response = requests.post(url, json=body, headers=headers, timeout=30, verify=False)
            response.raise_for_status()
            result = response.json()
            _logger.info(f"OMA Initiate Response: {result}")
            
            # Add request details to result for logging
            result['_request_url'] = url
            result['_request_headers'] = {k: v for k, v in headers.items() if k != 'omaSecretKey'}  # Don't log secret
            result['_request_body'] = body
            
            return result
            
        except Exception as e:
            _logger.error(f"OMA Initiation Error: {e}")
            return {
                'omaErrorCode': '999', 
                'omaErrorMessage': str(e),
                '_request_url': url if 'url' in locals() else '',
                '_request_headers': {},
                '_request_body': body if 'body' in locals() else {}
            }

    def check_status(self, client_ref, mw_request_id):
        """Check transaction status (Inquiry)."""
        url = f"{self.api_endpoint}/api/client/txnInquiry"
        
        try:
            headers = {
                'omaMid': str(self.merchant_id),
                'omaKeyVersion': str(self.key_version),
                'omaSecretKey': str(self.secret_key) if self.secret_key else '',
                'omaInstitute': str(self.institute),
                'omaTerminalid': str(self.terminal_id),
                'omaSerialNumber': str(self.serial_number),
                'Content-Type': 'application/json'
            }
            
            # Body as per user's Postman sample - includes omaMerchantId
            body = {
                "omaMerchantId": str(self.merchant_id),
                "omaPayload": "",
                "omaTerminalId": str(self.terminal_id),
                "omaTxnMwRequestId": str(mw_request_id),
                "omaTxnClientRefNumber": str(client_ref)
            }
            
            _logger.info(f"OMA Inquiry Request: {url}")
            _logger.info(f"OMA Inquiry Body: {body}")
            
            response = requests.post(url, json=body, headers=headers, timeout=30, verify=False)
            response.raise_for_status()
            result = response.json()
            _logger.info(f"OMA Inquiry Response: {result}")
            
            # Add request details to result for logging
            result['_request_url'] = url
            result['_request_headers'] = {k: v for k, v in headers.items() if k != 'omaSecretKey'}
            result['_request_body'] = body
            
            return result
            
        except Exception as e:
            _logger.error(f"OMA Inquiry Error: {e}")
            return {
                'omaErrorCode': '999', 
                'omaErrorMessage': str(e),
                '_request_url': url if 'url' in locals() else '',
                '_request_headers': {},
                '_request_body': body if 'body' in locals() else {}
            }

    def get_session_key(self):
        """
        Generate Session Key and UID.
        Endpoint: /api/auth/pos/getSession
        """
        if not self.api_endpoint:
            return {'omaErrorCode': '999', 'omaErrorMessage': 'API Endpoint not configured'}
            
        url = f"{self.api_endpoint}/api/auth/pos/getSession"
        
        try:
            headers = {
                'omaInstitute': str(self.institute),
                'omaRereg': 'false', 
                'Content-Type': 'application/json'
            }
            
            body = {
                "omaSerialNumber": str(self.serial_number),
                "omaTerminalId": str(self.terminal_id)
            }
            
            _logger.info(f"OMA Session Gen Request: {url} | Body: {body}")
            
            response = requests.post(url, json=body, headers=headers, timeout=30, verify=False)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            _logger.error(f"OMA Session Gen Error: {e}")
            return {'omaErrorCode': '999', 'omaErrorMessage': str(e)}
