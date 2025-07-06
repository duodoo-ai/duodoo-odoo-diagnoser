# -*- coding: utf-8 -*-
"""
@Time    : 2025/04/13 08:50
@Author  : Jason Zou
@Email   : zou.jason@qq.com
@Company: zou.jason@qq.com
"""
from odoo import fields, models

class MaintenanceWorkOrderHistory(models.Model):
    """Model for recording maintenance work order history."""
    _name = 'maintenance.work.order.history'
    _description = 'Maintenance Work Order History'

    work_order_id = fields.Many2one('maintenance.work.order', string='Work Order', required=True, ondelete='cascade')
    event_type = fields.Char(string='Event Type')
    description = fields.Text(string='Description')
    event_date = fields.Datetime(string='Event Date', default=fields.Datetime.now)