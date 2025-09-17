import { SIZES } from "@web/core/ui/ui_service";
import { browser } from "@web/core/browser/browser";
import { FormCompiler } from "@web/views/form/form_compiler";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";
import { patch } from "@web/core/utils/patch";
import { onMounted, useRef, useState } from "@odoo/owl";
import { formView } from "@web/views/form/form_view";
import { setAttributes } from "@web/core/utils/xml";



patch(FormCompiler.prototype, {
    /*
    * 源代码 src\addons\mail\static\src\chatter\web\form_renderer.js

    * EXTERNAL_COMBO_XXL:   chatter在侧栏，附件在单独的标签中
    * EXTERNAL_COMBO:       chatter在底部，附件在单独的标签中
    * COMBO:                chatter在底部，附件在侧栏
    * SIDE_CHATTER:         chatter在侧栏，没有附件
    * BOTTOM_CHATTER:       chatter在底部，没有附件
    * NONE
    */
    compile(node, params) {
        const res = super.compile(node, params);
        const form_chatter_position = session?.theme?.views?.form?.chatter?.position;
        const attachmentPreview = res.querySelector(".o_attachment_preview");
        let hasPreview = false;
        if (attachmentPreview) {
            // 更精确判断是否有实际附件内容
            hasPreview = !!attachmentPreview.querySelector('.o_attachment, .o_mail_attachment, [data-mimetype]');
        }
        console.log("form_chatter_position", form_chatter_position, "hasPreview", hasPreview);
        if (form_chatter_position === 2) {
            const chatterContainerHookXml = res.querySelector(".o-mail-Form-chatter");
            if (!chatterContainerHookXml) {
                return res;
            }
            const chatterContainerXml = chatterContainerHookXml.querySelector(
                "t[t-component='__comp__.mailComponents.Chatter']"
            );
            if (chatterContainerXml) {
                setAttributes(chatterContainerXml, {
                    isInFormSheetBg: "true",
                    isChatterAside: "false",
                });
                if (hasPreview) {
                    console.log("[eist_web_theme] patch: 强制chatter COMBO布局");
                } else {
                    console.log("[eist_web_theme] patch: 强制chatter BOTTOM_CHATTER布局");
                }
            } else {
                console.log("[eist_web_theme] patch: 未找到 ChatterContainerXml");
            }
        }
        console.log("最终res结构", res.outerHTML);
        return res;
    }
});