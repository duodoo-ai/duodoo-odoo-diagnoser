# -*- coding: utf-8 -*-
"""
@Time    : 2022/12/22 08:44
@Author  : Jason Zou
@Email   : zou.jason@qq.com
"""
from odoo import models, fields, exceptions
import os
import json
import logging
import requests
_logger = logging.getLogger(__name__)
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
headers = {'content-type': 'application/json'}


class EwiWechatConfig(models.Model):
    _name = 'ewi.wechat.config'
    _description = '接口认证信息'

    # 定义接口基本信息
    name = fields.Char(string='Auth接口名称', default='企业微信接口', help='API名称')
    corp_id = fields.Char(string='企业ID',
                          default='wwc87ed859c36005b2',
                          help='路径：我的企业-企业信息-企业ID')
    secret = fields.Char(string='通讯录同步Secret',
                         help='通讯录同步，注意应用需要是启用状态，获取方式参考：术语说明-secret')

    # 定义“审批”应用对接信息
    sp_AgentId = fields.Char(string='审批AgentId',
                             default='3010040',
                             help='路径：审批-AgentId')
    sp_Secret = fields.Char(string='审批Secret',
                            default='ub3ELV5X9d1JGkwmC9If_qr0szG78ogYBnGKZnCQPEg',
                            help='路径：审批-Secret-查看')
    sp_URL = fields.Char(string='审批URL',
                         default='http://bpm-test.dingyang.com:8069/corp_handler',
                         help='路径：审批-接收消息服务器配置-URL')
    sp_access_token = fields.Char(string='审批Token',
                                  default='TKkL0wVvklvIXD',
                                  help='路径：审批-接收消息服务器配置-Token')
    sp_EncodingAESKey = fields.Char(string='审批EncodingAESKey',
                                    default='vzpWA1cL9D8vPwgFOqTjFaysLhNbV36kWcXODL6knxf',
                                    help='路径：审批-接收消息服务器配置-EncodingAESKey')
