# -*- coding: utf-8 -*-

import json
import logging
from pickle import TRUE


from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.addons.web.controllers.home import Home as WebHome # type: ignore
from odoo.addons.web.controllers.utils import (
    ensure_db,
    _get_login_redirect_url,
    is_user_internal,
)


class Home(WebHome):

    @http.route()
    def web_client(self, s_action=None, **kw):
        """
        继承 web_client ，判断是否有锁屏信息
        """
        ensure_db()
        if not request.session.uid:
            return request.redirect('/web/login', 303)
        company = request.env['res.users'].sudo().browse(request.session.uid).company_id


        if "lock_screen_session_info" in request.session:
            lock_screen_session_info = request.session["lock_screen_session_info"]
            lock_screen_state = lock_screen_session_info["state"]
        else:
            lock_screen_state = False

        if lock_screen_state:
            return request.redirect('/web/session/lock', 303)
        screen_locked = request.env["res.users"].browse(request.session.uid).screen_locked
        if (
            request.session.uid
            and is_user_internal(request.session.uid)
            and screen_locked
        ):
            return request.redirect_query("/web/session/lock", "")
        return super().web_client(s_action, **kw)

    @http.route("/web/lang/toggle", type="json", auth="user")
    def toggle_web_lang(self, lang):
        uid = dict(request.context)["uid"]
        if not uid:
            return False

        user = request.env["res.users"].browse(uid)
        try:
            user.sudo().write({"lang": lang["code"]})
        except Exception as e:
            print(str(e))
            return False
        else:
            session_info = request.env["ir.http"].session_info()
            session_info["current_lang"] = lang
            return True
