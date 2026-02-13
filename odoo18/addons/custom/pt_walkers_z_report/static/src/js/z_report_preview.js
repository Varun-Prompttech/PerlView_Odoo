/** @odoo-module **/

import { registry } from "@web/core/registry";
import { downloadReportCustom } from "@gt_pdf_print_preview/webclient/actions/reports/utils";
import { rpc } from "@web/core/network/rpc";

registry.category("actions").add("z_report_preview", async (env, action) => {
    const report_data = action.params.data || {};
    const action_id = action.params.action_id;

    if (!report_data.config_id || !report_data.date_start || !report_data.date_stop) {
        alert("Missing required data to generate report");
        return;
    }

    const [report] = await rpc("/web/dataset/call_kw", {
        model: "ir.actions.report",
        method: "read",
        args: [[action_id], ['report_name', 'report_type', 'name']],
        kwargs: {},
    });

    const context = {
        active_model: 'walkers.z.report',
        active_id: 1,
        active_ids: [1],
        data: report_data,
    };
    const wizard_id = action.wizard_id;
    const actionData = {
        type: "ir.actions.report",
        name: report.name,
        report_type: report.report_type,
        report_name: report.report_name,
        context: {
            active_model: 'walkers.z.report',
              active_id: wizard_id,
            active_ids: [wizard_id],
        },
        data: report_data,
    };

    const resultData = await downloadReportCustom(rpc, actionData, 'pdf', context);
    if (!resultData.success && resultData.message) {
        alert(resultData.message);
    }
});
