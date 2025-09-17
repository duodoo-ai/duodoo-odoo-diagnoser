/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

function waitForBusService(timeout = 5000, interval = 100) {
    return new Promise((resolve, reject) => {
        const start = Date.now();
        (function check() {
            let busService = null;
            if (
                window.__WOWL_DEBUG__ &&
                window.__WOWL_DEBUG__.root &&
                window.__WOWL_DEBUG__.root.env &&
                window.__WOWL_DEBUG__.root.env.services &&
                window.__WOWL_DEBUG__.root.env.services.bus_service
            ) {
                busService = window.__WOWL_DEBUG__.root.env.services.bus_service;
            }
            if (busService) {
                resolve(busService);
            } else if (Date.now() - start > timeout) {
                reject(new Error("busService 获取超时"));
            } else {
                setTimeout(check, interval);
            }
        })();
    });
}

publicWidget.registry.LockScreen = publicWidget.Widget.extend({
    selector: '.lock-screen-page',
    events: {
        'focus #lock_password': '_onFocusPasswordInput',
        'input #lock_password': '_onInputPasswordInput',
        'blur #lock_password': '_onBlurPasswordInput',
        'click #confirm_logout_button': '_onClickRelogin',
        'click button.submit': '_onClickUnlock',
    },
    start: async function () {
        var self = this;

        var $form = $('form');
        var redirect = $form.find('input[name="redirect"]').val();
        try {
            this.busService = await waitForBusService();
            console.log("this.busService",this.busService);
            this.busService.subscribe('unlock_screen', () => {
                self.unlockScreen(redirect);
            });
        } catch (e) {
            console.warn("busService 获取失败：", e);
        }

        // if (this.busService) {
        //     this.busService.subscribe('unlock_screen', () => {
        //         this.unlockScreen(redirect);
        //     });
        // }

        return this._super.apply(this, arguments).then(function () {
            self.initLockScreen();
        })
    },
    unlockScreen: function (redirect) {
        // 等待2秒后跳转
        setTimeout(function () {
            window.location.href = redirect;
        }, 2000);
    },
    initLockScreen: function () {

    },

    _onFocusPasswordInput: function (ev) {
        var $input = $(ev.currentTarget);
        var originalFont = $input.data('original-font') || $input.css('font-family');
        $input.data('original-font', originalFont);
        if ($input.val().length > 0) {
            $input.css('font-family', '"password", ' + originalFont);
        } else {
            $input.css('font-family', originalFont);
        }
    },
    _onInputPasswordInput: function (ev) {
        var $input = $(ev.currentTarget);
        var originalFont = $input.data('original-font') || $input.css('font-family');
        $input.data('original-font', originalFont);
        if ($input.val().length > 0) {
            $input.css('font-family', '"password", ' + originalFont);
        } else {
            $input.css('font-family', originalFont);
        }
    },
    _onBlurPasswordInput: function (ev) {
        var $input = $(ev.currentTarget);
        var originalFont = $input.data('original-font') || $input.css('font-family');
        $input.data('original-font', originalFont);
        if ($input.val().length > 0) {
            $input.css('font-family', '"password", ' + originalFont);
        } else {
            $input.css('font-family', originalFont);
        }
    },
    _onClickRelogin: function (ev) {
        console.log('重新登录');
        ev.preventDefault();
        window.location.href = "/web/session/logout?redirect=/web/login";
    },
    _onClickUnlock: async function (ev) {
        ev.preventDefault(); // 阻止默认行为
        ev.stopPropagation(); // 阻止事件冒泡

        // 获取表单
        var $form = $(ev.currentTarget).closest('form');
        var login = $form.find('input[name="login"]').val();
        var password = $form.find('input[name="password"]').val();
        var redirect = $form.find('input[name="redirect"]').val();

        const result = await rpc("/web/session/unlock", {
            login: login,
            password: password,
        });

        // 判断是否有错误
        if (result.error) {
            $form.find('#error_alert').removeClass('d-none');
            $form.find('#error_alert').find('.error').text(result.error);
        }

        // 判断是否解锁成功
        if (result.unlock_success) {
            $form.find('#error_alert').addClass('d-none');
            $form.find('#message_alert').removeClass('d-none');
            $form.find('#message_alert').find('.message').text(result.message);

        }
    }
});

publicWidget.registry.LockScreen2 = publicWidget.Widget.extend({
    selector: '.lock-screen-theme-2',
    jsLibs: [
        '/eist_web_theme/static/libs/backstretch/jquery.backstretch.min.js',
    ],
    start: function () {
        var self = this;

        return this._super.apply(this, arguments).then(function () {
            self.change_background();
        })
    },
    change_background: function () {
        $.backstretch([
            "/eist_web_theme/static/img/lock/bg/1.jpg",
            "/eist_web_theme/static/img/lock/bg/2.jpg",
            "/eist_web_theme/static/img/lock/bg/3.jpg",
            "/eist_web_theme/static/img/lock/bg/4.jpg"
        ], {
            fade: 1000,
            duration: 8000
        });
    },
});