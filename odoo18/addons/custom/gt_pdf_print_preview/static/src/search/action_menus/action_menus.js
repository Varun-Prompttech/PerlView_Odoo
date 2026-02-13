/** @odoo-module **/

import { ActionMenus } from "@web/search/action_menus/action_menus";
import { patch } from "@web/core/utils/patch";
import { downloadReportCustom } from "@gt_pdf_print_preview/webclient/actions/reports/utils";
import { makeContext } from "@web/core/context";
import { user } from "@web/core/user";
import { session } from '@web/session';
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";


patch(ActionMenus.prototype, {
	async onItemSelected(item) {
    	var self = this;
        if (!(await this.props.shouldExecuteAction(item))) {
            return;
        }
        if(item.action && session.preview_print) {
        	let activeIds = this.props.getActiveIds();
        	if (this.props.isDomainSelected) {
        	    activeIds = await this.orm.search(this.props.resModel, this.props.domain, {
        	        limit: session.active_ids_limit,
        	        context: this.props.context,
        	    });
        	}
        	const activeIdsContext = {
        	    active_id: activeIds[0],
        	    active_ids: activeIds,
        	    active_model: this.props.resModel,
        	};

        	if (this.props.domain) {
        	    activeIdsContext.active_domain = this.props.domain;
        	}
        	const context = makeContext([this.props.context, activeIdsContext]);

        	let actionsData = await this.actionService.loadAction(item.action.id, context)
            if(actionsData.binding_type != "report") {
                super.onItemSelected(...arguments);
            }
        	else {
                let success, message;
                this.env.services.ui.block();
                try {
                    const downloadContext = { ...this.env.context };
                    if (item.action.context) {
                        Object.assign(downloadContext, item.action.context);

                    }
                    ({ success, message } = await downloadReportCustom(
                        rpc,
                        actionsData,
                        'pdf',
                        downloadContext
                    ));
                } finally {
                    this.env.services.ui.unblock();
                }
            }
        }
        else {
        	super.onItemSelected(...arguments);
        }
    }
});