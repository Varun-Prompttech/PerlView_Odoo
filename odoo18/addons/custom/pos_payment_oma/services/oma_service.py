# -*- coding: utf-8 -*-
import base64
import json
import logging
import uuid
import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

_logger = logging.getLogger(__name__)

class OMAService:
    def __init__(self, api_endpoint, merchant_id, api_key, aes_key, terminal_id, key_version, institute, serial_number):
        self.api_endpoint = api_endpoint.rstrip('/') if api_endpoint else ''
        self.merchant_id = merchant_id
        self.api_key = api_key
        self.aes_key = aes_key
        self.terminal_id = terminal_id
        self.key_version = key_version
        self.institute = institute
        self.serial_number = serial_number

    def _encrypt(self, plaintext):
        """Encrypt plaintext using AES-256-ECB."""
        if not self.aes_key:
            raise ValueError("AES Key is missing")
            
        try:
            key = base64.b64decode(self.aes_key)
        except Exception as e:
            raise ValueError(f"Invalid AES Key format: {e}")

        # PKCS7 Padding (AES block size is 128 bits)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext.encode('utf-8')) + padder.finalize()
        
        # AES ECB Encryption
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return base64.b64encode(ciphertext).decode('utf-8')

    def _generate_secret_key(self, random_number):
        """Generate omaSecretKey header."""
        # omaSecretKey = AES Encrypted data of(APIKey : mid : randomNumber) separated by ‘:’
        raw_key = f"{self.api_key}:{self.merchant_id}:{random_number}"
        return self._encrypt(raw_key)

    def initiate_transaction(self, amount, client_ref):
        """Initiate Sale Transaction (T001)."""
        if not self.api_endpoint:
            return {'omaErrorCode': '999', 'omaErrorMessage': 'API Endpoint not configured'}
            
        url = f"{self.api_endpoint}/api/client/txn"
        random_number = str(uuid.uuid4().int)[:6] # Short random
        
        try:
            secret_key = self._generate_secret_key(random_number)
            
            headers = {
                'omaMid': str(self.merchant_id),
                'omaKeyVersion': str(self.key_version),
                'omaSecretKey': secret_key,
                'omaInstitute': str(self.institute),
                'omaTerminalId': str(self.terminal_id),
                'omaSerialNumber': str(self.serial_number),
                'Content-Type': 'application/json'
            }
            
            # Payload
            payload_data = {
                "omaTxnType": "T001",
                "omaAmount": str(int(amount * 100)), # Minor currency units
                "omaTerminalId": self.terminal_id,
                "omaMerchantId": self.merchant_id,
                "omaTxnClientRefNumber": client_ref,
                "omaInvoiceNo": client_ref # Optional but recommended
            }
            
            json_payload = json.dumps(payload_data)
            encrypted_payload = self._encrypt(json_payload)
            
            body = {
                "omaPayload": encrypted_payload
            }
            
            _logger.info(f"OMA API Request: {url}")
            # _logger.info(f"OMA Headers: {headers}") # Security risk for logs?
            
            response = requests.post(url, json=body, headers=headers, timeout=30, verify=False)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            _logger.error(f"OMA Initiation Error: {e}")
            return {'omaErrorCode': '999', 'omaErrorMessage': str(e)}

    def check_status(self, client_ref, mw_request_id):
        """Check transaction status (Inquiry)."""
        url = f"{self.api_endpoint}/api/client/txnInquiry"
        random_number = str(uuid.uuid4().int)[:6]
        
        try:
            secret_key = self._generate_secret_key(random_number)
            
            headers = {
                'omaMid': str(self.merchant_id),
                'omaKeyVersion': str(self.key_version),
                'omaSecretKey': secret_key,
                'omaInstitute': str(self.institute),
                'omaTerminalId': str(self.terminal_id),
                'omaSerialNumber': str(self.serial_number),
                'Content-Type': 'application/json'
            }
            
            payload_data = {
                "omaTxnMwRequestId": mw_request_id,
                "omaTxnClientRefNumber": client_ref,
                "omaTerminalId": self.terminal_id
            }
             
            # Inquiry might also need encryption in body?
            # "Encrypted Sample Request: (for Encrypted version) { "omaPayload": ... }"
            # Yes, "Note : OmaPay load/Encrypted data must be a base64 encoded string."
            
            json_payload = json.dumps(payload_data)
            encrypted_payload = self._encrypt(json_payload)
            
            body = {
                "omaPayload": encrypted_payload
            }
            
            response = requests.post(url, json=body, headers=headers, timeout=30, verify=False)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            _logger.error(f"OMA Inquiry Error: {e}")
            return {'omaErrorCode': '999', 'omaErrorMessage': str(e)}
