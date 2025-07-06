# -*- coding: utf-8 -*-
"""
@Time    : 2022/12/22 08:44
@Author  : Jason Zou
@Email   : zou.jason@qq.com
"""
from odoo import models, fields, api


class HrDeptManage(models.Model):
    _inherit = 'hr.department'

    ewc_dept_order = fields.Integer(string='WeChat FID') # WeChat部门唯一ID


