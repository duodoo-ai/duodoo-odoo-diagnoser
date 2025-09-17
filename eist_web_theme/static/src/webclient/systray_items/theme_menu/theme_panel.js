/** @odoo-module **/

import { _lt, _t } from '@web/core/l10n/translation';
import { session } from '@web/session';
import { useService } from '@web/core/utils/hooks';
import { cookie as cookieManager } from '@web/core/browser/cookie';
import { browser } from '@web/core/browser/browser';
import { user } from '@web/core/user';

import {
    Component,
    onWillDestroy,
    useExternalListener,
    useEffect,
    onPatched,
    onRendered,
    useState,
    useRef,
    onWillUnmount,
} from '@odoo/owl';

export class ThemePanel extends Component {
    setup() {
        super.setup();

        this.user = user;
        this.orm = useService('orm');
        this.notification = useService('notification');
        this.uiService = useService('ui');
        this.theme = session['theme'];
        const old_theme = this.theme;
        this.state = useState({
            theme: session['theme'],
            need_refresh: false,
        });

        const theme = this.state.theme;
        // console.log("theme", this.state.theme.lock_screen.theme,typeof this.state.theme.lock_screen.theme);

        onPatched(() => {
            // console.log("onPatched-----------theme", this.state.theme.main_submenu_position);
            // console.log("onPatched-----------old_theme", old_theme.main_submenu_position);
        });
        onRendered(() => {

        });
    }

