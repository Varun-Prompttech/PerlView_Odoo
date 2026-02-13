from odoo import models, fields
from datetime import datetime
from pytz import timezone, UTC
import logging

_logger = logging.getLogger(__name__)

class ReportZWalkers(models.AbstractModel):
    _name = 'report.pt_walkers_z_report.report_z_walkers'

    def _get_report_values(self, docids, data=None):
        data = data or {}
        if not data.get('config_id'):
            raise ValueError("Missing 'config_id' in report data/context")

        report = self.env['ir.actions.report']._get_report_from_name('pt_walkers_z_report.report_z_walkers')

        lines = {
            'sales_summary': self.get_sales_summary(data),
            'payment_details': self.get_payment_details(data),
            'category_details': self.get_category_details(data),
        }

        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self.env[report.model].browse(docids),
            'date_start': self.get_datetime_conversion(data['date_start']),
            'date_stop': self.get_datetime_conversion(data['date_stop']),
            'branches': self.get_branches(data),
            'lines': lines,
        }

    def get_datetime_conversion(self, date_str):
        date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        user_tz = timezone(self.env.user.tz or 'UTC')
        return UTC.localize(date).astimezone(user_tz).strftime('%d-%m-%Y %I:%M:%S %p')

    def get_sales_summary(self, data):
        ids = tuple(data['config_id']) if len(data['config_id']) > 1 else f"({data['config_id'][0]})"
        self.env.cr.execute(f"""
            SELECT 'POS', COUNT(po.id), COALESCE(SUM(po.amount_total), 0)
            FROM pos_order po
            JOIN pos_config pc ON po.config_id = pc.id
            WHERE po.date_order >= %s AND po.date_order <= %s AND pc.id IN {ids}
        """, (data['date_start'], data['date_stop']))
        return [{'sales_type': row[0], 'bill_count': row[1], 'amount': '%.2f' % row[2]} for row in self.env.cr.fetchall()]

    def get_payment_details(self, data):
        ids = tuple(data['config_id']) if len(data['config_id']) > 1 else f"({data['config_id'][0]})"
        self.env.cr.execute(f"""
            SELECT pm.name, SUM(pp.amount)
            FROM pos_payment pp
            JOIN pos_order po ON pp.pos_order_id = po.id
            JOIN pos_config pc ON po.config_id = pc.id
            JOIN pos_payment_method pm ON pp.payment_method_id = pm.id
            WHERE po.date_order >= %s AND po.date_order <= %s AND pc.id IN {ids}
            GROUP BY pm.name
        """, (data['date_start'], data['date_stop']))
        return [{'payment_method': row[0] if not isinstance(row[0], dict) else list(row[0].values())[0],
                 'amount': '%.2f' % row[1]} for row in self.env.cr.fetchall()]

    def get_category_details(self, data):
        ids = tuple(data['config_id']) if len(data['config_id']) > 1 else f"({data['config_id'][0]})"
        self.env.cr.execute(f"""
            SELECT posc.name, SUM(pol.qty * pol.price_unit)
            FROM pos_order_line pol
            JOIN pos_order po ON pol.order_id = po.id
            JOIN product_product pp ON pol.product_id = pp.id
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            JOIN pos_config pc ON po.config_id = pc.id
            LEFT JOIN product_category posc ON pt.categ_id = posc.id
            WHERE po.date_order >= %s AND po.date_order <= %s AND pc.id IN {ids}
            GROUP BY posc.name
        """, (data['date_start'], data['date_stop']))
        return [{'category': row[0] or 'Not Categorized', 'amount': '%.2f' % row[1]} for row in self.env.cr.fetchall()]

    def get_branches(self, data):
        return ', '.join(self.env['pos.config'].browse(data['config_id']).mapped('name'))
