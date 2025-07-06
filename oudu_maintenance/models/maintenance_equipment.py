# -*- coding: utf-8 -*-
"""
@Time    : 2025/04/13 08:50
@Author  : Jason Zou
@Email   : zou.jason@qq.com
@Company: zou.jason@qq.com
"""
import qrcode
from io import BytesIO
import base64
from odoo import fields, models, api
from odoo.exceptions import UserError

class MaintenanceEquipment(models.Model):
    """Model for managing maintenance equipment."""
    _inherit = 'maintenance.equipment'

    # 关联设备分类
    category_id = fields.Many2one(
        'maintenance.equipment.category',
        string='Equipment Category',
        help='The category of the equipment.'
    )
    # 设备状态
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
        ('scrapped', 'Scrapped')
    ], string='Status', default='active', help='Current status of the equipment.')
    status_history_ids = fields.One2many(
        'maintenance.equipment.status.history',
        'equipment_id',
        string='Status History'
    )
    printed = fields.Boolean(string='Printed', default=False)

    # def unlock(self):
    #     """解锁记录"""
    #     self.write({'printed': False})

    def change_status(self, new_status):
        """Change the status of the equipment and record the history."""
        self.ensure_one()
        self.status = new_status
        self.env['maintenance.equipment.status.history'].create({
            'equipment_id': self.id,
            'status': new_status,
            'change_date': fields.Datetime.now()
        })

    @api.model_create_multi
    def create(self, vals_list):
        """Create a new record and record the initial status history."""
        records = super().create(vals_list)
        for record in records:
            if 'status' in vals_list[0]:
                record.env['maintenance.equipment.status.history'].create({
                    'equipment_id': record.id,
                    'status': record.status,
                    'change_date': fields.Datetime.now()
                })
        return records

    def write(self, vals):
        """Record the status history when the status field is updated."""
        old_statuses = {record: record.status for record in self}
        result = super().write(vals)
        if 'status' in vals:
            for record in self:
                old_status = old_statuses[record]
                if old_status != record.status:
                    record.env['maintenance.equipment.status.history'].create({
                        'equipment_id': record.id,
                        'status': record.status,
                        'change_date': fields.Datetime.now()
                    })
        return result

    # # 在MaintenanceEquipment类中添加
    # inspection_ids = fields.One2many(
    #     'maintenance.equipment.inspection',
    #     'equipment_id',
    #     string='巡检记录'
    # )
    #
    # def action_create_inspection(self):
    #     """创建巡检记录"""
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': '新建巡检',
    #         'res_model': 'maintenance.equipment.inspection',
    #         'view_mode': 'form',
    #         'target': 'current',
    #         'context': {'default_equipment_id': self.id}
    #     }


class MaintenanceEquipmentStatusHistory(models.Model):
    """Model for recording equipment status history."""
    _name = 'maintenance.equipment.status.history'
    _description = 'Maintenance Equipment Status History'

    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment')
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
        ('scrapped', 'Scrapped')
    ], string='Status')
    change_date = fields.Datetime(string='Change Date')