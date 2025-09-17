# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # ------------------------------------------------------------
    # 品牌设置
    # ------------------------------------------------------------
    system_name = fields.Char(
        string="System Name",
        readonly=False,
        default="EIST ERP",
        config_parameter="eist_erp.system_name",
    )
    display_company_name = fields.Boolean(
        string="Display Company Name",
        default=False,
        config_parameter="eist_erp.display_company_name",
    )
    # full_system_name = fields.Char(
    #     config_parameter="eist_erp.full_system_name", compute="_compute_full_system_name"
    # )
    logo = fields.Binary(related="company_id.logo", readonly=False)
    square_logo = fields.Binary(related="company_id.square_logo", readonly=False)
    favicon = fields.Binary(related="company_id.favicon", readonly=False)
    copyright = fields.Char(related="company_id.copyright", readonly=False)
    doc_url = fields.Char(related="company_id.doc_url", readonly=False)
    support_url = fields.Char(related="company_id.support_url", readonly=False)

    # 多公司管理-限制不同公司的系统管理员只能看到自己公司/以及公司所属系统用户的数据
    multi_company_system_data_limit = fields.Boolean(
        string="Multi Company Data Access Limit",
        default=False,
        config_parameter="eist_erp.multi_company_system_data_limit",
    )

    # 应用
    module_eist_web_theme = fields.Boolean(string="Web Theme", default=False)
    module_eist_web_toolbox = fields.Boolean(string="Web ToolBox", default=False)
    module_eist_report_management = fields.Boolean(string="Report Management", default=False)

    hide_enterprise_app = fields.Boolean(
        string="Hide Enterprise App",
        default=False,
        config_parameter="eist_erp.hide_enterprise_app",
    )

    # 解决方案-Pos
    module_eist_pos = fields.Boolean(string="Solutions for stores and restaurants", default=False)

    # 解决方案-社交应用
    module_eist_social = fields.Boolean(string="Social integration", default=False)
    module_eist_social_wechat = fields.Boolean(string="WeChat integration", default=False)
    module_eist_social_wecom = fields.Boolean(string="Wecom integration", default=False)
    module_eist_social_feishu = fields.Boolean(string="Feishu integration", default=False)
    module_eist_social_dingding = fields.Boolean(string="Dingding integration", default=False)

    # 扩展功能
    module_eist_geolocalize = fields.Boolean(string="Partners Geolocation", default=False)
    module_eist_multi_platform = fields.Boolean(string="Multi platform access", default=False)

    @api.onchange("hide_enterprise_app")
    def _onchange_hide_enterprise_app(self):
        """
        隐藏企业版应用
        """
        modules = self.env["ir.module.module"].search(
            ["&", ("to_buy", "=", True), ("application", "=", True)]
        )
        for module in modules:
            module.write({"application": not self.hide_enterprise_app})
        self.env["ir.module.module"].update_list()  # 避免打开设置页面报错

    # @api.onchange("multi_company_system_data_limit")
    # def _onchange_multi_company_system_data_limit(self):
    #     """
    #     限制不同公司的系统管理员只能看到自己公司/以及公司所属系统用户的数据
    #     """
    #     try:
    #         # 获取安全规则引用
    #         companies_rule = self.env.ref(
    #             "eist_erp_base.eist_companies_rule_multi_company", raise_if_not_found=False
    #         )
    #         users_rule = self.env.ref(
    #             "eist_erp_base.eist_users_rule_multi_company_system_user", raise_if_not_found=False
    #         )

    #         if self.multi_company_system_data_limit:
    #             # 启用多公司数据访问限制规则
    #             if companies_rule:
    #                 companies_rule.active = True
    #             if users_rule:
    #                 users_rule.active = True
    #         else:
    #             # 禁用多公司数据访问限制规则
    #             if companies_rule:
    #                 companies_rule.active = False
    #             if users_rule:
    #                 users_rule.active = False
    #     except Exception as e:
    #         # 如果规则不存在，记录日志但不中断流程
    #         _logger.warning("无法找到多公司数据访问限制规则: %s", str(e))

    @api.depends("company_id", "system_name", "display_company_name")
    def _compute_full_system_name(self):
        for record in self:
            print("company_id", record.company_id.name)
            main_company = self.sudo().env.ref("base.main_company")
            if record.display_company_name:
                record.full_system_name = "%s - %s" % (
                    main_company.name,
                    record.system_name,
                )
            else:
                record.full_system_name = record.system_name