    //-------------------------
    // MAIN
    //-------------------------
    onChangeAppLoadMethod(method) {
        this.state.theme.main.app_load_method.default = method.id.toString();
        // this.orm.call("res.users", "set_user_theme", [
        // 	session.uid,
        // 	{
        // 		main_app_load_method: method.id.toString(),
        // 	},
        // ]);
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: {
                    main_app_load_method: method.id.toString(),
                },
            },
        });
    }

    onToggleMainDisplayDrawerMenuButton(state) {
        this.state.theme.main.display_drawer_menu_button = !state;
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: {
                    main_display_drawer_menu_button: !state,
                },
            },
        });
    }

    onToggleMainOpenActionInTabs(state) {
        this.state.theme.main.open_action_in_tabs = !state;
        // this.orm.call("res.users", "set_user_theme", [
        // 	session.uid,
        // 	{
        // 		main_open_action_in_tabs: !state,
        // 	},
        // ]);
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: {
                    main_open_action_in_tabs: !state,
                },
            },
        });
    }

    onChangeSubmenuPosition(position) {
        this.state.theme.main.submenu.position = position.id;
        // this.orm.call("res.users", "set_user_theme", [
        // 	session.uid,
        // 	{
        // 		main_submenu_position: position.id.toString(),
        // 	},
        // ]);
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: {
                    main_submenu_position: position.id.toString(),
                },
            },
        });
    }

    //-------------------------
    // 主题颜色
    //-------------------------
    onChangeDefaultThemeColor(color) {
        this.state.theme.color.default = color.id;
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: {
                    theme_color: color.id,
                },
            },
        });
    }

    //-------------------------
    // 锁屏主题
    //-------------------------
    onChangeLockScreenTheme(ev) {
        this.state.theme.lock_screen.theme = ev.target.value;
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: {
                    lock_screen_theme: ev.target.value,
                },
            },
        });
    }

    //-------------------------
    // 侧边栏
    //-------------------------
    onToggleSidebarDisplayNumberOfSubmenus(state) {
        this.state.theme.sidebar.display_number_of_submenus = !state;
        // this.orm.call("res.users", "set_user_theme", [
        // 	session.uid,
        // 	{
        // 		sidebar_display_number_of_submenus: !state,
        // 	},
        // ]);
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: {
                    sidebar_display_number_of_submenus: !state,
                },
            },
        });
    }
    onToggleSidebarShowMinimizeButton(state) {
        this.state.theme.sidebar.show_minimize_button = !state;
        // this.orm.call("res.users", "set_user_theme", [
        // 	session.uid,
        // 	{
        // 		sidebar_show_minimize_button: !state,
        // 	},
        // ]);
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: {
                    sidebar_show_minimize_button: !state,
                },
            },
        });
    }
    onToggleSidebarDefaultMinimizedn(state) {
        this.state.theme.sidebar.default_minimized = !state;
        // this.orm.call("res.users", "set_user_theme", [
        // 	session.uid,
        // 	{
        // 		sidebar_default_minimized: !state,
        // 	},
        // ]);
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: {
                    sidebar_default_minimized: !state,
                },
            },
        });
    }
    onToggleSidebarHoverMaximize(state) {
        this.state.theme.sidebar.hover_maximize = !state;
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: {
                    sidebar_hover_maximize: !state,
                },
            },
        });
    }
    onToggleSidebarMainMenuDisplayIcon(state) {
        this.state.theme.sidebar.main_menu.display_icon = !state;
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: {
                    sidebar_main_menu_display_icon: !state,
                },
            },
        });
    }
    onToggleSidebarMainMenuDisplayArrow(state) {
        this.state.theme.sidebar.main_menu.display_arrow = !state;
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: {
                    sidebar_main_menu_display_arrow: !state,
                },
            },
        });
    }
    onToggleSidebarSubmenuDisplayIcon(state) {
        this.state.theme.sidebar.submenu.display_icon = !state;
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: {
                    sidebar_submenu_display_icon: !state,
                },
            },
        });
    }
    onToggleSidebarSubmenuDisplayArrow(state) {
        this.state.theme.sidebar.submenu.display_arrow = !state;
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: {
                    sidebar_submenu_display_arrow: !state,
                },
            },
        });
    }

    //-------------------------
    // 视图
    //-------------------------

    // 视图-向上滚动按钮
    //-------------------------
    onToggleDisplayScrollTopButton(state) {
        this.state.theme.views.display_scroll_top_button = !state;
        // this.orm.call("res.users", "set_user_theme", [
        // 	session.uid,
        // 	{
        // 		display_scroll_top_button: !state,
        // 	},
        // ]);
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: {
                    display_scroll_top_button: !state,
                },
            },
        });
    }

    // 视图-列表-列表单页显示数量限制
    //-------------------------
    onChangeListRowsLimit(ev) {
        this.state.theme.views.list.rows.limit = ev.target.value;
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: {
                    lock_screen_theme: ev.target.value,
                },
            },
        });
    }

    // 视图-Form- 使用分割线调整表单大小
    //-------------------------
    onToggleFormUseDividerResizeSheet(state) {
        this.state.theme.views.form.use_divider_resize_sheet = !state;
        this.set_body_data();
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: {
                    form_use_divider_resize_sheet: !state,
                    form_chatter_position: "1",
                },
            },
        });
    }

    // 视图-Form-Chatter-位置
    //-------------------------
    onChangeChatterPosition(position) {
        this.state.theme.views.form.chatter.position = position.id;
        this.set_body_data();
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: {
                    form_chatter_position: position.id.toString(),
                },
            },
        });
    }

    // 页脚-显示
    //-------------------------
    onToggleFooterDisplay(display) {
        this.state.theme.footer.display = !display;
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: { display_footer: !display },
            },
        });
    }

    // 页脚-显示技术支持
    //-------------------------
    onToggleFooterDisplaySupport(display) {
        this.state.theme.footer.display_support = !display;
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: { display_footer_support: !display },
            },
        });
    }

    // 页脚-显示版权
    //-------------------------
    onToggleFooterDisplayCopyright(display) {
        this.state.theme.footer.display_copyright = !display;
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: { display_footer_copyright: !display },
            },
        });
    }

    // 页脚-显示文档
    //-------------------------
    onToggleFooterDisplayDoc(display) {
        this.state.theme.footer.display_doc = !display;
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: { display_footer_doc: !display },
            },
        });
    }

    // 页脚-显示版本
    //-------------------------
    onToggleFooterDisplayVersion(display) {
        this.state.theme.footer.display_version = !display;
        this.orm.call('res.users', 'set_user_theme', [this.user.userId], {
            context: {
                theme: { display_footer_version: !display },
            },
        });
    }

    hasKey(key, obj) {
        if (obj.hasOwnProperty(key)) {
            return true;
        } else {
            return false;
        }
    }

    set_body_data() {
        document.body.setAttribute(
			"data-form-use-divider",
			this.state.theme.views.form.use_divider_resize_sheet
		); // 使用分割线调整表单大小
        document.body.setAttribute(
			"data-chatter-chatter-position",
			this.state.theme.views.form.chatter.position
		); // 聊天位置
    }
}

ThemePanel.template = 'eist_web_theme.ThemePanel';
ThemePanel.components = {};
ThemePanel.props = {};
