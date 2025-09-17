/* @odoo-module */


import { hasTouch } from "@web/core/browser/feature_detection";
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { session } from "@web/session";
import { SIZES } from "@web/core/ui/ui_service";
import { onMounted, onWillUnmount, useState } from "@odoo/owl";
import { ScrollTopButton } from '@eist_web_theme/components/scroll_top_button/scroll_top_button';
import { renderToElement } from "@web/core/utils/render";


patch(FormController.prototype, {
    setup() {
        super.setup(...arguments);
        this.theme = session["theme"];

        this.state = useState({});
        this.state.use_divider_resize_sheet = this.theme["views"]["form"]["use_divider_resize_sheet"];
        this.state.form_chatter_position = this.theme["views"]["form"]["chatter"]["position"];
        this.state.displayScrollTopButton = this.theme["views"]["display_scroll_top_button"];


        const self = this;
        this.onScrollFormEl = (ev) => {
            const offset = 300;
            if (this.state.displayScrollTopButton && this.scrollTopButton) {
                if (ev.target.scrollTop > offset) {
                    this.scrollTopButton.classList.remove('o_hidden');
                } else {
                    this.scrollTopButton.classList.add('o_hidden');
                }
            }
        }

        this.onClickScrollToTop = (ev) => {
            ev.preventDefault();
            if (this.contentEl) {
                $(this.contentEl).animate(
                    {
                        scrollTop: 0
                    },
                    500
                );
            }
            return false;
        }

        onMounted(() => {
            this.contentEl = this.rootRef.el.querySelector(".o_content");
            if (this.contentEl) {
                this.contentEl.addEventListener('scroll', this.onScrollFormEl);
            }

            // 初始化 scrollTopButton 引用
            if (this.state.displayScrollTopButton) {
                this.scrollTopButton = this.rootRef.el.querySelector(".o_scroll_top");
            }
        });
    },

    /*
    ! 覆盖
    */
    // get className() {
    //     const result = {};
    //     const { size } = this.ui;

    //     if (size <= SIZES.XS) {
    //         result.o_xxs_form_view = true;
    //     } else if (!this.env.inDialog && size === SIZES.XXL && this.state.form_chatter_position === 1) {
    //         result["o_xxl_form_view h-100"] = true;
    //     } else if (this.state.form_chatter_position === 2) {
    //         result.o_xxs_form_view = false;
    //         result["o_xxl_form_view h-100"] = false;
    //         result["flex-nowrap"] = false;
    //         result["flex-column"] = true;
    //     }
    //     if (this.props.className) {
    //         result[this.props.className] = true;
    //     }
    //     result["o_field_highlight"] = size < SIZES.SM || hasTouch();
    //     return result;
    // },



});
