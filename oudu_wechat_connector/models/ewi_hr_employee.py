# -*- coding: utf-8 -*-
"""
@Time    : 2022/12/22 08:44
@Author  : Jason Zou
@Email   : zou.jason@qq.com
"""
from odoo import models, fields


class HrEmpAccount(models.Model):
    _inherit = 'hr.employee'

    ewc_employee_order = fields.Char(string='WeChat FID')  # WeChat职工账号
    ewc_enable = fields.Boolean(string='Enable Employee', default=True,
                                help='Check to Disable sync, default checked')  # 默认启用企业微信职工

