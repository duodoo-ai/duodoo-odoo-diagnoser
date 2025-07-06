# -*- coding: utf-8 -*-
"""
@Time    : 2022/12/23 08:44
@Author  : Jason Zou
@Email   : zou.jason@qq.com
@ 一级部门/公司跳过不处理，需手动维护ODOO与企业微信一级部门名称一致
"""
from odoo import models, fields, exceptions
import os
import json
import logging
import requests
_logger = logging.getLogger(__name__)
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
headers = {'content-type': 'application/json'}


class EWIInterface(models.Model):
    _inherit = 'ewi.interface'

    def gen_application_access_token(self):
        """授权信息，获取企微应用授权Access Token"""
        access_obj = self.env['ewi.wechat.config']
        access_record = access_obj.search([('name', '=', '企业微信接口')])
        corp_id = access_record.corp_id
        corp_secret = self.secret       # 通过每个应用动态获得
        _logger.info(f"应用授权信息{corp_id} --- {corp_secret}")
        if not corp_id or not corp_secret:
            _logger.info(f"应用授权信息{corp_secret}为空，请填入！")
            return
        token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={corp_secret}"
        for line in self:
            try:
                ret = requests.get(token_url, headers=headers)
                ret.raise_for_status()
                result = ret.json()
                if result.get('errcode') == 0:
                    line.write({'access_token': result['access_token'],
                                         'errcode': result['errcode'],
                                         'errmsg': result['errmsg'],
                                         'expires_in': result['expires_in'],
                                         })
                    return result['access_token']
                else:
                    _logger.error(f"获取企业应用Access Token失败: {result.get('errmsg')}")
                    return None
            except requests.RequestException as e:
                _logger.error(f"获取企业应用Access Token时出错: {str(e)}")
                return None

    def send_message(self):
        """发送各种应用消息"""
        access_token = self.gen_application_access_token()
        if not access_token:
            _logger.info(f"创建应用消息-----access_token------凭证为空 {access_token}")
            return
        token_url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
        data = {
           "touser" : "odoo025|18066043008",    # 指定接收消息的成员，成员ID列表（多个接收者用‘|’分隔，最多支持1000个）
           # "toparty" : "PartyID1|PartyID2",
           # "totag" : "TagID1 | TagID2",
           "msgtype" : "text",
           "agentid" : self.agentId,
           "text" : {
               "content" : "你的快递已到，请携带工卡前往邮件中心领取。聪明避开排队。"
           },
           "safe":0,
           "enable_id_trans": 0,
           "enable_duplicate_check": 0,
           "duplicate_check_interval": 1800
        }
        ret = requests.post(token_url, data=json.dumps(data), headers=headers)
        if json.loads(ret.text)['errcode'] == 0:
            _logger.info("发送应用消息成功{}".format(json.loads(ret.text)))

        else:
            _logger.error("发送应用消息失败{}".format(json.loads(ret.text)))

