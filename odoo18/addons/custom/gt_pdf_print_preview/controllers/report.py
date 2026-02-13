# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import werkzeug
from odoo.addons.web.controllers.report import ReportController
from odoo import http
from odoo.http import request


class ReportController(ReportController):
    # ------------------------------------------------------
    # Report controllers
    # ------------------------------------------------------
    @http.route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        report = request.env["ir.actions.report"]
        context = dict(request.env.context)

        if docids:
            docids = [int(i) for i in docids.split(",") if i.isdigit()]
        if data.get("options"):
            data.update(json.loads(data.pop("options")))
        if data.get("context"):
            data["context"] = json.loads(data["context"])
            context.update(data["context"])
        if converter == "html":
            html = report.with_context(context)._render_qweb_html(
                reportname, docids, data=data
            )[0]
            return request.make_response(html)
        elif converter == "pdf":
            pdf = report.with_context(context)._render_qweb_pdf(
                reportname, docids, data=data
            )[0]
            pdfhttpheaders = [
                ("Content-Type", "application/pdf"),
                ("Content-Length", len(pdf)),
            ]
            active_model = data.get("active_model")
            if data.get("is_download") and active_model:
                docids_ids = (
                    request.env[active_model].browse(docids).mapped("name")
                )
                if all(doc_id for doc_id in docids_ids):
                    docids_name = ",".join(docids_ids) 
                    pdfhttpheaders.append(
                        (
                            "Content-Disposition",
                            f'attachment; filename="{docids_name}.pdf"',
                        )
                    )
                else:
                    pdfhttpheaders.append(
                        (
                            "Content-Disposition",
                            f'attachment; filename="{data.get("pdf_name")}.pdf"',
                        )
                    )
            return request.make_response(pdf, headers=pdfhttpheaders)
        elif converter == "text":
            text = report.with_context(context)._render_qweb_text(
                reportname, docids, data=data
            )[0]
            texthttpheaders = [
                ("Content-Type", "text/plain"),
                ("Content-Length", len(text)),
            ]
            return request.make_response(text, headers=texthttpheaders)
        else:
            raise werkzeug.exceptions.HTTPException(
                description="Converter %s not implemented." % converter
            )
