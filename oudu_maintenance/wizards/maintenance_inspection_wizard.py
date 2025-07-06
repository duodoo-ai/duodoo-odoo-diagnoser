from odoo import fields, models, api

class MaintenanceInspectionWizard(models.TransientModel):
    _name = 'maintenance.inspection.wizard'
    _description = 'Equipment Inspection Wizard'

    equipment_barcode_id = fields.Many2one(
        'maintenance.equipment.barcode',
        string='QR Code',
        help='Scan or select device QR code'     # 扫描或选择设备二维码
    )
    equipment_id = fields.Many2one(
        'maintenance.equipment',
        related='equipment_barcode_id.equipment_id',
        string='Equipment',
        readonly=True
    )
    inspection_result = fields.Selection(
        [('pass', 'Pass'), ('fail', 'Fail')],
        string='Result'
    )
    notes = fields.Text('Notes')
    photo = fields.Binary('Photo')

    @api.model
    def default_get(self, fields):
        """ 添加上下文自动获取设备二维码 """
        res = super().default_get(fields)
        # 从上下文获取当前设备二维码记录
        if self.env.context.get('active_model') == 'maintenance.equipment.barcode':
            res['equipment_barcode_id'] = self.env.context.get('active_id')
        return res

    def action_create_inspection(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.equipment.inspection',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_equipment_id': self.equipment_id.id,
                'default_inspector_id': self.env.uid,
                'default_result': self.inspection_result,
                'default_notes': self.notes,
                'default_photo': self.photo,
                'default_equipment_barcode_id': self.equipment_barcode_id.id
            }
        }

    def scan_barcode(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'action_scan_barcode',  # 与XML中的tag字段保持一致
            'name': 'Device scan code',  # 设备扫码
        }


# 实现效果：
#
# 向导界面显示"扫码巡检"按钮
# 点击按钮启动设备扫码
# 扫描成功自动填充设备信息
# 支持序列号和设备名称两种扫码方式
# 错误时显示提示信息