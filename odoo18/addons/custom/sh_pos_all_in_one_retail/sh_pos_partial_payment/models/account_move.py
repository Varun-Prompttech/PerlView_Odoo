# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_invoice_pdf_report_attachment(self):
        pdf_content = self.env['ir.actions.report']._render('account.account_invoices', self.ids)[0]
        pdf_name = self._get_invoice_report_filename() if len(self) == 1 else "Invoices.pdf"
        return pdf_content, pdf_name
    