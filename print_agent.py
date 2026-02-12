#!/usr/bin/env python3
"""
PerlView Local Print Agent
===========================
A tiny HTTP server that runs on your LOCAL machine (where the thermal printer
is connected). It receives raw ESC/POS data from the browser and sends it
to the local printer via `lp`.

Usage:
    python3 print_agent.py                        # Uses default printer POS-80
    python3 print_agent.py --printer POS-80       # Specify printer name
    python3 print_agent.py --port 9632            # Specify port (default 9632)

The kiosk browser JavaScript will POST raw print data to:
    http://localhost:9632/print

Requirements:
    - Python 3 (no extra packages needed)
    - CUPS with your thermal printer configured
    - The printer must accept raw ESC/POS data via `lp -o raw`
"""

import argparse
import subprocess
import tempfile
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler


class PrintHandler(BaseHTTPRequestHandler):
    """Handle incoming print requests from the kiosk browser."""

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """Health check endpoint."""
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            printer = self.server.printer_name
            self.wfile.write(f'{{"status":"running","printer":"{printer}"}}'.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """Receive raw ESC/POS data and send to local printer."""
        if self.path != '/print':
            self.send_response(404)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            return

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            raw_data = self.rfile.read(content_length)

            if not raw_data:
                self._send_json(400, '{"success":false,"error":"No data received"}')
                return

            printer = self.server.printer_name
            print(f"[PRINT] Received {len(raw_data)} bytes, sending to printer: {printer}")

            # Write raw data to temp file
            with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as tmp:
                tmp.write(raw_data)
                tmp_path = tmp.name

            # Send to printer using lp
            result = subprocess.run(
                ['lp', '-d', printer, '-o', 'raw', tmp_path],
                capture_output=True,
                text=True,
                timeout=15
            )

            # Clean up
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

            if result.returncode == 0:
                msg = result.stdout.strip()
                print(f"[PRINT] Success: {msg}")
                self._send_json(200, f'{{"success":true,"message":"{msg}"}}')
            else:
                err = result.stderr.strip().replace('"', '\\"')
                print(f"[PRINT] Failed: {err}")
                self._send_json(500, f'{{"success":false,"error":"{err}"}}')

        except subprocess.TimeoutExpired:
            self._send_json(500, '{"success":false,"error":"Print command timed out"}')
        except Exception as e:
            err = str(e).replace('"', '\\"')
            print(f"[PRINT] Error: {err}")
            self._send_json(500, f'{{"success":false,"error":"{err}"}}')

    def _send_json(self, status, body):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body.encode())

    def log_message(self, format, *args):
        """Quieter logging."""
        print(f"[HTTP] {args[0]}")


def main():
    parser = argparse.ArgumentParser(description='PerlView Local Print Agent')
    parser.add_argument('--printer', default='POS-80', help='Printer name (default: POS-80)')
    parser.add_argument('--port', type=int, default=9632, help='Port to listen on (default: 9632)')
    args = parser.parse_args()

    server = HTTPServer(('0.0.0.0', args.port), PrintHandler)
    server.printer_name = args.printer

    print(f"╔════════════════════════════════════════════╗")
    print(f"║   PerlView Local Print Agent               ║")
    print(f"╠════════════════════════════════════════════╣")
    print(f"║   Printer : {args.printer:<30}║")
    print(f"║   Port    : {args.port:<30}║")
    print(f"║   URL     : http://localhost:{args.port}/print    ║")
    print(f"╠════════════════════════════════════════════╣")
    print(f"║   Press Ctrl+C to stop                     ║")
    print(f"╚════════════════════════════════════════════╝")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[STOP] Print agent stopped.")
        server.server_close()


if __name__ == '__main__':
    main()
