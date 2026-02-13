from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # def _action_done(self):
    #
    #     res = super()._action_done()
    #     if self.move_ids:
    #         if self.picking_type_id.code != 'outgoing':
    #             analytic_account_id = self.purchase_id.analytic_account_id.ids
    #             self.move_ids.account_move_ids.analytic_account_id = analytic_account_id
    #             distribution_list = {}
    #             if analytic_account_id:
    #                 account = self.env['account.analytic.account'].search(
    #                     [('id', 'in', self.purchase_id.analytic_account_id.ids)])
    #                 for acc in account:
    #                     find_account = self.env['account.analytic.account'].search([('id', '=', acc.id)])
    #                     distribution_list[find_account.id] = 100
    #             for line in self.move_ids.account_move_ids.line_ids:
    #                 line.analytic_distribution = distribution_list
    #     return res
    def _action_done(self):

        res = super()._action_done()
        if self.move_ids:
            analytic_account_id = None
            if self.picking_type_id.code == 'incoming':
                analytic_account_id = self.purchase_id.analytic_account_id.ids
            elif self.picking_type_id.code == 'outgoing':
                analytic_account_id = self.sale_id.analytic_account_id.ids
            self.move_ids.account_move_ids.analytic_account_id = analytic_account_id
            distribution_list = {}
            if analytic_account_id:
                account = self.env['account.analytic.account'].search(
                    [('id', 'in', analytic_account_id)])
                for acc in account:
                    find_account = self.env['account.analytic.account'].search([('id', '=', acc.id)])
                    distribution_list[find_account.id] = 100
                for line in self.move_ids.account_move_ids.line_ids:
                    line.analytic_distribution = distribution_list
        if self:
            """Creating Journal Entry If Picking Type is Internal Transfer"""
            if self.picking_type_id.code == 'internal':
                for rec in self.move_ids:
                    # print("rec", self.name, rec.name, )
                    description = self.name + " - " + rec.name
                    journal_id, acc_src, acc_dest, acc_valuation = rec._get_accounting_data_for_valuation()
                    # print("journal_id", journal_id, "acc_src", acc_src, "acc_dest", acc_dest, "acc_valuation",
                    #       acc_valuation)
                    source_distribution_list = {}
                    dest_distribution_list = {}
                    source_account = self.env['account.analytic.account'].search([('id', 'in', self.location_id.analytic_account_id.ids)])
                    dest_account = self.env['account.analytic.account'].search([('id', 'in', self.location_dest_id.analytic_account_id.ids)])
                    for acc in source_account:
                        find_account = self.env['account.analytic.account'].search([('id', '=', acc.id)])
                        source_distribution_list[find_account.id] = 100
                    for acc in dest_account:
                        find_account = self.env['account.analytic.account'].search([('id', '=', acc.id)])
                        dest_distribution_list[find_account.id] = 100
                    lines = [(0, 0, {
                        'account_id': acc_valuation,
                        'partner_id': rec.partner_id.id,
                        'name': description,
                        'analytic_distribution':source_distribution_list,
                        'debit': 0.00,
                        'credit': rec.product_id.product_tmpl_id.standard_price * rec.product_uom_qty

                    }),
                             (0, 0, {
                                 'account_id': acc_valuation,
                                 'partner_id': rec.partner_id.id,
                                 'name': description,
                                 'analytic_distribution': dest_distribution_list,
                                 'debit': rec.product_id.product_tmpl_id.standard_price * rec.product_uom_qty,
                                 'credit': 0.00

                             })
                             ]

                    account_moves = self.env['account.move'].create({
                        'ref': description,
                        'date': self.scheduled_date.date(),
                        'journal_id': journal_id,
                        'line_ids': lines,
                        'partner_id': rec.partner_id.id,
                        'stock_move_id': rec.id,
                        'move_type': 'entry',
                        'company_id': self.company_id.id,
                    })
                    account_moves._post()
        return res
