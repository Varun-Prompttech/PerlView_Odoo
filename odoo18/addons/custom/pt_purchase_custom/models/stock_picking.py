from odoo import models, fields
from odoo.exceptions import MissingError, ValidationError, AccessError, UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    state = fields.Selection(selection_add=[('received', 'Received'), ('in_transit', 'In Transit'), ('done',)])
    return_bill = fields.Boolean('Return Bill', related='picking_type_id.return_bill')
    invoice_id = fields.Many2one('account.move')

    def action_received(self):
        self.state = 'received'

    def action_in_transit(self):
        if all(x in self.env.user.default_analytic_account.ids for x in self.location_id.analytic_account_id.ids):
            self.state = 'in_transit'
        else:
            raise ValidationError('Transfer is not Authorized for this User')

    def button_validate(self):
        if self.picking_type_id.code == 'internal':
            # if self.env.user.default_analytic_account.ids == self.location_dest_id.analytic_account_id.ids:
            if all(x in self.env.user.default_analytic_account.ids for x in
                       self.location_dest_id.analytic_account_id.ids):
                    return super().button_validate()
            else:
                raise ValidationError('Validation is not Authorized for this User')
        else:
            return super().button_validate()

    def action_create_bill(self):
        if self.state != 'done':
            raise ValidationError('Please Validate the Delivery Order')

        else:
            invoice_lines = []
            distribution_list = {}
            if self.location_id.analytic_account_id:
                account = self.env['account.analytic.account'].search(
                    [('id', 'in', self.location_id.analytic_account_id.ids)])
                for acc in account:
                    find_account = self.env['account.analytic.account'].search([('id', '=', acc.id)])
                    distribution_list[find_account.id] = 100
            for line in self.move_ids:
                invoice_lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'analytic_distribution': distribution_list,
                    'quantity': line.quantity,
                    'product_uom_id': line.product_id.uom_po_id.id,
                    'price_unit': line.product_id.standard_price,
                    'tax_ids': [(6, 0, line.product_id.supplier_taxes_id.ids)]
                }))
            invoice_id = self.env['account.move'].create({
                'partner_id': self.partner_id.id,
                'analytic_account_id': [(6, 0, self.location_id.analytic_account_id.ids)],
                'move_type': 'in_refund',
                'invoice_line_ids': invoice_lines
            })
            self.invoice_id = invoice_id
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'res_id': self.invoice_id.id,
                'view_mode': 'form',
                'target': 'current',
            }

    def open_invoice_form(self):
        if self.invoice_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'res_id': self.invoice_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
