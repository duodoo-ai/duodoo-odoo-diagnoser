# -*- coding: utf-8 -*-

import json
import odoo
from odoo import http, _
from odoo.http import request
from odoo.addons.web.controllers.session import Session
from odoo.addons.web.controllers.utils import (
    ensure_db,
    _get_login_redirect_url,
    is_user_internal,
)


UNLOCK_REQUEST_PARAMS = {
    "db",
    "login",
    "debug",
    "token",
    "message",
    "error",
    "scope",
    "mode",
    "redirect",
    "redirect_hostname",
    "email",
    "name",
    "partner_id",
    "password",
    "confirm_password",
    "city",
    "country_id",
    "lang",
    "signup_email",
}


class LockHome(Session):

    @http.route(
        "/web/session/lockscreen_info",
        type="json",
        auth="user",
        website=True,
    )
    def get_lockscreen_info(self, uid, lock_screen_info):
        """
        获取锁屏信息
        """
        result = {}
        session_info = request.env["ir.http"].session_info()

        lock_info = {
            "uid": uid,
            "href": lock_screen_info["href"],
            "host": lock_screen_info["host"],
            "pathname": lock_screen_info["pathname"],
            "search": lock_screen_info["search"],
            "hash": lock_screen_info["hash"],
        }

        try:
            lock_info["state"] = True  # 更新 lock_screen_session_info["state"] 为 True
            request.session["lock_screen_session_info"] = json.loads(json.dumps(lock_info))
            request.session.modified = True  # 标记session已修改
            result.update(
                {
                    "state": True,
                    "msg": "",
                    "lock_screen_state": True,
                }
            )
        except Exception as e:
            print("错误信息", str(e))
            result.update(
                {
                    "state": False,
                    "msg": str(e),
                }
            )
            return {
                "state": False,
            }
        finally:
            return result

    def _prepare_lock_layout_values(self):
        lock_user_sudo = request.env.user.sudo()
        session_info = request.env["ir.http"].session_info()

        current_company_id = session_info.get("user_companies").get("current_company")
        lock_screen_theme = int(session_info["theme"]["lock_screen"]["theme"])
        template = "eist_web_theme.lock1"
        if lock_screen_theme == 2:
            template = "eist_web_theme.lock2"

        return {
            "template": template,
            "lock_user": lock_user_sudo,
            "version": session_info.get("server_version"),
            "system_name": request.env["ir.config_parameter"].get_param("eist_erp.system_name"),
            "copyright": request.env["res.company"].browse(current_company_id).copyright,
        }

    @http.route(
        "/web/session/lock",
        type="http",
        auth="user",
        website=True,
        sitemap=False,
    )
    def web_lock_client(self, **kw):
        """
        锁屏页面
        """
        if "lock_screen_session_info" in request.session:
            lock_screen_session_info = request.session["lock_screen_session_info"]
            lock_screen_state = lock_screen_session_info["state"]

        values = self._prepare_lock_layout_values()
        if "lock_screen_session_info" in request.session:
            lock_screen_session_info = request.session["lock_screen_session_info"]
            request.session.modified = True  # 标记session已修改
            values.update(**lock_screen_session_info)

        session_info = request.env["ir.http"].session_info()

        screen_locked = request.env["res.users"].browse(request.session.uid).screen_locked
        # if (
        #     request.session.uid
        #     and is_user_internal(request.session.uid)
        #     and not screen_locked
        # ):
        #     if lock_screen_session_info["href"]:
        #         return request.redirect(lock_screen_session_info["href"])
        #     else:
        #         return request.redirect_query("/web", "")
        if not screen_locked:
            if lock_screen_session_info["href"]:
                return request.redirect(lock_screen_session_info["href"])
            else:
                return request.redirect_query("/web", "")

        response = request.render(values["template"], values)
        response.headers["X-Frame-Options"] = "DENY"
        return response

    @http.route("/web/session/unlock", type="json", auth="user", website=True, methods=["POST", "GET"])
    def web_unlock_client(self, **params):
        """
        解锁页面
        """
        ensure_db()
        session_info = request.env["ir.http"].session_info()
        lock_screen_session_info = request.session["lock_screen_session_info"]

        values = {k: v for k, v in request.params.items() if k in UNLOCK_REQUEST_PARAMS}
        values = self._prepare_lock_layout_values()

        if request.params["password"] == "":
            values["error"] = _("The password cannot be empty")
            values["unlock_success"] = False
        else:
            if request.httprequest.method == "POST":
                try:
                    credential = {
                        "login": request.params["login"],
                        "password": request.params["password"],
                        "type": "password",
                    }
                    auth_info = request.session.authenticate(session_info.get("db"), credential)
                    values["message"] = _("The password is correct, unlocking...")
                    values["unlock_success"] = True

                    user = (
                        request.env["res.users"]
                        .sudo()
                        .search([("id", "=", lock_screen_session_info.get("uid"))], limit=1)
                    )
                    user.write({"screen_locked": False})
                    user._bus_send("unlock_screen", {})
                    request.session["lock_screen_session_info"]["state"] = False
                    request.session.modified = True  # 标记session已修改
                except odoo.exceptions.AccessDenied as e:
                    values["unlock_success"] = False
                    if e.args == odoo.exceptions.AccessDenied().args:
                        values["error"] = _("Wrong password")
                    else:
                        values["error"] = e.args[0]


            else:
                if "error" in request.params and request.params.get("error") == "access":
                    values["unlock_success"] = False
                    values["error"] = _(
                        "Only employees can access this database. Please contact the administrator."
                    )

        return values

    @http.route("/web/session/lock_user", type="json", auth="user", website=True)
    def web_lock_user(self, uid):
        try:
            user = request.env["res.users"].sudo().browse(uid)
            user.write({"screen_locked": True})
            return True
        except Exception as e:
            return False

    @http.route("/web/session/unlock_user", type="json", auth="user", website=True)
    def web_unlock_user(self, uid):
        result = {}
        try:
            user = request.env["res.users"].sudo().browse(uid)
            user.write({"screen_locked": False})
            return True
        except Exception as e:
            return False

    @http.route()
    def logout(self, redirect="/odoo"):
        company = request.env["res.users"].sudo().browse(request.session.uid).company_id
        if request.session.uid:
            request.env["res.users"].sudo().browse(request.session.uid).write({"screen_locked": False})
        return super().logout(redirect)
