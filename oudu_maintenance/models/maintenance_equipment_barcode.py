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
# from docx import Document

class MaintenanceEquipmentBarcode(models.Model):
    """Model for generating equipment barcodes."""
    _name = 'maintenance.equipment.barcode'
    _description = 'Equipment Barcode'
    _inherit = ['mail.thread']  # 继承 mail.thread 模型以支持邮件功能

    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', required=True,  tracking=True)
    owner_user_id = fields.Many2one('res.users',
                                    related='equipment_id.owner_user_id',
                                    string='Owner',
                                    tracking=True)
    category_id = fields.Many2one('maintenance.equipment.category',
                                  string='Equipment Category',
                                  related='equipment_id.category_id')
    partner_id = fields.Many2one('res.partner',
                                 string='Vendor',
                                 related='equipment_id.partner_id')
    partner_ref = fields.Char('Vendor Reference', related='equipment_id.partner_ref', )
    location = fields.Char('Location', related='equipment_id.location', )
    model = fields.Char('Model', related='equipment_id.model', )
    serial_no = fields.Char('Serial Number', related='equipment_id.serial_no', copy=False)
    qr_code = fields.Char(string='QR Code')
    qr_context = fields.Text(string='QR Context')
    printed = fields.Boolean(string='Printed', default=False)
    # 显式定义 display_name
    display_name = fields.Char(
        string='显示名称',
        compute='_compute_display_name',
        store=True
    )

    @api.depends('equipment_id.name', 'equipment_id.serial_no')
    def _compute_display_name(self):
        for record in self:
            if record.equipment_id.name and record.equipment_id.serial_no:
                record.display_name = f"{record.equipment_id.name} - {record.equipment_id.serial_no}"
            elif record.equipment_id.name:
                record.display_name = f"{record.equipment_id.name}"
            else:
                record.display_name = ''

    def generate_qr_code(self):
        """批量生成二维码（自动处理单/多设备）"""
        for record in self.filtered(lambda r: not r.qr_code):
            # 生成逻辑保持不变
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=6,
                border=1,
            )

            equipment = record.equipment_id
            if not equipment:
                raise UserError("Equipment ID is missing.")

            qr_data = f"Equipment Name: {equipment.name or ''}\n" \
                      f"Model: {equipment.model or ''}\n" \
                      f"Category: {equipment.category_id.name or ''}\n" \
                      f"Serial No: {equipment.serial_no or ''}\n" \
                      f"Location: {equipment.location or ''}\n" \
                      f"Assign Date: {equipment.assign_date or ''}\n" \
                      f"Owner: {equipment.owner_user_id.name or ''}"

            qr.add_data(qr_data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # 创建字节流并编码为 base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            qr_image = base64.b64encode(buffered.getvalue())

            # 确保保存为字符串
            record.write({
                'qr_code': qr_image.decode('utf-8'),  # 转换为字符串
                'qr_context': qr_data
            })
        return True

    inspection_ids = fields.One2many(
        'maintenance.equipment.inspection',
        'equipment_barcode_id',
        string='Inspections',
        help='关联的巡检记录'
    )

    def action_start_inspection(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.inspection.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_equipment_barcode_id': self.id}
        }

