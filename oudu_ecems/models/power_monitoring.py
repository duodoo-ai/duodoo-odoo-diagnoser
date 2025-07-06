from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import math

class PowerMonitoring(models.Model):
    _name = 'ecems.power_monitor'
    _description = '电力监控数据'
    _order = 'monitor_date desc'

    project_id = fields.Many2one(
        'project.project',
        string='项目',
        help='关联的项目'
    )
    # 树形结构字段
    circuit_id = fields.Many2one(
        'ecems.circuit.name',
        string='回路名称',
        required=True,
        ondelete='restrict',  # 防止误删
        index=True
    )
    circuit_name = fields.Char(related='circuit_id.name', string='回路详细名称', store=True)
    parent_path = fields.Char(index=True)
    monitor_date = fields.Date(
        string='监测日期',
        default=fields.Date.context_today,
        required=True
    )
    forward_active = fields.Float(
        string='正向有功电度(kWh)',
        digits=(12, 2),
        required=True
    )
    reverse_active = fields.Float(
        string='反向有功电度(kWh)',
        digits=(12, 2)
    )
    forward_reactive = fields.Float(
        string='正向无功电度(kvarh)',
        digits=(12, 2)
    )
    reverse_reactive = fields.Float(
        string='反向无功电度(kvarh)',
        digits=(12, 2)
    )
    avg_power_factor = fields.Float(
        string='平均功率因数',
        compute='_compute_power_factor',
        store=True,
        digits=(3, 2)
    )
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)

    @api.depends(
        'forward_active',
        'reverse_active',
        'forward_reactive',
        'reverse_reactive'
    )
    def _compute_power_factor(self):
        for record in self:
            try:
                # 计算总有功功率
                total_active = record.forward_active - record.reverse_active
                # 计算总无功功率
                total_reactive = record.forward_reactive - record.reverse_reactive
                # 计算视在功率
                apparent_power = math.sqrt(
                    total_active**2 + total_reactive**2
                )
                if apparent_power != 0:
                    record.avg_power_factor = abs(total_active) / apparent_power
                else:
                    record.avg_power_factor = 0.0
            except Exception as e:
                raise ValidationError(
                    _('功率因数计算错误: %s') % str(e)
                )

    _sql_constraints = [
        ('unique_circuit_date', 'unique(circuit_name, monitor_date)',
         '同一回路同一天只能有一条记录！')
    ]

    # 显式定义 display_name
    display_name = fields.Char(
        string='显示名称',
        compute='_compute_display_name',
        store=True
    )

    @api.depends('circuit_id', 'monitor_date')
    def _compute_display_name(self):
        for record in self:
            if record.circuit_id and record.monitor_date:
                record.display_name = f"{record.circuit_id.name} - {fields.Datetime.to_string(record.monitor_date)}"
            else:
                record.display_name = ''