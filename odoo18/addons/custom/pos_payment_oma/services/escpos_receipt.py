# -*- coding: utf-8 -*-
"""
ESC/POS Raw Receipt Formatter for 80mm Thermal Printers.

Builds raw ESC/POS byte commands character-by-character for direct
printing to thermal receipt printers. No PDF rendering involved.

Standard 80mm thermal printer: 48 characters per line (Font A).
"""

import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

# ─── ESC/POS Command Constants ───────────────────────────────────────────────
ESC = b'\x1b'
GS = b'\x1d'

# Printer initialization
INIT = ESC + b'\x40'  # ESC @ - Initialize printer

# Text alignment
ALIGN_LEFT = ESC + b'\x61\x00'    # ESC a 0
ALIGN_CENTER = ESC + b'\x61\x01'  # ESC a 1
ALIGN_RIGHT = ESC + b'\x61\x02'   # ESC a 2

# Text emphasis
BOLD_ON = ESC + b'\x45\x01'   # ESC E 1
BOLD_OFF = ESC + b'\x45\x00'  # ESC E 0

# Underline
UNDERLINE_ON = ESC + b'\x2d\x01'   # ESC - 1
UNDERLINE_OFF = ESC + b'\x2d\x00'  # ESC - 0

# Text size (using ESC ! n)
# Bit 0: Font B (0=A, 1=B)
# Bit 3: Emphasized/Bold
# Bit 4: Double height
# Bit 5: Double width
SIZE_NORMAL = ESC + b'\x21\x00'       # Normal (Font A)
SIZE_DOUBLE_HEIGHT = ESC + b'\x21\x10'  # Double height
SIZE_DOUBLE_WIDTH = ESC + b'\x21\x20'   # Double width
SIZE_DOUBLE = ESC + b'\x21\x30'         # Double height + width

# Line spacing
LINE_SPACING_DEFAULT = ESC + b'\x32'          # ESC 2 - default
LINE_SPACING_SET = lambda n: ESC + b'\x33' + bytes([n])  # ESC 3 n

# Paper cut
CUT_FULL = GS + b'\x56\x00'      # GS V 0 - Full cut
CUT_PARTIAL = GS + b'\x56\x01'   # GS V 1 - Partial cut
CUT_FEED_FULL = GS + b'\x56\x41\x03'   # GS V A 3 - Feed & full cut
CUT_FEED_PARTIAL = GS + b'\x56\x42\x03'  # GS V B 3 - Feed & partial cut

# Feed
FEED_LINES = lambda n: ESC + b'\x64' + bytes([n])  # ESC d n - Feed n lines

# Horizontal line character
LINE_CHAR = '-'
DOUBLE_LINE_CHAR = '='

# Paper width in characters (80mm, Font A = 48 chars)
PAPER_WIDTH = 48


class ESCPOSReceipt:
    """Builds a raw ESC/POS receipt byte stream for an 80mm thermal printer."""

    def __init__(self, width=PAPER_WIDTH):
        self.width = width
        self._buffer = bytearray()
        self._buffer.extend(INIT)

    # ─── Low-level helpers ────────────────────────────────────────────────

    def _write(self, data):
        """Append raw bytes to the buffer."""
        if isinstance(data, str):
            self._buffer.extend(data.encode('utf-8', errors='replace'))
        else:
            self._buffer.extend(data)

    def _writeln(self, text=''):
        """Write a line of text followed by newline."""
        if isinstance(text, str):
            self._buffer.extend(text.encode('utf-8', errors='replace'))
        else:
            self._buffer.extend(text)
        self._buffer.extend(b'\n')

    # ─── Formatting helpers ───────────────────────────────────────────────

    def align_center(self):
        self._write(ALIGN_CENTER)
        return self

    def align_left(self):
        self._write(ALIGN_LEFT)
        return self

    def align_right(self):
        self._write(ALIGN_RIGHT)
        return self

    def bold_on(self):
        self._write(BOLD_ON)
        return self

    def bold_off(self):
        self._write(BOLD_OFF)
        return self

    def size_normal(self):
        self._write(SIZE_NORMAL)
        return self

    def size_double(self):
        self._write(SIZE_DOUBLE)
        return self

    def size_double_height(self):
        self._write(SIZE_DOUBLE_HEIGHT)
        return self

    def size_double_width(self):
        self._write(SIZE_DOUBLE_WIDTH)
        return self

    def feed(self, lines=1):
        self._write(FEED_LINES(lines))
        return self

    def cut(self):
        self._write(CUT_FEED_PARTIAL)
        return self

    # ─── Text layout helpers ──────────────────────────────────────────────

    def line(self, char=LINE_CHAR):
        """Print a full-width separator line."""
        self._writeln(char * self.width)
        return self

    def double_line(self):
        """Print a full-width double separator line."""
        self._writeln(DOUBLE_LINE_CHAR * self.width)
        return self

    def text_center(self, text):
        """Print centered text."""
        self._write(ALIGN_CENTER)
        self._writeln(str(text))
        self._write(ALIGN_LEFT)
        return self

    def text_left(self, text):
        """Print left-aligned text."""
        self._write(ALIGN_LEFT)
        self._writeln(str(text))
        return self

    def text_right(self, text):
        """Print right-aligned text."""
        self._write(ALIGN_RIGHT)
        self._writeln(str(text))
        self._write(ALIGN_LEFT)
        return self

    def text_left_right(self, left, right):
        """Print text with left part and right part on the same line."""
        left = str(left)
        right = str(right)
        space = self.width - len(left) - len(right)
        if space < 1:
            # Text too long - truncate left side
            max_left = self.width - len(right) - 1
            if max_left > 0:
                left = left[:max_left]
                space = 1
            else:
                # Even right is too long, just print both on separate lines
                self._writeln(left)
                self._write(ALIGN_RIGHT)
                self._writeln(right)
                self._write(ALIGN_LEFT)
                return self
        self._write(ALIGN_LEFT)
        self._writeln(left + (' ' * space) + right)
        return self

    def text_columns(self, col1, col2, col3):
        """Print three columns (item, qty, amount)."""
        col1 = str(col1)
        col2 = str(col2)
        col3 = str(col3)
        # Allocate: col1(ITEM)=26 chars, col2(QTY)=8 chars, col3(AMOUNT)=14 chars
        c1_w = 26
        c2_w = 8
        c3_w = self.width - c1_w - c2_w

        col1 = col1[:c1_w].ljust(c1_w)
        col2 = col2[:c2_w].ljust(c2_w)
        col3 = col3[:c3_w].rjust(c3_w)

        self._write(ALIGN_LEFT)
        self._writeln(col1 + col2 + col3)
        return self

    def blank_line(self):
        self._writeln('')
        return self

    # ─── Get final output ─────────────────────────────────────────────────

    def get_bytes(self):
        """Return the complete receipt as bytes."""
        return bytes(self._buffer)


