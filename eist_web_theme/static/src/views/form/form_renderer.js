/* @odoo-module */

import { SIZES } from "@web/core/ui/ui_service";
import { FormRenderer } from "@web/views/form/form_renderer";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { useRef, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { FormSplitter } from "./form_splitter";


patch(FormRenderer.components, { FormSplitter });

patch(FormRenderer.prototype, {
    setup() {
        super.setup(...arguments);
        // this.form_split_ratio = browser.getItem("eist_web_theme_form_split_ratio");

        this.state = useState({
            ...this.state,
            use_divider_resize_sheet: session['theme'].views.form.use_divider_resize_sheet,
            form_chatter_position: session['theme'].views.form.chatter.position,
        });


        const rootRef = useRef("compiled_view_root");
        this.rootRef = rootRef; // 让其它方法也能访问

        onMounted(() => {
            // 监听 body 的 data-chatter-chatter-position 属性变化
            this._bodyAttrObserver = new MutationObserver((mutationsList) => {
                for (const mutation of mutationsList) {
                    if (
                        mutation.type === "attributes" &&
                        mutation.attributeName === "data-form-use-divider"
                    ) {
                        const newFormDividerValue = document.body.getAttribute("data-form-use-divider") === "true";
                        this.state.use_divider_resize_sheet = newFormDividerValue;

                        // console.log("[FormRenderer] onMounted, newFormDividerValue:", newFormDividerValue);

                        // 只有在 XXL 且开启分割时才插入分割线
                        if (this.uiService.size >= SIZES.XXL) {
                            // 等待 DOM 更新
                            setTimeout(() => {
                                // 查找主 form 元素
                                const form = document.querySelector(".o_form_renderer");
                                const splitter = form?.querySelector(".o_form_splitter");
                                if (form && splitter) {
                                    if (this.state.use_divider_resize_sheet) {
                                        form.classList.add("o_form_layout_split_container");
                                        splitter.classList.remove("d-none");
                                    } else {
                                        form.classList.remove("o_form_layout_split_container");
                                        splitter.classList.add("d-none");
                                    }
                                } 
                            }, 1000);
                        }
                    }
                    if (
                        mutation.type === "attributes" &&
                        mutation.attributeName === "data-chatter-chatter-position"
                    ) {
                        const newPositionValue = document.body.getAttribute("data-chatter-chatter-position");
                        this.state.form_chatter_position = Number(newPositionValue);

                        // 这里建议加 setTimeout，确保 DOM 已更新
                        setTimeout(() => {
                            if (this.rootRef && this.rootRef.el) {
                                const attachmentPreview = this.rootRef.el.querySelector(".o_attachment_preview");
                                if (attachmentPreview) {
                                    if (this.state.form_chatter_position === 2 && !this.hasFile()) {
                                        attachmentPreview.classList.add("d-none");
                                    } else {
                                        attachmentPreview.classList.remove("d-none");
                                    }
                                }
                            }
                        }, 1000)
                    }
                }
            });

            this._bodyAttrObserver.observe(document.body, {
                attributes: true,
                attributeFilter: ["data-form-use-divider", "data-chatter-chatter-position"],
            });
        });


        // 组件卸载时断开监听
        onWillUnmount(() => {
            if (this._bodyAttrObserver) {
                this._bodyAttrObserver.disconnect();
            }
        });
    },

    mailLayout(hasAttachmentContainer) {
        /*
        * 源代码 src\addons\mail\static\src\chatter\web\form_renderer.js

        * EXTERNAL_COMBO_XXL:   chatter在侧栏，附件在单独的标签中
        * EXTERNAL_COMBO:       chatter在底部，附件在单独的标签中
        * COMBO:                chatter在底部，附件在侧栏
        * SIDE_CHATTER:         chatter在侧栏，没有附件
        * BOTTOM_CHATTER:       chatter在底部，没有附件
        * NONE
        */

        const layout = super.mailLayout(hasAttachmentContainer);
        const hasFile = this.hasFile();
        const hasChatter = !!this.mailStore;
        // const hasExternalWindow = !!this.mailPopoutService.externalWindow;
        if (!hasFile) {
            if (this.rootRef.el) {
                const attachmentPreview = this.rootRef.el.querySelector(".o_attachment_preview ");
                // console.log("attachmentPreview", attachmentPreview);
                if (attachmentPreview) {
                    attachmentPreview.classList.add("d-none");
                }
            }
        }
        if (this.state.form_chatter_position === 2) {
            return "COMBO";
        }

        return layout
    },


})