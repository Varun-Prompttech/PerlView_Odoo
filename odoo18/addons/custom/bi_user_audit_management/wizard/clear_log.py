# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class ClearLog(models.TransientModel):
	_name = 'clear.log'
	_description = 'Clear Log'

	name = fields.Char()
	all_log = fields.Boolean('All log')
	to_date = fields.Date('To Date')

	read_log = fields.Boolean('Read')
	write_log = fields.Boolean('Write')
	create_log = fields.Boolean('Create')
	delete_log = fields.Boolean('Delete')

	model_ids = fields.Many2many('ir.model')

	def log_delete(self):
		Log = self.env['user.audit.log'].sudo()

		if self.all_log:
			Log.search([]).unlink()
			return

		if not self.model_ids:
			return

		log_type_domain = []
		if self.create_log:
			log_type_domain.append('Create')
		if self.read_log:
			log_type_domain.append('Read')
		if self.write_log:
			log_type_domain.append('Write')
		if self.delete_log:
			log_type_domain.append('Delete')

		if not log_type_domain:
			return

		for model in self.model_ids:
			records_to_delete = Log.search([
				('model_id', '=', model.id),
				('log_type', 'in', log_type_domain)
			])
			if records_to_delete:
				records_to_delete.unlink()