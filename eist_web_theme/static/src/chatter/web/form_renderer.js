import { SIZES } from "@web/core/ui/ui_service";
import { session } from "@web/session";
import { patch } from "@web/core/utils/patch";
import { FormRenderer } from "@web/views/form/form_renderer";
import { onMounted, onWillUnmount, useState } from "@odoo/owl";

console.log("eist_web_theme form_renderer.js loaded!");
window._eist_mailLayout_called = false;
patch(FormRenderer.prototype, {
    setup() {
        super.setup();
        console.log("this in setup", this);
        this.state = useState({
            ...this.state,
            use_divider_resize_sheet: session['theme'].views.form.use_divider_resize_sheet,
            form_chatter_position: session['theme'].views.form.chatter.position,
        });
    },

    /*
    * 源代码 src\addons\mail\static\src\chatter\web\form_renderer.js
    * EXTERNAL_COMBO_XXL:   chatter在侧栏，附件在单独的标签中
    * EXTERNAL_COMBO:       chatter在底部，附件在单独的标签中
    * COMBO:                chatter在底部，附件在侧栏
    * SIDE_CHATTER:         chatter在侧栏，没有附件
    * BOTTOM_CHATTER:       chatter在底部，没有附件
    * NONE
    */
    mailLayout(hasAttachmentContainer) {
        // const layout = super.mailLayout(hasAttachmentContainer);
        window._eist_mailLayout_called = true;
        console.log("mailLayout called!");
        console.log("继承的mailLayout");

        const position = session?.theme?.views?.form?.chatter?.position;
        const hasFile = this.hasFile();
        const hasChatter = !!this.mailStore;
        const hasExternalWindow = !!this.mailPopoutService.externalWindow;
        console.log("hasFile", hasFile, "hasChatter", hasChatter, "hasExternalWindow", hasExternalWindow);
        // console.log("this.state", this.state);
        // if (this.state.use_divider_resize_sheet) {
        //     return layout;
        // }
        const new_layout = layout;
        if (position === 2) {
            if (hasFile && hasAttachmentContainer) {
                new_layout = "COMBO";
            } else {
                new_layout = "BOTTOM_CHATTER";
            }
            return new_layout;
        }
        console.log("layout", layout);
        return super.mailLayout(hasAttachmentContainer);
    },
});
