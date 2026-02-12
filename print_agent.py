#!/usr/bin/env python3
"""
PerlView Local Print Agent (Windows + Linux)
=============================================
A tiny HTTP server that runs on your LOCAL machine (where the thermal printer
is connected). It receives raw ESC/POS data from the browser and sends it
to the local printer.

Usage (Windows):
    python print_agent.py                          # Uses default printer
    python print_agent.py --printer "POS-80"       # Specify printer name
    python print_agent.py --port 9632              # Specify port (default 9632)

Usage (Linux):
    python3 print_agent.py --printer POS-80

Install requirement (Windows only):
    pip install pywin32

The kiosk browser JavaScript will POST raw print data to:
    http://localhost:9632/print
"""

import argparse
import sys
import os
import platform
from http.server import HTTPServer, BaseHTTPRequestHandler

IS_WINDOWS = platform.system() == 'Windows'


def print_raw_windows(printer_name, raw_data):
    """Send raw bytes to a Windows printer using win32print."""
    import win32print
    import win32con

    if not printer_name:
        printer_name = win32print.GetDefaultPrinter()
        print(f"[PRINT] Using default printer: {printer_name}")

    hPrinter = win32print.OpenPrinter(printer_name)
    try:
        # Start a raw print job
        hJob = win32print.StartDocPrinter(hPrinter, 1, ("ESC/POS Receipt", None, "RAW"))
        try:
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, raw_data)
            win32print.EndPagePrinter(hPrinter)
        finally:
            win32print.EndDocPrinter(hPrinter)
    finally:
        win32print.ClosePrinter(hPrinter)

    return f"Sent {len(raw_data)} bytes to {printer_name}"


def print_raw_linux(printer_name, raw_data):
    """Send raw bytes to a Linux printer using lp."""
    import subprocess
    import tempfile

    with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as tmp:
        tmp.write(raw_data)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            ['lp', '-d', printer_name, '-o', 'raw', tmp_path],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            raise Exception(result.stderr.strip())
        return result.stdout.strip()
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


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
            printer = self.server.printer_name or "default"
            self.wfile.write(f'{{"status":"running","printer":"{printer}","os":"{platform.system()}"}}'.encode())
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
            print(f"[PRINT] Received {len(raw_data)} bytes, sending to printer: {printer or 'default'}")

            if IS_WINDOWS:
                msg = print_raw_windows(printer, raw_data)
            else:
                if not printer:
                    printer = 'POS-80'
                msg = print_raw_linux(printer, raw_data)

            print(f"[PRINT] Success: {msg}")
            msg_escaped = msg.replace('"', '\\"')
            self._send_json(200, f'{{"success":true,"message":"{msg_escaped}"}}')

        except Exception as e:
            err = str(e).replace('"', '\\"').replace('\n', ' ')
            print(f"[PRINT] Error: {err}")
            self._send_json(500, f'{{"success":false,"error":"{err}"}}')

    def _send_json(self, status, body):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body.encode())

    def log_message(self, format, *args):
        print(f"[HTTP] {args[0]}")


def list_windows_printers():
    """List all available printers on Windows."""
    try:
        import win32print
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        default = win32print.GetDefaultPrinter()
        print("\nAvailable printers:")
        for _, _, name, _ in printers:
            marker = " <-- DEFAULT" if name == default else ""
            print(f"  - {name}{marker}")
        print()
        return default
    except ImportError:
        print("\n[ERROR] pywin32 is required on Windows. Install it with:")
        print("    pip install pywin32\n")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='PerlView Local Print Agent')
    parser.add_argument('--printer', default='', help='Printer name (default: system default on Windows, POS-80 on Linux)')
    parser.add_argument('--port', type=int, default=9632, help='Port to listen on (default: 9632)')
    args = parser.parse_args()

    if IS_WINDOWS:
        default_printer = list_windows_printers()
        if not args.printer:
            args.printer = default_printer
            print(f"[INFO] No --printer specified, using default: {default_printer}")

    printer_display = args.printer or 'POS-80'

    server = HTTPServer(('0.0.0.0', args.port), PrintHandler)
    server.printer_name = args.printer

    print(f"{'='*50}")
    print(f"  PerlView Local Print Agent")
    print(f"{'='*50}")
    print(f"  OS      : {platform.system()}")
    print(f"  Printer : {printer_display}")
    print(f"  Port    : {args.port}")
    print(f"  URL     : http://localhost:{args.port}/print")
    print(f"{'='*50}")
    print(f"  Press Ctrl+C to stop")
    print(f"{'='*50}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[STOP] Print agent stopped.")
        server.server_close()


if __name__ == '__main__':
    main()
