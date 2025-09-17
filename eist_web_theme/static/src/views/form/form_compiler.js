/* @odoo-module */

import { browser } from "@web/core/browser/browser";
import { SIZES } from "@web/core/ui/ui_service";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { createElement, setAttributes } from "@web/core/utils/xml";
import { session } from "@web/session";
import { onMounted, useRef, useState, onWillUnmount } from "@odoo/owl";
import { FormCompiler } from "@web/views/form/form_compiler";


const FORM_SPLIT_RATIO = "eist_web_theme_form_split_ratio";

patch(FormCompiler.prototype, {
    setup() {
        super.setup(...arguments);
        this.theme = session["theme"];
        this.uiService = useService("ui");
        this.form_split_ratio = parseFloat(browser.localStorage.getItem(FORM_SPLIT_RATIO));

        this.state = useState({
            use_divider_resize_sheet: session['theme'].views.form.use_divider_resize_sheet,
            form_chatter_position: session['theme'].views.form.chatter.position,
        });

        onMounted(() => {
            this.init_form_splitter();
        });

    },

    init_form_splitter() {
        const form = document.querySelector(".o_form_renderer");
        const splitter = form?.querySelector(".o_form_splitter");
        if (this.uiService.size >= SIZES.XXL) {
            if (form && splitter) {
                if (this.state.use_divider_resize_sheet) {
                    form.classList.add("o_form_layout_split_container");
                    splitter.classList.remove("d-none");
                }
                else {
                    form.classList.remove("o_form_layout_split_container");
                    splitter.classList.add("d-none");
                }
            }

        }
    },

    dynamic_display_splitter(form, sheet, chatter, show) {
        form.classList.add("o_form_layout_split_container");
        const splitter = createElement("FormSplitter", {
            containerSelector: "'.o_form_layout_split_container'",
            sheetSelector: "'.o_form_sheet_bg'",
            chatterSelector: "'.o-mail-ChatterContainer'",
            display: show
        });

        if (sheet && chatter) {
            sheet.parentNode.insertBefore(splitter, chatter);
        }

        if (show) {
            form.classList.add("o_form_layout_split_container");
        } else {
            form.classList.remove("o_form_layout_split_container");
        }
    },

    compileForm(el, params) {
        const form = super.compileForm(...arguments);
        const sheet = form.querySelector(".o_form_sheet_bg");
        const chatter = form.querySelector(".o-mail-ChatterContainer");

        // 添加分割布局容器 class
        // const isXXL = this.uiService.size >= SIZES.XXL;
        let show = false;
        if (this.state.use_divider_resize_sheet && this.uiService.size >= SIZES.XXL) {
            show = true;
        }
        this.dynamic_display_splitter(form, sheet, chatter, show);
        return form;
    },


});
