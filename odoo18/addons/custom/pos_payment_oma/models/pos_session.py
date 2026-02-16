# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _validate_session(self, balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None):
        res = super()._validate_session(balancing_account=balancing_account, amount_to_balance=amount_to_balance,
                                        bank_payment_method_diffs=bank_payment_method_diffs)
        distribution_list = {}
        account_analytic_distribution = self.env['account.analytic.distribution.model'].search(
            [('pos_config_id', '=', self.config_id.id)], limit=1)
        
        analytic_account = self.env['account.analytic.account']
        if account_analytic_distribution and account_analytic_distribution.analytic_distribution:
            keys_as_int = [int(key) for key in account_analytic_distribution.analytic_distribution.keys()]
            analytic_account = self.env['account.analytic.account'].search([('id', 'in', keys_as_int)])
            for acc in analytic_account:
                distribution_list[acc.id] = 100

        # Adding Analytic Account in Journal Entry
        if self.move_id and analytic_account:
            self.move_id.analytic_account_id = [(6, 0, analytic_account.ids)]
        
        # Adding Analytic Account Cash Payment
        if self.statement_line_ids and analytic_account:
            move_id = self.statement_line_ids.mapped('move_id')
            move_id.analytic_account_id = [(6, 0, analytic_account.ids)]
            for line in move_id.line_ids:
                line.analytic_distribution = distribution_list
        
        # Adding Analytic Account Bank Payment
        if self.bank_payment_ids and analytic_account:
            move_id = self.bank_payment_ids.mapped('move_id')
            move_id.analytic_account_id = [(6, 0, analytic_account.ids)]
            for line in move_id.line_ids:
                line.analytic_distribution = distribution_list
            move_id.origin_payment_id.write({'analytic_account_id': [(6, 0, analytic_account.ids)]})
        
        if self.mapped('order_ids.payment_ids.account_move_id') and analytic_account:
            move_id = self.mapped('order_ids.payment_ids.account_move_id')
            move_id.analytic_account_id = [(6, 0, analytic_account.ids)]

        return res


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _prepare_invoice_vals(self):
        vals = super()._prepare_invoice_vals()
        account_analytic_distribution = self.env['account.analytic.distribution.model'].search(
            [('pos_config_id', '=', self.session_id.config_id.id)], limit=1)
        
        if account_analytic_distribution and account_analytic_distribution.analytic_distribution:
            keys_as_int = [int(key) for key in account_analytic_distribution.analytic_distribution.keys()]
            analytic_account = self.env['account.analytic.account'].search([('id', 'in', keys_as_int)]).ids
            vals['analytic_account_id'] = [(6, 0, analytic_account)]
        return vals

    @api.model
    def _get_invoice_lines_values(self, line_values, pos_order_line):
        res = super()._get_invoice_lines_values(line_values, pos_order_line)
        
        distribution_list = {}
        if pos_order_line.order_id.config_id:
            account_analytic_distribution = self.env['account.analytic.distribution.model'].search(
                [('pos_config_id', '=', pos_order_line.order_id.config_id.id)], limit=1)
            
            if account_analytic_distribution and account_analytic_distribution.analytic_distribution:
                keys_as_int = [int(key) for key in account_analytic_distribution.analytic_distribution.keys()]
                analytic_account = self.env['account.analytic.account'].search([('id', 'in', keys_as_int)])
                if analytic_account:
                    distribution_list[analytic_account[0].id] = 100
                    res['analytic_distribution'] = distribution_list

        return res

    def _create_order_picking(self):
        res = super()._create_order_picking()
        distribution_list = {}
        account_analytic_distribution = self.env['account.analytic.distribution.model'].search(
            [('pos_config_id', '=', self.session_id.config_id.id)], limit=1)
        
        analytic_account = self.env['account.analytic.account']
        if account_analytic_distribution and account_analytic_distribution.analytic_distribution:
            keys_as_int = [int(key) for key in account_analytic_distribution.analytic_distribution.keys()]
            analytic_account = self.env['account.analytic.account'].search([('id', 'in', keys_as_int)])
            for acc in analytic_account:
                distribution_list[acc.id] = 100
                
        if analytic_account:
            for picking in self.picking_ids:
                journal_entry = self.env['account.move'].search(
                    [('move_type', '=', 'entry'), ('ref', 'ilike', picking.name), ('state', '=', 'posted')])
                journal_entry.write({'analytic_account_id': [(6, 0, analytic_account.ids)]})
                for line in journal_entry.line_ids:
                    line.analytic_distribution = distribution_list

        return res
