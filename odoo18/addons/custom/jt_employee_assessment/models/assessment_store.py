from odoo import fields, models,api,_
from odoo.tools import config
import requests
import logging
_logger = logging.getLogger(__name__)


class AssessmentStore(models.Model):

    _name = 'assessment.store'
    _description = 'Assessment Store'
    _inherit = [
                'mail.thread',
                'mail.activity.mixin',
               ]

    name = fields.Char(string='Name')
    partner_latitude = fields.Float('Geo Latitude', digits=(10, 7))
    partner_longitude = fields.Float('Geo Longitude', digits=(10, 7))
    date_localization = fields.Date(string='Geolocation Date')

    def get_system_location(self):
        """Get the system's current location based on IP using an external geolocation service."""
        try:
            response = requests.get('http://ipinfo.io/json')
            if response.status_code != 200:
                _logger.error(f"Failed to fetch location: {response.status_code} - {response.text}")
                return 0.0, 0.0

            data = response.json()
            loc = data.get('loc', '').split(',')
            latitude = loc[0] if loc else 0.0
            longitude = loc[1] if len(loc) > 1 else 0.0
            return float(latitude), float(longitude)

        except requests.RequestException as e:
            _logger.error(f"Request error when fetching system location: {str(e)}")
        except ValueError as e:
            _logger.error(f"Value error when processing system location data: {str(e)}")
        except Exception as e:
            _logger.error(f"Unexpected error fetching system location: {str(e)}")
        return 0.0, 0.0

    def update_partner_location(self):
        latitude, longitude = self.get_system_location()
        self.write({
            'partner_latitude': latitude,
            'partner_longitude': longitude,
        })
        _logger.info(f"Updated partner location to lat: {latitude}, lon: {longitude}")


    _sql_constraints = [
        ('constrains_rating_label', 'unique(name)', 'Rating Label already exists!!')]
