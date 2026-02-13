from odoo import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'


    def _get_all_related_aml(self):
        res = super()._get_all_related_aml()
        # Add Location's analytic account in account.move while creating physical adjustments
        analytic_account_id = None
        print("self",self)
        for line in self:
            if line.picking_type_id.code == 'incoming':
                res.move_id.write({'analytic_account_id': line.location_dest_id.analytic_account_id.ids})
                analytic_account_id = line.location_dest_id.analytic_account_id.ids
            elif line.picking_type_id.code == 'outgoing':
                res.move_id.write({'analytic_account_id': line.location_id.analytic_account_id.ids})
                analytic_account_id = line.location_id.analytic_account_id.ids
        distribution_list = {}
        account = self.env['account.analytic.account'].search(
            [('id', 'in', analytic_account_id)])
        for acc in account:
            find_account = self.env['account.analytic.account'].search([('id', '=', acc.id)])
            distribution_list[find_account.id] = 100
        for line in res:
            line.analytic_distribution = distribution_list
        return res


class StockLocation(models.Model):
    _inherit = 'stock.location'

    analytic_account_id = fields.Many2many('account.analytic.account', string='Analytic Account')
