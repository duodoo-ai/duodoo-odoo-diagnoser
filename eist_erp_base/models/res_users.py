# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError
import logging
import threading
import time

_logger = logging.getLogger(__name__)

# 使用线程本地存储来跟踪创建用户状态
_creating_user_local = threading.local()


class Users(models.Model):
    _inherit = "res.users"

    """
    系统参数控制功能开关开启后：
    1. 用户id=1 或 用户id=2的用户可以访问所有用户，直接返回原始查询结果
    2. 检查是否在创建用户的过程中，如果是，则跳过访问控制，直接返回原始查询结果
    3. 获取当前用户ID，避免递归
    4. 用户id!=1 或 用户id!=2，返回去除 用户id=2 或 用户id=7 的查询结果
    5. 与自己 company_id 相同的用户列表
    6. company_ids 包含自己 company_id 的用户列表
    """

    # @api.model
    # def _search(self, domain, offset=0, limit=None, order=None):
    #     """
    #     重写搜索方法，实现多公司用户访问控制
    #     """
    #     ICP = self.env["ir.config_parameter"].sudo()
    #     limit_company_access = ICP.get_param("eist_erp.multi_company_system_data_limit")

    #     if not limit_company_access:
    #         return super(Users, self)._search(domain, offset, limit, order)
    #     else:
    #         # 检查是否在创建用户的过程中
    #         if (
    #             self.env.context.get("creating_user")
    #             or self.env.context.get("create_user")
    #             or getattr(_creating_user_local, "is_creating", False)
    #             or getattr(_creating_user_local, "just_created", False)
    #         ):
    #             # 在创建用户时，暂时禁用访问控制
    #             _logger.info("创建用户过程中，跳过访问控制")
    #             return super(Users, self)._search(domain, offset, limit, order)

    #         # 获取当前用户ID，避免递归
    #         current_user = self.env.user
    #         current_user_id = current_user.id

    #         # 检查用户ID是否有效
    #         if not current_user_id or current_user_id is False:
    #             _logger.warning(f"无效的用户ID: {current_user_id}，返回原始查询结果")
    #             return super(Users, self)._search(domain, offset, limit, order)

    #         # 系统用户、超级用户或管理员可以访问所有用户
    #         if current_user.id in [1, 2]:
    #             _logger.info(f"用户 {current_user_id} (系统/超级) 可以访问所有用户")
    #             return super(Users, self)._search(domain, offset, limit, order)

    #         # 直接使用SQL查询获取用户公司信息，完全避免触发 _search
    #         self.env.cr.execute("SELECT company_id FROM res_users WHERE id = %s", (current_user_id,))
    #         result = self.env.cr.fetchone()
    #         user_company_id = result[0] if result else False

    #         if not user_company_id:
    #             # 如果用户没有公司，返回空结果
    #             return []

    #         # 构建访问控制域：满足任一条件
    #         # 1. company_id 相等的用户
    #         # 2. company_ids 包含用户 company_id 的用户
    #         # 3. 排除特殊用户ID (2, 7)
    #         access_domain = [
    #             "&",
    #             "|",
    #             ("company_id", "=", user_company_id),  # company_id 相等的用户
    #             ("company_ids", "in", user_company_id),  # company_ids 包含用户 company_id 的用户
    #             "!",
    #             ("id", "in", [2, 7]),  # 排除特殊用户ID
    #         ]

    #         # 合并原始域和访问控制域
    #         if domain:
    #             final_domain = ["&"] + domain + access_domain
    #         else:
    #             final_domain = access_domain

    #         _logger.info(f"用户 {current_user_id} 搜索域: {final_domain}")
    #         # _logger.info(f"用户 {current_user_id} 的 company_id: {user_company_id}")

    #         # 检查要访问的用户信息（仅在调试时启用）
    #         # if domain:
    #         #     for item in domain:
    #         #         if isinstance(item, tuple) and len(item) == 3 and item[0] == "id" and item[1] == "in":
    #         #             if isinstance(item[2], list):
    #         #                 for user_id in item[2]:
    #         #                     try:
    #         #                         # 使用SQL查询获取用户信息，避免递归
    #         #                         self.env.cr.execute(
    #         #                             "SELECT company_id FROM res_users WHERE id = %s", (user_id,)
    #         #                         )
    #         #                         user_result = self.env.cr.fetchone()
    #         #                         if user_result:
    #         #                             user_company = user_result[0]
    #         #                             # 获取 company_ids - 使用正确的表名
    #         #                         self.env.cr.execute(
    #         #                             "SELECT cid FROM res_company_users_rel WHERE user_id = %s",
    #         #                             (user_id,),
    #         #                         )
    #         #                         company_ids = [row[0] for row in self.env.cr.fetchall()]
    #         #                         _logger.info(
    #         #                             f"用户 {user_id} - company_id: {user_company}, company_ids: {company_ids}"
    #         #                         )
    #         #                     except Exception as e:
    #         #                         _logger.error(f"无法获取用户 {user_id} 信息: {e}")

    #         return super(Users, self)._search(final_domain, offset, limit, order)

    # @api.model
    # def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
    #     """
    #     重写 search_read 方法，确保读取时也应用访问控制
    #     """
    #     ICP = self.env["ir.config_parameter"].sudo()
    #     limit_company_access = ICP.get_param("eist_erp.multi_company_system_data_limit")

    #     if not limit_company_access:
    #         return super(Users, self).search_read(domain, fields, offset, limit, order)
    #     else:
    #         # 检查是否在创建用户的过程中
    #         if (
    #             self.env.context.get("creating_user")
    #             or self.env.context.get("create_user")
    #             or getattr(_creating_user_local, "is_creating", False)
    #             or getattr(_creating_user_local, "just_created", False)
    #         ):
    #             # 在创建用户时，暂时禁用访问控制
    #             _logger.info("创建用户过程中，跳过访问控制")
    #             return super(Users, self).search_read(domain, fields, offset, limit, order)

    #         # 获取当前用户ID，避免递归
    #         current_user = self.env.user
    #         current_user_id = current_user.id

    #         # 检查用户ID是否有效
    #         if not current_user_id or current_user_id is False:
    #             _logger.warning(f"无效的用户ID: {current_user_id}，返回原始查询结果")
    #             return super(Users, self).search_read(domain, fields, offset, limit, order)

    #         # 系统用户、超级用户或管理员可以访问所有用户
    #         if current_user.id in [1, 2]:
    #             _logger.info(f"用户 {current_user_id} (系统/超级) 可以访问所有用户")
    #             return super(Users, self).search_read(domain, fields, offset, limit, order)

    #         # 直接使用SQL查询获取用户公司信息，完全避免触发 _search
    #         self.env.cr.execute("SELECT company_id FROM res_users WHERE id = %s", (current_user_id,))
    #         result = self.env.cr.fetchone()
    #         user_company_id = result[0] if result else False

    #         if not user_company_id:
    #             # 如果用户没有公司，返回空结果
    #             return []

    #         # 构建访问控制域：满足任一条件
    #         # 1. company_id 相等的用户
    #         # 2. company_ids 包含用户 company_id 的用户
    #         # 3. 排除特殊用户ID (2, 7)
    #         access_domain = [
    #             "&",
    #             "|",
    #             ("company_id", "=", user_company_id),  # company_id 相等的用户
    #             ("company_ids", "in", user_company_id),  # company_ids 包含用户 company_id 的用户
    #             "!",
    #             ("id", "in", [2, 7]),  # 排除特殊用户ID
    #         ]

    #         # 合并原始域和访问控制域
    #         if domain:
    #             final_domain = ["&"] + domain + access_domain
    #         else:
    #             final_domain = access_domain

    #         # _logger.info(f"用户 {current_user_id} search_read 域: {final_domain}")
    #         return super(Users, self).search_read(final_domain, fields, offset, limit, order)

    # def read(self, fields=None, load="_classic_read"):
    #     """
    #     重写 read 方法，在创建用户时允许访问
    #     """
    #     ICP = self.env["ir.config_parameter"].sudo()
    #     limit_company_access = ICP.get_param("eist_erp.multi_company_system_data_limit")

    #     if not limit_company_access:
    #         return super(Users, self).read(fields, load)
    #     else:
    #         # 检查是否在创建用户的过程中
    #         if (
    #             self.env.context.get("creating_user")
    #             or self.env.context.get("create_user")
    #             or getattr(_creating_user_local, "is_creating", False)
    #             or getattr(_creating_user_local, "just_created", False)
    #         ):
    #             # 在创建用户时，暂时禁用访问控制
    #             _logger.info("创建用户过程中，跳过访问控制")
    #             return super(Users, self).read(fields, load)

    #         # 正常调用父类的 read 方法
    #         return super(Users, self).read(fields, load)

    # @api.model_create_multi
    # def create(self, vals_list):
    #     """
    #     重写 create 方法，在创建用户时设置上下文标记
    #     """
    #     ICP = self.env["ir.config_parameter"].sudo()
    #     limit_company_access = ICP.get_param("eist_erp.multi_company_system_data_limit")

    #     if limit_company_access:
    #         # 设置创建用户的上下文标记和线程本地标记
    #         self = self.with_context(creating_user=True)
    #         _creating_user_local.is_creating = True
    #         _logger.info("设置创建用户上下文标记和线程本地标记")

    #     try:
    #         result = super(Users, self).create(vals_list)
    #         if limit_company_access:
    #             # 创建完成后，设置just_created标记，延迟清理
    #             _creating_user_local.just_created = True
    #             _creating_user_local.just_created_time = time.time()
    #             _logger.info("设置just_created标记")
    #         return result
    #     finally:
    #         if limit_company_access:
    #             # 清理线程本地标记
    #             _creating_user_local.is_creating = False
    #             _logger.info("清理创建用户线程本地标记")

    # def browse(self, ids=()):
    #     """
    #     重写 browse 方法，在创建用户时允许访问
    #     """
    #     ICP = self.env["ir.config_parameter"].sudo()
    #     limit_company_access = ICP.get_param("eist_erp.multi_company_system_data_limit")

    #     if not limit_company_access:
    #         return super(Users, self).browse(ids)
    #     else:
    #         # 检查是否在创建用户的过程中 - 更严格的检查
    #         if (
    #             self.env.context.get("creating_user")
    #             or self.env.context.get("create_user")
    #             or getattr(_creating_user_local, "is_creating", False)
    #             or getattr(_creating_user_local, "just_created", False)
    #             or self.env.context.get("skip_access_control")  # 新增：跳过访问控制标记
    #         ):
    #             # 在创建用户时，暂时禁用访问控制
    #             _logger.info("创建用户过程中，跳过访问控制")
    #             return super(Users, self).browse(ids)

    #         # 正常调用父类的 browse 方法
    #         return super(Users, self).browse(ids)

    # def fetch(self, fnames):
    #     """
    #     重写 fetch 方法，在创建用户时允许访问
    #     """
    #     ICP = self.env["ir.config_parameter"].sudo()
    #     limit_company_access = ICP.get_param("eist_erp.multi_company_system_data_limit")

    #     if not limit_company_access:
    #         return super(Users, self).fetch(fnames)
    #     else:
    #         # 检查是否在创建用户的过程中
    #         if (
    #             self.env.context.get("creating_user")
    #             or self.env.context.get("create_user")
    #             or getattr(_creating_user_local, "is_creating", False)
    #             or getattr(_creating_user_local, "just_created", False)
    #         ):
    #             # 在创建用户时，暂时禁用访问控制
    #             _logger.info("创建用户过程中，跳过访问控制")
    #             return super(Users, self).fetch(fnames)

    #         # 正常调用父类的 fetch 方法
    #         return super(Users, self).fetch(fnames)

    # def write(self, vals):
    #     """
    #     重写 write 方法，在创建用户时允许访问
    #     """
    #     ICP = self.env["ir.config_parameter"].sudo()
    #     limit_company_access = ICP.get_param("eist_erp.multi_company_system_data_limit")

    #     if not limit_company_access:
    #         return super(Users, self).write(vals)
    #     else:
    #         # 检查是否在创建用户的过程中
    #         if (
    #             self.env.context.get("creating_user")
    #             or self.env.context.get("create_user")
    #             or getattr(_creating_user_local, "is_creating", False)
    #             or getattr(_creating_user_local, "just_created", False)
    #         ):
    #             # 在创建用户时，暂时禁用访问控制
    #             _logger.info("创建用户过程中，跳过访问控制")
    #             return super(Users, self).write(vals)

    #         # 正常调用父类的 write 方法
    #         return super(Users, self).write(vals)
