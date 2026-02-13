import logging
from odoo import api, fields, models, _
from datetime import datetime,date
from dateutil.relativedelta import relativedelta
from odoo.tools import format_date

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def _cron_check_future_pdc_payments(self):
        # print(">>> CRON: _cron_check_future_pdc_payments called")
        # _logger.info("CRON: _cron_check_future_pdc_payments called")

        today = fields.Date.today()
        threshold_date = today + relativedelta(days=30)
        # print(f">>> Threshold Date: {threshold_date}")

        pdc_journal = self.env['account.journal'].search([('code', '=', 'PDC')], limit=1)
        # print(">>> PDC Journal:", pdc_journal)
        if not pdc_journal:
            # print(">>> No journal found with code 'PDC'")
            # _logger.warning("No journal found with code 'PDC'")
            return

        # Find payments between today and the next 30 days
        payments = self.search([
            ('journal_id', '=', pdc_journal.id),
            ('date', '>=', today),
            ('date', '<=', threshold_date),
            ('state', '=', 'in_process'),
        ])
        # print(f">>> Payments Found: {len(payments)}")
        # _logger.info(f"Payments Found: {len(payments)}")

        for payment in payments:
            days_ahead = (payment.date - today).days
            # print(f">>> Payment ID {payment.id} is scheduled in {days_ahead} days on {payment.date}")
            # _logger.info(f"Payment ID {payment.id} is scheduled in {days_ahead} days on {payment.date}")

            # Remove duplicate activities
            existing = self.env['mail.activity'].search([
                ('res_model', '=', 'account.payment'),
                ('res_id', '=', payment.id),
                ('summary', '=', 'Future PDC Payment Alert')
            ])
            existing.unlink()

            user_id = payment.create_uid.id or self.env.ref('base.user_admin').id
            lang = self.env['res.users'].browse(user_id).lang
            formatted_date = format_date(payment.env, payment.date, date_format="dd MMMM y", lang_code=lang)

            payment.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=user_id,
                summary='Future PDC Payment Alert',
                note=_('This payment is post-dated by %s days on %s', days_ahead, formatted_date)
            )
            print("payment",payment.date)
            print("self",date.today(),type((payment.date-date.today()).days))
            if (payment.date-date.today()).days == 5:

                payment.message_post(
                    body=_('Cheque date is scheduled in %s days: %s', days_ahead, formatted_date),
                    message_type='notification'
                )
            elif (payment.date-date.today()).days == 2:
                payment.message_post(
                    body=_('Cheque date is scheduled in %s days: %s', days_ahead, formatted_date),
                    message_type='notification'
                )
            elif (payment.date-date.today()).days == 1:
                print("tdayss")
                payment.message_post(
                    body=_('Cheque date is scheduled in %s days: %s', days_ahead, formatted_date),
                    message_type='notification'
                )
            else:
                pass


            # print(f">>> Activity and message posted for Payment ID: {payment.id}")
