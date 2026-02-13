# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date


class UserActivity(models.AbstractModel):
	_inherit = 'mail.thread'

	@api.model_create_multi
	def create(self, values):
		record = super(UserActivity, self).create(values)
		model_name = self._name
		action = 'Create'
		context = self._context
		current_uid = context.get('uid')
		current_user = self.env['res.users'].browse(current_uid)
		search = self.env['user.audit.configuration'].search([])
		for search in search:
			if search.create_log:
				check_user = False
				if search.all_users:
					check_user = True				
				else:		
					for user in search.user_ids:
						if current_user.name == user.name:
							check_user = True
				for rec in search.model_ids:
					if check_user:
						search_model = self.env['ir.model'].search([('model', '=', model_name)])
						if search_model.name == rec.name:
							self.log_activity(model_name, record.id, action, current_user.id)
						for values in values:
							if type(values) != str:
								for field_name, field_value in values.items():
									field = record._fields.get(field_name)
									if field.type == 'one2many':
										model_model = self.env['ir.model'].search([('model','=',model_name)])
										model_field = self.env['ir.model.fields'].search([('name','=',field_name),('model_id','=',model_model.id)])
										if model_field:
											related_model_name = self.env[model_field[0].relation]._name
											for models in search.model_ids:
												if models.model == related_model_name:
													self.log_activity(related_model_name, record.id, action, current_user.id)
							
		return record
	
	def unlink(self):
		user_id = self.env.user.id
		action = 'Delete'

		search = self.env['user.audit.configuration'].search([])
		for record in self:
			model_name = record._name
			for config in search:
				if config.delete_log:
					check_user = False
					if config.all_users:
						check_user = True
					else:
						for user in config.user_ids:
							if user.name == record.env.user.name:
								check_user = True
								break

					for rec in config.model_ids:
						if check_user:
							search_model = self.env['ir.model'].search([('model', '=', model_name)])
							if search_model.name == rec.name:
								self.log_activity(model_name, record.id, action, user_id)
		return super(UserActivity, self).unlink()

	def read(self, fields=None, load='_classic_read'):
		model_name = self._name
		user_id = self.env.user.id
		action = 'Read'
		search = self.env['user.audit.configuration'].sudo().search([])
		search_model = None
		for search in search:
			if search.read_log:
				check_user = False
				if search.all_users:
					check_user = True
				else:
					for user in search.user_ids:
						if user.name == self.env.user.name:
							check_user = True
				for rec in search.model_ids:
					if check_user:
						search_model = self.env['ir.model'].sudo().search([('model', '=', model_name)])
						if search_model.name == rec.name:
							if search_model:
								l1 = []
								for i in self:
									l1.append(i.id)
									if len(l1) == 1:
										if len(fields)>=12:
											if type(i.id) == int:
												self.log_activity(model_name, i.id, action, user_id)
				else:
					continue  
				break 
		return super(UserActivity, self).read(fields=fields, load=load)

	def write(self, values):
		model_name = self._name
		user_id = self.env.user.id
		action = 'Write'
		search_configs = self.env['user.audit.configuration'].search([])
		for config in search_configs:
			if config.write_log:
				check_user = False
				if config.all_users:
					check_user = True				
				else:		
					for user in config.user_ids:
						if user.name == self.env.user.name:
							check_user = True
				if check_user:
					search_model = self.env['ir.model'].search([('model', '=', model_name)])
					if search_model.name in config.model_ids.mapped('name'):
						updated_fields = []
						for field in config.field_ids:
							if field.model == model_name:
								if field.name in values:
									updated_fields.append(field.name)
									old_value = getattr(self, field.name, False)
									updated_value = values[field.name]
									if old_value != updated_value:
										log_values = {
											'model_id': search_model.id,
											'record_id': self.id,
											'log_type': action.capitalize(),
											'user_id': user_id,
											'updated_id': field.id,
										}
										if field.ttype == 'many2one':
											related_field_value = ''
											for key, value in values.items():
												if isinstance(value, int):
													related_record = self.env[field.relation].browse(value)
													if related_record:
														updated_value = getattr(related_record, 'name', '') or getattr(related_record, 'description', '') or ''
														log_values.update({'updated_value': updated_value})
											
											old_value_description = getattr(old_value, 'name', '') or getattr(old_value, 'description', '') or ''
											log_values.update({
												'old_value': old_value_description,
											})

										elif(field.ttype == 'many2many'):
											old_values = ", ".join(old_value.mapped('display_name'))
											log_values.update({'old_value': old_values})

											if values.get(field.name):
												updated_ids = set(old_value.ids)  

												for command in values[field.name]:
													if command[0] == 6:
														updated_ids = set(command[2]) 
													elif command[0] == 4:
														updated_ids.add(command[1])
													elif command[0] == 3:
														updated_ids.discard(command[1])
													elif command[0] == 0:
														created_record = self.env[field.relation].create(command[2])
														updated_ids.add(created_record.id)
													elif command[0] == 5:
														updated_ids.clear()

												updated_records = self.env[field.relation].browse(list(updated_ids))
												updated_values = ", ".join(updated_records.mapped('display_name'))
												log_values.update({'updated_value': updated_values})

										elif field.ttype == 'one2many':
											old_values = ""
											if old_value:
												old_value_names = []
												for record in old_value:
													if hasattr(record, 'name'):
														old_value_names.append(record.name)
													elif hasattr(record, 'display_name'):
														old_value_names.append(record.display_name)
												old_values = ", ".join(old_value_names)
											log_values.update({'old_value': old_values})

											updated_records = old_value and list(old_value) or []

											changes = values.get(field.name, [])
											for change in changes:
												if len(change) == 3:
													operation, record_id, record_data = change
												elif len(change) == 2:
													operation, record_id = change
													record_data = {}
												else:
													continue

												if operation == 4: 
													updated_record = self.env[field.relation].browse(record_id)
													if updated_record not in updated_records:
														updated_records.append(updated_record)
												elif operation == 1: 
													updated_record = self.env[field.relation].browse(record_id)
													if updated_record not in updated_records:
														updated_records.append(updated_record)
												elif operation == 0: 
													added_record_name = record_data.get('name', record_data.get('bank_id', ''))
													if added_record_name not in updated_records:
														updated_records.append(added_record_name)
												elif operation == 2: 
													updated_record = self.env[field.relation].browse(record_id)
													if updated_record in updated_records:
														updated_records.remove(updated_record)

											updated_value_display = ", ".join(
												record.name if hasattr(record, 'name') else record.display_name if hasattr(record, 'display_name') else str(record)
												for record in updated_records
											)
											log_values.update({'updated_value': updated_value_display})

										else:
											log_values.update({
												'old_value': old_value,
												'updated_value': updated_value,
												})
										self.env['user.audit.log'].sudo().create(log_values)
						if updated_fields: 
							break
		return super(UserActivity, self).write(values)

	@api.model
	def log_activity(self, model_name, record_id, action, user_id):
		log_type = action.capitalize()
		log_values = {
			'model_id': self.env['ir.model'].search([('model', '=', model_name)]).id,
			'record_id': record_id,
			'log_type': log_type,
			'user_id': user_id,
		}
		self.env['user.audit.log'].sudo().create(log_values)

