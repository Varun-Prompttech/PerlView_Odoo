# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.tools import convert, SQL


class PosConfig(models.Model):
    _inherit = 'pos.config'

    limited_products_loading = fields.Boolean(string='Limited Product Loading',
                                              help="we load all starred products (favorite).\n"
                                                   "When the session is open, we keep on loading all remaining products in the background.\n",
                                              default=False)
    limited_product_count = fields.Integer(string="Number of Products Loaded", default=20000)
    product_load_background = fields.Boolean(default=False)

    def get_limited_product_count(self):
        default_limit = 20000
        config_param = self.limited_product_count if self.limited_products_loading and self.limited_product_count > 0 else default_limit
        try:
            return int(config_param)
        except (TypeError, ValueError, OverflowError):
            return default_limit

    def get_products_loading_in_background(self, fields, offset, limit):
        query = self.env['product.product']._where_calc(
            self._get_available_product_domain()
        )
        sql = SQL(
            """
            WITH pm AS (
                  SELECT product_id,
                         MAX(write_date) date
                    FROM stock_move_line
                GROUP BY product_id
            )
               SELECT product_product.id
                 FROM %s
            LEFT JOIN pm ON product_product.id=pm.product_id
                WHERE %s
             ORDER BY product_product__product_tmpl_id.is_favorite DESC,
                      CASE WHEN product_product__product_tmpl_id.type = 'service' THEN 1 ELSE 0 END DESC,
                      pm.date DESC NULLS LAST,
                      product_product.write_date DESC
                LIMIT %s
               OFFSET %s
            """,
            query.from_clause,
            query.where_clause or SQL("TRUE"),
            int(limit),
            int(offset),  # Added offset parameter here
        )
        product_ids = [r[0] for r in self.env.execute_query(sql)]
        special_products = self._get_special_products().filtered(
            lambda product: not product.sudo().company_id
                            or product.sudo().company_id == self.company_id
        )
        # product_ids.extend(special_products.ids)
        products = self.env['product.product'].browse(product_ids)
        product_combo = products.filtered(lambda p: p['type'] == 'combo')
        product_in_combo = product_combo.combo_ids.combo_item_ids.product_id
        products_available = products | product_in_combo
        return products_available.read(fields, load=False)


