# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = "res.users"

    """
    1. 与自己 company_id 相同的用户
    2. company_ids 包含自己 company_id 的用户
    """

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        """
        重写搜索方法，实现多公司用户访问控制
        """
        ICP = self.env["ir.config_parameter"].sudo()
        limit_company_access = ICP.get_param("eist_erp.multi_company_system_data_limit")

        if not limit_company_access:
            return super(Users, self)._search(domain, offset, limit, order)
        else:
            # 获取当前用户的公司信息 - 使用 sudo() 避免递归
            current_user = self.env.user.sudo()
            user_company_id = current_user.company_id.id

            # 构建访问控制域：满足任一条件
            # 1. company_id 相等的用户
            # 2. company_ids 包含用户 company_id 的用户
            access_domain = [
                "|",
                ("company_id", "=", user_company_id),  # company_id 相等的用户
                ("company_ids", "in", user_company_id),  # company_ids 包含用户 company_id 的用户
            ]

            # 合并原始域和访问控制域
            if domain:
                final_domain = ["&"] + domain + access_domain
            else:
                final_domain = access_domain

            _logger.info(f"用户 {current_user.id} 搜索域: {final_domain}")
            _logger.info(f"用户 {current_user.id} 的 company_id: {user_company_id}")

            # 检查要访问的用户信息
            if domain:
                for item in domain:
                    if isinstance(item, tuple) and len(item) == 3 and item[0] == "id" and item[1] == "in":
                        if isinstance(item[2], list):
                            for user_id in item[2]:
                                try:
                                    user = self.env["res.users"].sudo().browse(user_id)
                                    _logger.info(
                                        f"用户 {user_id} - company_id: {user.company_id.id}, company_ids: {user.company_ids.ids}"
                                    )
                                except Exception as e:
                                    _logger.error(f"无法获取用户 {user_id} 信息: {e}")

            return super(Users, self)._search(final_domain, offset, limit, order)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """
        重写 search_read 方法，确保读取时也应用访问控制
        """
        ICP = self.env["ir.config_parameter"].sudo()
        limit_company_access = ICP.get_param("eist_erp.multi_company_system_data_limit")

        if not limit_company_access:
            return super(Users, self).search_read(domain, fields, offset, limit, order)
        else:
            # 获取当前用户的公司信息 - 使用 sudo() 避免递归
            current_user = self.env.user.sudo()
            user_company_id = current_user.company_id.id

            # 构建访问控制域：满足任一条件
            # 1. company_id 相等的用户
            # 2. company_ids 包含用户 company_id 的用户
            access_domain = [
                "|",
                ("company_id", "=", user_company_id),  # company_id 相等的用户
                ("company_ids", "in", user_company_id),  # company_ids 包含用户 company_id 的用户
            ]

            # 合并原始域和访问控制域
            if domain:
                final_domain = ["&"] + domain + access_domain
            else:
                final_domain = access_domain

            _logger.info(f"用户 {current_user.id} search_read 域: {final_domain}")
            return super(Users, self).search_read(final_domain, fields, offset, limit, order)