def format_currency(amount, currency_symbol='', position='after'):
    """Format a monetary amount for receipt display."""
    formatted = f"{amount:,.2f}"
    if currency_symbol:
        if position == 'before':
            return f"{currency_symbol} {formatted}"
        else:
            return f"{formatted} {currency_symbol}"
    return formatted


def build_receipt_from_pos_order(pos_order):
    """
    Build a raw ESC/POS receipt from a pos.order record.

    Args:
        pos_order: An Odoo pos.order recordset (sudo'd)

    Returns:
        bytes: Raw ESC/POS data ready to send to printer
    """
    receipt = ESCPOSReceipt()
    company = pos_order.company_id
    invoice = pos_order.account_move

    # Determine currency symbol and position
    currency = pos_order.currency_id or company.currency_id
    cur_symbol = currency.symbol if currency else ''
    cur_position = currency.position if currency else 'after'

    def fmt(amount):
        return format_currency(amount, cur_symbol, cur_position)

    # ═══════════════════════════════════════════════════════════════════════
    # HEADER - Company Info
    # ═══════════════════════════════════════════════════════════════════════
    receipt.align_center()
    receipt.bold_on()
    receipt.size_double_height()
    receipt._writeln(company.name or 'Store')
    receipt.size_normal()
    receipt.bold_off()

    if company.street:
        receipt._writeln(company.street)
    if company.street2:
        receipt._writeln(company.street2)
    city_parts = []
    if company.city:
        city_parts.append(company.city)
    if company.state_id:
        city_parts.append(company.state_id.name)
    if company.zip:
        city_parts.append(company.zip)
    if city_parts:
        receipt._writeln(', '.join(city_parts))
    if company.country_id:
        receipt._writeln(company.country_id.name)
    if company.phone:
        receipt._writeln(f"Tel: {company.phone}")
    if company.email:
        receipt._writeln(company.email)
    if company.website:
        receipt._writeln(company.website)
    if company.vat:
        receipt._writeln(f"TRN: {company.vat}")

    receipt.blank_line()
    receipt.align_left()

    # ═══════════════════════════════════════════════════════════════════════
    # ORDER REFERENCE / INVOICE NUMBER
    # ═══════════════════════════════════════════════════════════════════════
    receipt.align_center()
    receipt.bold_on()
    receipt.size_double()

    # Show tracking number prominently if available
    tracking = getattr(pos_order, 'tracking_number', None)
    if tracking:
        receipt._writeln(str(tracking))
    
    # Always show order name/number
    order_name = pos_order.name or ''
    pos_ref = pos_order.pos_reference or ''
    if order_name:
        # If tracking was shown, show order name in normal size below
        if tracking:
            receipt.size_normal()
            receipt.bold_on()
        receipt._writeln(f"Order: {order_name}")
    
    # Show POS reference if different from order name
    if pos_ref and pos_ref != order_name and not tracking:
        receipt._writeln(str(pos_ref))

    receipt.size_normal()
    receipt.bold_off()

    # Invoice number
    if invoice and invoice.name:
        receipt._writeln(f"Invoice: {invoice.name}")

    # Date/time
    order_date = pos_order.date_order
    if order_date:
        receipt._writeln(order_date.strftime('%d/%m/%Y %H:%M'))
    else:
        receipt._writeln(datetime.now().strftime('%d/%m/%Y %H:%M'))

    receipt.align_left()
    receipt.blank_line()

    # Cashier / Table
    if pos_order.user_id:
        receipt.text_center(f"Served by: {pos_order.user_id.name}")
    if pos_order.table_id:
        table_info = f"Table: {pos_order.table_id.name}"
        if pos_order.customer_count:
            table_info += f"  Guests: {pos_order.customer_count}"
        receipt.text_center(table_info)

    # Customer
    if pos_order.partner_id and pos_order.partner_id.name and 'guest' not in pos_order.partner_id.name.lower():
        receipt.text_center(f"Customer: {pos_order.partner_id.name}")

    receipt.line()

    # ═══════════════════════════════════════════════════════════════════════
    # ORDER LINES
    # ═══════════════════════════════════════════════════════════════════════
    receipt.bold_on()
    receipt.text_columns('ITEM', 'QTY', 'AMOUNT')
    receipt.bold_off()
    receipt.line()

    # Use invoice lines if available, otherwise pos order lines
    if invoice and invoice.invoice_line_ids:
        for line in invoice.invoice_line_ids.filtered(lambda l: l.display_type in ('product', False, None)):
            product_name = line.product_id.display_name or line.name or 'Item'
            qty = line.quantity
            unit_price = line.price_unit
            total = line.price_total

            # First row: Name, Qty, Total
            receipt.text_columns(
                product_name[:26],
                f"{qty:g}",
                fmt(total)
            )

            # Second row: unit price detail (indented)
            if qty != 1:
                receipt.text_left(f"      {qty:g} x {fmt(unit_price)}")

            # Discount
            if line.discount and line.discount > 0:
                receipt.text_left(f"      Disc: {line.discount:g}%")
    else:
        for line in pos_order.lines:
            product_name = line.product_id.display_name or 'Item'
            qty = line.qty
            unit_price = line.price_unit
            total = line.price_subtotal_incl

            receipt.text_columns(
                product_name[:26],
                f"{qty:g}",
                fmt(total)
            )

            if qty != 1:
                receipt.text_left(f"      {qty:g} x {fmt(unit_price)}")

            if line.discount and line.discount > 0:
                receipt.text_left(f"      Disc: {line.discount:g}%")

    receipt.line()

    # ═══════════════════════════════════════════════════════════════════════
    # TOTALS
    # ═══════════════════════════════════════════════════════════════════════
    if invoice:
        subtotal = invoice.amount_untaxed
        tax = invoice.amount_tax
        total = invoice.amount_total
    else:
        subtotal = sum(l.price_subtotal for l in pos_order.lines)
        tax = pos_order.amount_tax
        total = pos_order.amount_total

    receipt.text_left_right('Subtotal', fmt(subtotal))

    if tax and tax > 0:
        receipt.text_left_right('Tax', fmt(tax))

        # Show tax breakdown if invoice available
        if invoice:
            for tax_line in invoice.line_ids.filtered(lambda l: l.tax_line_id):
                tax_name = tax_line.tax_line_id.name or 'Tax'
                receipt.text_left_right(f"  {tax_name}", fmt(abs(tax_line.balance)))

    receipt.double_line()
    receipt.bold_on()
    receipt.size_double_height()
    receipt.text_left_right('TOTAL', fmt(total))
    receipt.size_normal()
    receipt.bold_off()
    receipt.double_line()

    # ═══════════════════════════════════════════════════════════════════════
    # PAYMENT DETAILS
    # ═══════════════════════════════════════════════════════════════════════
    if pos_order.payment_ids:
        receipt.blank_line()
        for payment in pos_order.payment_ids:
            method_name = payment.payment_method_id.name or 'Payment'
            receipt.text_left_right(method_name, fmt(payment.amount))

            # Show card details if available
            if hasattr(payment, 'card_no') and payment.card_no:
                receipt.text_left(f"  Card: {payment.card_no}")
            if hasattr(payment, 'card_type') and payment.card_type:
                receipt.text_left(f"  Type: {payment.card_type}")

        if pos_order.amount_return and pos_order.amount_return > 0:
            receipt.text_left_right('Change', fmt(pos_order.amount_return))

    receipt.blank_line()

    # ═══════════════════════════════════════════════════════════════════════
    # FOOTER
    # ═══════════════════════════════════════════════════════════════════════
    receipt.line()
    receipt.align_center()
    receipt._writeln('Thank you for your purchase!')
    receipt.blank_line()

    # POS Reference at bottom
    ref = pos_order.pos_reference or pos_order.name
    receipt._writeln(str(ref))

    receipt._writeln('Powered by Odoo')
    receipt.blank_line()

    # Feed and cut
    receipt.feed(4)
    receipt.cut()

    return receipt.get_bytes()
