# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.survey.controllers.main import Survey  # Inherit from correct class
from odoo import http
from odoo.http import request
import logging
from odoo.addons.base.models.ir_qweb import keep_query


import base64

_logger = logging.getLogger(__name__)


class CustomSurveyController(Survey):

    @http.route('/survey/test/<string:survey_token>', type='http', auth='user', website=True)
    def survey_test(self, survey_token, **kwargs):
        """ Test mode for surveys: create a test answer, only for managers or officers
        testing their surveys """
        survey_sudo, dummy = self._fetch_from_access_token(survey_token, False)
        try:
            answer_sudo = survey_sudo._create_answer(user=request.env.user, test_entry=False)
        except:
            return request.redirect('/')
        return request.redirect('/survey/start/%s?%s' % (survey_sudo.access_token, keep_query('*', answer_token=answer_sudo.access_token)))
