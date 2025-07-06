# -*- coding: utf-8 -*-
"""
@Time    : 2025/04/13 08:50
@Author  : Jason Zou
@Email   : zou.jason@qq.com
@Company: zou.jason@qq.com
"""
from odoo import fields, models, api

class MaintenanceEquipmentInspection(models.Model):
    _name = 'maintenance.equipment.inspection'
    _description = 'Equipment Inspection Record'  # 英文描述
    _order = 'inspection_date desc'

    equipment_barcode_id = fields.Many2one(
        'maintenance.equipment.barcode',
        string='QR Code',
        help='Associated equipment QR code record'  # 英文
    )  # 关联的设备二维码记录

    equipment_id = fields.Many2one(
        'maintenance.equipment',
        string='Equipment',
        required=True,
        help='Equipment being inspected'  # 英文
    )  # 被检查的设备

    inspection_date = fields.Datetime(
        string='Inspection Date',
        default=fields.Datetime.now,
        help='Time when the inspection occurred'  # 英文
    )  # 检查发生的时间

    inspector_id = fields.Many2one(
        'res.users',
        string='Inspector',
        default=lambda self: self.env.user,
        help='Personnel performing the inspection'  # 英文
    )  # 执行检查的人员

    result = fields.Selection(
        [('pass', 'Pass'), ('fail', 'Fail')],
        string='Result',
        required=True,
        help='Inspection result: Pass or Fail'  # 英文
    )  # 检查结果：通过或不通过

    notes = fields.Text(
        string='Notes',
        help='Inspection remarks'  # 英文
    )  # 检查备注信息

    photo = fields.Binary(
        string='Photo',
        help='On-site inspection photo'  # 英文
    )  # 现场检查照片