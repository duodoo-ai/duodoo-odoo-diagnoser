/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { Component, onMounted, onWillUnmount, useRef, useState } from "@odoo/owl";

const FORM_SPLIT_RATIO = "eist_web_theme_form_split_ratio";
const MIN_LEFT = 1200;
const MIN_RIGHT = 400;
const MASK_CLASS = "o_form_splitter_mask";

export class FormSplitter extends Component {
    static template = "eist_web_theme.FormSplitter";
    static props = {
        containerSelector: String,
        sheetSelector: String,
        chatterSelector: String,
        display: Boolean,
    };

    setup() {
        this.splitterRef = useRef("splitter");
        this.state = useState({ dragging: false, startX: 0, startLeft: 0, ratio: null, display: false });
        this.onMouseDown = this.onMouseDown.bind(this);
        this.onMouseMove = this.onMouseMove.bind(this);
        this.onMouseUp = this.onMouseUp.bind(this);
        onMounted(() => {
            // 渲染后查找真实 DOM
            this.container = document.querySelector(this.props.containerSelector);
            this.sheet = document.querySelector(this.props.sheetSelector);
            this.chatter = document.querySelector(this.props.chatterSelector);
            // 恢复缓存
            const ratio = localStorage.getItem(FORM_SPLIT_RATIO);
            // console.log("[FormSplitter] onMounted, ratio from storage:", ratio);
            // console.log("[FormSplitter] DOM elements:", this.container, this.sheet, this.chatter);
            if (ratio) {
                this.applyRatio(parseFloat(ratio));
            } else if (this.sheet) {
                this.sheet.classList.add("has_seat_form_split_ratio");
            }
            browser.addEventListener("mousemove", this.onMouseMove);
            browser.addEventListener("mouseup", this.onMouseUp);
        });
        onWillUnmount(() => {
            browser.removeEventListener("mousemove", this.onMouseMove);
            browser.removeEventListener("mouseup", this.onMouseUp);
        });
    }

    onMouseDown(ev) {
        if (!this.sheet || !this.container) return;
        this.state.dragging = true;
        this.state.startX = ev.clientX;
        this.state.startLeft = this.sheet.offsetWidth;
        this.state.containerWidth = this.container.offsetWidth;
        document.body.classList.add("o_noselect");
        // 添加遮罩层
        if (!document.querySelector('.' + MASK_CLASS)) {
            const mask = document.createElement('div');
            mask.className = MASK_CLASS;
            Object.assign(mask.style, {
                position: 'fixed',
                left: 0,
                top: 0,
                width: '100vw',
                height: '100vh',
                zIndex: 999,
                cursor: 'ew-resize',
            });
            document.body.appendChild(mask);
        }
    }

    onMouseMove(ev) {
        if (!this.state.dragging || !this.sheet || !this.container || !this.chatter) return;
        const dx = ev.clientX - this.state.startX;
        let newLeft = this.state.startLeft + dx;
        let newRight = this.state.containerWidth - newLeft - 6; // 6为分割线宽度
        if (newLeft < MIN_LEFT) newLeft = MIN_LEFT;
        if (newRight < MIN_RIGHT) newLeft = this.state.containerWidth - MIN_RIGHT - 6;
        const ratio = newLeft / this.state.containerWidth;
        this.applyRatio(ratio);
        // console.log("[FormSplitter] onMouseMove", {
        //     dx,
        //     newLeft,
        //     newRight,
        //     ratio
        // });
    }

    onMouseUp() {
        if (!this.state.dragging || !this.sheet || !this.container) return;
        this.state.dragging = false;
        // 缓存比例
        const ratio = this.sheet.offsetWidth / this.container.offsetWidth;
        localStorage.setItem(FORM_SPLIT_RATIO, ratio);
        document.body.classList.remove("o_noselect");
        // 移除遮罩层
        const mask = document.querySelector('.' + MASK_CLASS);
        if (mask) mask.remove();
        // console.log("[FormSplitter] onMouseUp, saved ratio:", ratio);
    }

    applyRatio(ratio) {
        if (!this.sheet || !this.chatter || !this.container) return;
        this.state.ratio = ratio;
        const containerWidth = this.container.offsetWidth;
        // 先计算最大允许的 leftWidth，保证右侧最小宽度
        const maxLeft = containerWidth - MIN_RIGHT - 6;
        let leftWidth = Math.max(MIN_LEFT, Math.round(containerWidth * ratio));
        leftWidth = Math.min(leftWidth, maxLeft);
        const rightWidth = Math.max(MIN_RIGHT, containerWidth - leftWidth - 6);
        this.sheet.style.width = leftWidth + "px";
        this.chatter.style.width = rightWidth + "px";
        this.sheet.classList.remove("has_seat_form_split_ratio");
        // console.log("[FormSplitter] applyRatio", { ratio, leftWidth, rightWidth });
    }
}