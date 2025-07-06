import {registry} from "@web/core/registry";
import {WARNING_MESSAGE,_getReportUrl} from "./tools.esm";

registry
    .category("ir.actions.report handlers")
    .add("open_report_handler", async function (action, options, env) {
        console.log(action.report_type);
        if (["docx", "qweb-pdf"].includes(action.report_type)) {
            const url = _getReportUrl(action, action.report_type, env);
                if (!window.open(url)) {
                    console.log("WARNING_MESSAGE");
                    env.services.notification.add(WARNING_MESSAGE, {
                        type: "warning",
                    });
                }
            return Promise.resolve(true);
        }
    });