# -*- coding: utf-8 -*-
from odoo import models, fields, api
from io import BytesIO
import base64
import xlsxwriter
from odoo.exceptions import UserError

class FastMovingProductWizard(models.TransientModel):
    _name = 'fast.moving.product.wizard'
    _description = 'Fast Moving Product Report Wizard'

    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    branch_id = fields.Many2one('pos.config', string="Branch", required=True)

    def action_print_xls(self):

        if self.end_date < self.start_date:
            raise UserError("Please enter a valid date range — The End Date cannot be earlier than the Start Date.")

        start = self.start_date
        end = self.end_date

        pos_orders = self.env['pos.order'].search([
            ('config_id', '=', self.branch_id.id),
            ('date_order', '>=', start),
            ('date_order', '<=', end),
            ('state', 'in', ['paid', 'done']),
        ])

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        sheet = workbook.add_worksheet("Fast Moving Products")

        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter'
        })
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D0E3F5',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        center_format = workbook.add_format({'align': 'center', 'border': 1})
        text_format = workbook.add_format({'border': 1})
        qty_format = workbook.add_format({'border': 1, 'align': 'right'})
        money_format = workbook.add_format({'border': 1, 'num_format': '#,##0.00'})
        total_format = workbook.add_format({'bold': True, 'bg_color': '#FAD7A0', 'border': 1})
        total_money_format = workbook.add_format({
            'bold': True,
            'bg_color': '#FAD7A0',
            'border': 1,
            'num_format': '#,##0.00'
        })

        sheet.set_column('A:A', 12)
        sheet.set_column('B:B', 52)
        sheet.set_column('C:C', 12)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 18)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:G', 30)

        title = f"Best Selling Products Report: {self.branch_id.name} – {start} to {end}"
        sheet.merge_range('B2:J2', title, title_format)

        headers = ["SL No", "Product", "Qty", "Unit Price", "Total Value", "Branch", "Company"]
        for col, text in enumerate(headers):
            sheet.write(3, col, text, header_format)

        if not pos_orders:
            workbook.close()
            file_data = output.getvalue()
            output.close()
        else:
            lines = pos_orders.mapped('lines')

            product_data = {}

            for line in lines:
                p = line.product_id
                if p not in product_data:
                    product_data[p] = {
                        'qty': 0,
                        'unit_price': line.price_unit,
                        'total': 0,
                        'branch': line.order_id.config_id.name,
                        'company': line.order_id.company_id.name,
                    }

                product_data[p]['qty'] += line.qty
                product_data[p]['total'] += line.qty * line.price_unit

            sorted_products = sorted(product_data.items(), key=lambda x: x[1]['qty'], reverse=True)

            row = 4
            sl = 1
            total_qty = 0
            total_value = 0

            for product, vals in sorted_products:
                sheet.write(row, 0, sl, center_format)
                sheet.write(row, 1, product.name, text_format)
                sheet.write(row, 2, vals['qty'], qty_format)
                sheet.write(row, 3, vals['unit_price'], money_format)
                sheet.write(row, 4, vals['total'], money_format)
                sheet.write(row, 5, vals['branch'], text_format)
                sheet.write(row, 6, vals['company'], text_format)

                total_qty += vals['qty']
                total_value += vals['total']
                row += 1
                sl += 1

            sheet.write(row, 1, "TOTAL", total_format)
            sheet.write(row, 2, total_qty, total_format)
            sheet.write(row, 4, total_value, total_money_format)

            workbook.close()
            file_data = output.getvalue()
            output.close()

        clean_branch = self.branch_id.name.replace(" ", "_")
        file_name = f"Best_Selling_Products_{clean_branch}_{start}_to_{end}.xlsx"

        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'type': 'binary',
            'datas': base64.b64encode(file_data),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
            'close_on_report_download': True,
        }
