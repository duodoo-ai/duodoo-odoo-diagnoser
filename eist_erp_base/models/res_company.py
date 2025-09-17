# -*- coding: utf-8 -*-

import base64
import datetime
import logging

from odoo import models, fields, api, tools, _
from odoo.tools import html2plaintext, file_open, ormcache
from odoo.modules.module import get_module_resource
from odoo.tools import html2plaintext, file_open, ormcache

_logger = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = "res.company"

    fax = fields.Char(related="partner_id.fax", store=True, readonly=False)

    def _get_favicon(self):
        # favicon_path = get_module_resource('eist_erp_base', 'static/img', 'square_logo.png')
        # with open(favicon_path, "rb") as f:
        #     return base64.b64encode(f.read())
        with file_open("eist_erp_base/static/img/square_logo.png", "rb") as file:
            return base64.b64encode(file.read())

    def _get_square_logo(self):
        # logo_path = get_module_resource('eist_erp_base', 'static/img', 'square_logo.png')
        # with open(logo_path, "rb") as f:
        #     return base64.b64encode(f.read())
        with file_open("eist_erp_base/static/img/square_logo.png", "rb") as file:
            return base64.b64encode(file.read())

    favicon = fields.Binary(
        string="Company Favicon",
        help="This field holds the image used to display a favicon for a given company.",
        default=_get_favicon,
    )
    square_logo = fields.Binary(
        default=_get_square_logo,
        # related="partner_id.image_1920",
        string="Company Square Logo",
        readonly=False,
    )
    square_logo_web = fields.Binary(compute="_compute_square_logo_web", store=True, attachment=False)
    short_name = fields.Char("Short Name", translate=True)

    def _get_default_copyright(self):
        """
        年份© 公司名称
        """
        return "%s© %s" % (datetime.datetime.today().year, (self.name if self.name else "EIST"))  # type: ignore

    copyright = fields.Char(string="Copyright", default=_get_default_copyright)
    doc_url = fields.Char(string="Documentation URL", default="https://docs.eist.com.cn")
    support_url = fields.Char(string="Support URL", default="https://eist.com.cn/")

    @api.depends("square_logo")
    def _compute_square_logo_web(self):
        for company in self:
            img = company.square_logo
            company.square_logo_web = img and base64.b64encode(
                tools.image_process(base64.b64decode(img), size=(46, 0))
            )

    # ----------------------
    # 系统参数控制功能开关开启后：
    # 1. 用户id=1 或 用户id=2的用户可以访问所有公司
    # 2. 与用户company_id 相同的公司列表
    # 3. company_ids 包含用户 company_id 的公司列表
    # ----------------------

    # @api.model
    # def _search(self, domain, offset=0, limit=None, order=None):
    #     """
    #     重写搜索方法，实现多公司访问控制
    #     """
    #     ICP = self.env["ir.config_parameter"].sudo()
    #     limit_company_access = ICP.get_param("eist_erp.multi_company_system_data_limit")

    #     if not limit_company_access:
    #         return super(Company, self)._search(domain, offset, limit, order)
    #     else:
    #         # 获取当前用户ID，避免递归
    #         current_user = self.env.user
    #         current_user_id = current_user.id

    #         # 检查用户ID是否有效
    #         if not current_user_id or current_user_id is False:
    #             _logger.warning(f"无效的用户ID: {current_user_id}，返回原始查询结果")
    #             return super(Company, self)._search(domain, offset, limit, order)

    #         # 系统用户、超级用户或管理员可以访问所有公司
    #         if current_user.id in [1, 2]:
    #             _logger.info(f"用户 {current_user_id} (系统/超级) 可以访问所有公司")
    #             return super(Company, self)._search(domain, offset, limit, order)

    #         # 直接使用SQL查询获取用户公司信息，完全避免触发 _search
    #         self.env.cr.execute("SELECT company_id FROM res_users WHERE id = %s", (current_user_id,))
    #         result = self.env.cr.fetchone()
    #         user_company_id = result[0] if result else False

    #         if not user_company_id:
    #             # 如果用户没有公司，返回空结果
    #             return []

    #         # 构建访问控制域：满足任一条件
    #         # 1. 用户 company_id 相等的公司
    #         # 2. 用户 company_ids 包含的公司
    #         access_domain = [
    #             "|",
    #             ("id", "=", user_company_id),  # 用户 company_id 相等的公司
    #             ("id", "in", self._get_user_company_ids(current_user_id)),  # 用户 company_ids 包含的公司
    #         ]

    #         # 合并原始域和访问控制域
    #         if domain:
    #             final_domain = ["&"] + domain + access_domain
    #         else:
    #             final_domain = access_domain

    #         _logger.info(f"用户 {current_user_id} 公司搜索域: {final_domain}")
    #         return super(Company, self)._search(final_domain, offset, limit, order)

    # @api.model
    # def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
    #     """
    #     重写 search_read 方法，确保读取时也应用访问控制
    #     """
    #     ICP = self.env["ir.config_parameter"].sudo()
    #     limit_company_access = ICP.get_param("eist_erp.multi_company_system_data_limit")

    #     if not limit_company_access:
    #         return super(Company, self).search_read(domain, fields, offset, limit, order)
    #     else:
    #         # 获取当前用户ID，避免递归
    #         current_user = self.env.user
    #         current_user_id = current_user.id

    #         # 检查用户ID是否有效
    #         if not current_user_id or current_user_id is False:
    #             _logger.warning(f"无效的用户ID: {current_user_id}，返回原始查询结果")
    #             return super(Company, self).search_read(domain, fields, offset, limit, order)

    #         # 系统用户、超级用户或管理员可以访问所有公司
    #         if current_user.id in [1, 2]:
    #             _logger.info(f"用户 {current_user_id} (系统/超级) 可以访问所有公司")
    #             return super(Company, self).search_read(domain, fields, offset, limit, order)

    #         # 直接使用SQL查询获取用户公司信息，完全避免触发 _search
    #         self.env.cr.execute("SELECT company_id FROM res_users WHERE id = %s", (current_user_id,))
    #         result = self.env.cr.fetchone()
    #         user_company_id = result[0] if result else False

    #         if not user_company_id:
    #             # 如果用户没有公司，返回空结果
    #             return []

    #         # 构建访问控制域：满足任一条件
    #         # 1. 用户 company_id 相等的公司
    #         # 2. 用户 company_ids 包含的公司
    #         access_domain = [
    #             "|",
    #             ("id", "=", user_company_id),  # 用户 company_id 相等的公司
    #             ("id", "in", self._get_user_company_ids(current_user_id)),  # 用户 company_ids 包含的公司
    #         ]

    #         # 合并原始域和访问控制域
    #         if domain:
    #             final_domain = ["&"] + domain + access_domain
    #         else:
    #             final_domain = access_domain

    #         return super(Company, self).search_read(final_domain, fields, offset, limit, order)

    # def _get_user_company_ids(self, user_id):
    #     """
    #     获取用户的 company_ids
    #     """
    #     try:
    #         self.env.cr.execute(
    #             "SELECT cid FROM res_company_users_rel WHERE user_id = %s",
    #             (user_id,),
    #         )
    #         return [row[0] for row in self.env.cr.fetchall()]
    #     except Exception as e:
    #         _logger.error(f"无法获取用户 {user_id} 的 company_ids: {e}")
    #         return []
