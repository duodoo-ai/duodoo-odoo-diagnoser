/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

export class LockScreen extends Component {
    setup() {
        this.busService = useService("bus_service");
        this.notification = useService("notification");
        this.state = useState({
            login: "",
            password: "",
            error: "",
            message: "",
            redirect: "/web",
        });

        this.busService.subscribe("unlock_screen", () => {
            this.unlockScreen();
        });

        onMounted(() => {
            // 你可以在这里做一些初始化
        });
    }

    async onUnlock(ev) {
        ev.preventDefault();
        const result = await rpc("/web/session/unlock", {
            login: this.state.login,
            password: this.state.password,
        });
        if (result.error) {
            this.state.error = result.error;
        } else if (result.unlock_success) {
            this.state.error = "";
            this.state.message = result.message;
            setTimeout(() => {
                window.location.href = this.state.redirect;
            }, 2000);
        }
    }

    unlockScreen() {
        window.location.href = this.state.redirect;
    }
}