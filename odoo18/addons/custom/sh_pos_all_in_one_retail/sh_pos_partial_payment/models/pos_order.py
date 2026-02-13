# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api, _
from odoo.tools import float_is_zero, float_round
from odoo.exceptions import ValidationError, UserError
from odoo.exceptions import UserError

class PosOrder(models.Model):
    _inherit = 'pos.order'

    sh_amount_residual = fields.Monetary(string='Amount Due',
        compute='_compute_amount',precompute=True ,store=True)

    @api.depends('amount_paid','amount_total')
    def _compute_amount(self):
        for each in self:
            if each.amount_paid < each.amount_total:
                each.sh_amount_residual = each.amount_total-each.amount_paid
            else:
                each.sh_amount_residual = 0.00

    def _create_invoice(self, move_vals):
        if self.config_id.cash_rounding and not self._is_pos_order_paid():
            self.ensure_one()
            new_move = self.env['account.move'].sudo().with_company(self.company_id).with_context(default_move_type=move_vals['move_type']).create(move_vals)
            message = _("This invoice has been created from the point of sale session: %s",
                self._get_html_link())

            new_move.message_post(body=message)
            return new_move
        return super()._create_invoice(move_vals)


    def _apply_invoice_payments(self, is_reverse=False):

        payment_ids = self.payment_ids.filtered(lambda x: not x.account_move_id)

        receivable_account = self.env["res.partner"]._find_accounting_partner(self.partner_id).with_company(self.company_id).property_account_receivable_id
        payment_moves = payment_ids.sudo().with_company(self.company_id)._create_payment_moves(is_reverse)
        if receivable_account.reconcile:
            invoice_receivables = self.account_move.line_ids.filtered(lambda line: line.account_id == receivable_account and not line.reconciled)
            if invoice_receivables:
                credit_line_ids = payment_moves._context.get('credit_line_ids', None)
                payment_receivables = payment_moves.mapped('line_ids').filtered(
                    lambda line: (
                        (credit_line_ids and line.id in credit_line_ids) or
                        (not credit_line_ids and line.account_id == receivable_account and line.partner_id)
                    )
                )
                (invoice_receivables | payment_receivables).sudo().with_company(self.company_id).reconcile()
        return payment_moves


    @api.model
    def sync_from_ui(self, orders):
        for order in orders:
            existing_order = self._get_open_order(order)
            if existing_order and existing_order.state == 'invoiced':
                if order.get('payment_ids'):
                    # existing_order.write({'state':'draft'})
                    for each_payment in order.get('payment_ids'):
                        existing_order.add_payment({
                            'name':each_payment[2]['name'],
                            'pos_order_id': existing_order.id,
                            'amount': each_payment[2]['amount'],
                            'payment_date': fields.Datetime.now(),
                            'payment_method_id': each_payment[2]['payment_method_id'],
                            'is_change': False,  
                        })
                    existing_order.write({'state':'invoiced'})
                    existing_order._apply_invoice_payments(existing_order.session_id.state == 'closed')

        return super().sync_from_ui(orders)
        
    def _process_payment_lines(self, pos_order, order, pos_session, draft):
        if pos_order and pos_order['amount_total'] and pos_order['amount_return'] and pos_order['amount_return'] < 0 and pos_order['to_invoice'] and pos_order['amount_paid'] < pos_order['amount_total']:
            draft = True
        return super()._process_payment_lines(pos_order, order, pos_session, draft)
