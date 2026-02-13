/** @odoo-module */

import { downloadReport } from "@web/webclient/actions/reports/utils";
import { FileViewer } from "@web/core/file_viewer/file_viewer";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { getReportUrl } from "@web/webclient/actions/reports/utils";
import { browser } from "@web/core/browser/browser";
import { getDataURLFromFile } from "@web/core/utils/urls";

function getWKHTMLTOPDF_MESSAGES(status) {
    const link = '<br><br><a href="http://wkhtmltopdf.org/" target="_blank">wkhtmltopdf.org</a>'; // FIXME missing markup
    const _status = {
        broken:
            _t(
                "Your installation of Wkhtmltopdf seems to be broken. The report will be shown in html."
            ) + link,
        install:
            _t("Unable to find Wkhtmltopdf on this system. The report will be shown in html.") +
            link,
        upgrade:
            _t(
                "You should upgrade your version of Wkhtmltopdf to at least 0.12.0 in order to get a correct display of headers and footers as well as support for table-breaking between pages."
            ) + link,
        workers: _t(
            "You need to start Odoo with at least two workers to print a pdf version of the reports."
        ),
    };
    return _status[status];
}

export async function downloadReportCustom(rpc, action, type, userContext) {
    let message;
    let fileViewerId = 0;
    let data, urlData;
    if (type === "pdf") {
        // Cache the wkhtml status on the function. In prod this means is only
        // checked once, but we can reset it between tests to test multiple statuses.
        downloadReport.wkhtmltopdfStatusProm ||= rpc("/report/check_wkhtmltopdf");
        const status = await downloadReport.wkhtmltopdfStatusProm;
        message = getWKHTMLTOPDF_MESSAGES(status);
        if (!["upgrade", "ok"].includes(status)) {
            return { success: false, message };
        }
    }
    const url = getReportUrl(action, type);
    let prom = await new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.onload = () => {
            getDataURLFromFile(xhr.response).then((response) => {
                data = response;

                const base64toBlob = (data => {
                    // Cut the prefix `data:application/pdf;base64` from the raw base 64
                    const base64WithoutPrefix = data.substr('data:application/pdf;base64,'.length);

                    const bytes = atob(base64WithoutPrefix);
                    let length = bytes.length;
                    let out = new Uint8Array(length);

                    while (length--) {
                        out[length] = bytes.charCodeAt(length);
                    }

                    return new Blob([out], { type: 'application/pdf' });
                });


                const blob = base64toBlob(data);
                urlData = URL.createObjectURL(blob);
                resolve();
            });
        };
        xhr.open('GET', url);
        xhr.responseType = 'blob';
        xhr.onerror = reject;
        xhr.send();
    });
    const viewerId = `web.file_viewer${fileViewerId++}`;
    const pdf_name = action.name.replace(/\//g, '-').trim();
    let custom_url;
    if(action.is_custom) {
        custom_url = false;
    }else {
        custom_url = url + `?active_model=${action.context.active_model}&pdf_name=${pdf_name}&is_download=true`;
    }

    await registry.category("main_components").add(viewerId, {
        Component: FileViewer,
        props: {
            files: [{
                    isPdf: true,
                    isViewable: false,
                    displayName: action.name,
                    defaultSource: '/web/static/lib/pdfjs/web/viewer.html?file=' + url,
                    downloadUrl: custom_url,
            }],
            startIndex: 0,
            close: () => {
                registry.category('main_components').remove(viewerId);
            },
        },
    });
    return { success: true, message };
}