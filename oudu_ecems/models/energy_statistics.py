from odoo import models, fields, api, _
import json
from datetime import datetime, timedelta

class ElectricityCollection(models.Model):
    _name = 'ecems.collection'
    _description = '用电集抄管理'
    _order = 'record_date desc'

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
    record_date = fields.Date(
        string='记录日期',
        default=fields.Date.context_today,
        required=True
    )
    base_reading = fields.Float(
        string='0点示数(kW·h)',
        digits=(12, 2),
        required=True
    )
    hourly_readings = fields.Text(
        string='小时示数存储',
        help="JSON格式存储24小时数据"
    )
    total_consumption = fields.Float(
        string='用电量(kW·h)',
        compute='_compute_total',
        store=True,
        digits=(12, 2)
    )
    # JSON格式处理
    hourly_data = fields.Json(
        string='小时数据',
        compute='_compute_hourly_data',
        inverse='_inverse_hourly_data',
        help="结构：[{'hour':0-23, 'value':读数}]"
    )
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)

    # 显式定义 display_name
    display_name = fields.Char(
        string='显示名称',
        compute='_compute_display_name',
        store=True
    )

    @api.depends('circuit_id.code', 'circuit_id.name')
    def _compute_display_name(self):
        for record in self:
            if record.circuit_id.code and record.circuit_id.name:
                record.display_name = f"{record.circuit_id.code} - {record.circuit_id.name}"
            else:
                record.display_name = ''

    @api.depends('hourly_readings')
    def _compute_hourly_data(self):
        for record in self:
            try:
                record.hourly_data = json.loads(record.hourly_readings or '[]')
            except json.JSONDecodeError:
                record.hourly_data = []

    def _inverse_hourly_data(self):
        for record in self:
            record.hourly_readings = json.dumps(record.hourly_data)

    @api.depends('base_reading', 'hourly_data')
    def _compute_total(self):
        for record in self:
            if record.hourly_data:
                last_value = max((item['value'] for item in record.hourly_data),
                              default=record.base_reading)
                record.total_consumption = last_value - record.base_reading
            else:
                record.total_consumption = 0.0

    _sql_constraints = [
        ('unique_circuit_date', 'unique(circuit_name, record_date)',
         '同一回路同一天只能有一条记录！')
    ]


class ElectricityStatistics(models.Model):
    _name = 'ecems.statistics'
    _description = '用电统计分析'
    _order = 'start_date desc'

    project_id = fields.Many2one(
        'project.project',
        string='项目',
        help='关联的项目'
    )
    circuit_id = fields.Many2one(
        'ecems.circuit.name',
        string='回路名称',
        required=True,
        ondelete='restrict',  # 防止误删
        index=True
    )
    report_type = fields.Selection([
        ('daily', '日报'),
        ('monthly', '月报'),
        ('yearly', '年报')],
        string='报表类型',
        required=True
    )
    start_date = fields.Date(
        string='开始日期',
        required=True
    )
    end_date = fields.Date(
        string='结束日期',
        compute='_compute_end_date',
        store=True
    )
    base_reading = fields.Float(
        string='初始示数(kW·h)',
        digits=(12, 2)
    )
    total_reading = fields.Float(
        string='累计示数(kW·h)',
        digits=(12, 2)
    )
    hourly_data = fields.Json(
        string='时段数据'
    )
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)

    # 显式定义 display_name
    display_name = fields.Char(
        string='显示名称',
        compute='_compute_display_name',
        store=True
    )

    @api.depends('circuit_id.code', 'circuit_id.name')
    def _compute_display_name(self):
        for record in self:
            if record.circuit_id.code and record.circuit_id.name:
                record.display_name = f"{record.circuit_id.code} - {record.circuit_id.name}"
            else:
                record.display_name = ''

    @api.depends('start_date', 'report_type')
    def _compute_end_date(self):
        for record in self:
            if not record.start_date:
                record.end_date = False
                continue
            if record.report_type == 'daily':
                record.end_date = record.start_date
            elif record.report_type == 'monthly':
                next_month = record.start_date.replace(day=28) + timedelta(days=4)
                record.end_date = next_month - timedelta(days=next_month.day)
            else:
                record.end_date = record.start_date.replace(month=12, day=31)

class TimeSlotConsumption(models.Model):
    _name = 'ecems.timeslot'
    _description = '分时段用电统计'

    project_id = fields.Many2one(
        'project.project',
        string='项目',
        help='关联的项目'
    )
    parent_path = fields.Char(index=True)
    circuit_id = fields.Many2one(
        'ecems.circuit.name',
        string='回路名称',
        required=True,
        ondelete='restrict',  # 防止误删
        index=True
    )
    record_date = fields.Date(
        string='记录日期',
        required=True
    )

    # 尖时段
    peak_energy = fields.Float(
        string='尖电量(kW·h)',
        digits=(12, 2)
    )
    peak_price = fields.Float(
        string='尖单价',
        digits=(6, 4)
    )
    peak_amount = fields.Float(
        string='尖金额',
        compute='_compute_peak_amount',
        store=True,
        digits=(12, 2)
    )

    # 峰时段
    high_energy = fields.Float(
        string='峰电量(kW·h)',
        digits=(12, 2)
    )
    high_price = fields.Float(
        string='峰单价',
        digits=(6, 4)
    )
    high_amount = fields.Float(
        string='峰金额',
        compute='_compute_high_amount',
        store=True,
        digits=(12, 2)
    )

    # 平时段
    normal_energy = fields.Float(
        string='平电量(kW·h)',
        digits=(12, 2)
    )
    normal_price = fields.Float(
        string='平单价',
        digits=(6, 4)
    )
    normal_amount = fields.Float(
        string='平金额',
        compute='_compute_normal_amount',
        store=True,
        digits=(12, 2)
    )

    # 谷时段
    valley_energy = fields.Float(
        string='谷电量(kW·h)',
        digits=(12, 2)
    )
    valley_price = fields.Float(
        string='谷单价',
        digits=(6, 4)
    )
    valley_amount = fields.Float(
        string='谷金额',
        compute='_compute_valley_amount',
        store=True,
        digits=(12, 2)
    )

    # 合计字段
    total_energy = fields.Float(
        string='总电量(kW·h)',
        compute='_compute_total',
        store=True,
        digits=(12, 2)
    )
    total_amount = fields.Float(
        string='总金额',
        compute='_compute_total',
        store=True,
        digits=(12, 2)
    )
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)

    # 显式定义 display_name
    display_name = fields.Char(
        string='显示名称',
        compute='_compute_display_name',
        store=True
    )

    @api.depends('circuit_id.code', 'circuit_id.name')
    def _compute_display_name(self):
        for record in self:
            if record.circuit_id.code and record.circuit_id.name:
                record.display_name = f"{record.circuit_id.code} - {record.circuit_id.name}"
            else:
                record.display_name = ''

    @api.depends('peak_energy', 'peak_price')
    def _compute_peak_amount(self):
        for r in self:
            r.peak_amount = r.peak_energy * r.peak_price

    @api.depends('high_energy', 'high_price')
    def _compute_high_amount(self):
        for r in self:
            r.high_amount = r.high_energy * r.high_price

    @api.depends('normal_energy', 'normal_price')
    def _compute_normal_amount(self):
        for r in self:
            r.normal_amount = r.normal_energy * r.normal_price

    @api.depends('valley_energy', 'valley_price')
    def _compute_valley_amount(self):
        for r in self:
            r.valley_amount = r.valley_energy * r.valley_price

    @api.depends(
        'peak_energy', 'high_energy', 'normal_energy', 'valley_energy',
        'peak_amount', 'high_amount', 'normal_amount', 'valley_amount'
    )
    def _compute_total(self):
        for r in self:
            r.total_energy = sum([
                r.peak_energy,
                r.high_energy,
                r.normal_energy,
                r.valley_energy
            ])
            r.total_amount = sum([
                r.peak_amount,
                r.high_amount,
                r.normal_amount,
                r.valley_amount
            ])

class LineLossAnalysis(models.Model):
    _name = 'ecems.lineloss'
    _description = '线路损耗分析'

    project_id = fields.Many2one(
        'project.project',
        string='项目',
        help='关联的项目'
    )
    parent_path = fields.Char(index=True)
    parent_id = fields.Many2one(
        'ecems.lineloss',
        string='上级支路',
        index=True,
        ondelete='cascade'
    )
    child_ids = fields.One2many(
        'ecems.lineloss',
        'parent_id',
        string='下级支路'
    )

    circuit_id = fields.Many2one(
        'ecems.circuit.name',
        string='回路名称',
        required=True,
        ondelete='restrict',  # 防止误删
        index=True
    )
    record_date = fields.Date(
        string='记录日期',
        default=fields.Date.context_today,
        required=True
    )
    current_energy = fields.Float(
        string='当前能耗(kW·h)',
        digits=(12, 2)
    )
    child_energy = fields.Float(
        string='下级合计(kW·h)',
        compute='_compute_child_energy',
        store=True,
        digits=(12, 2)
    )
    energy_diff = fields.Float(
        string='能耗差值(kW·h)',
        compute='_compute_diff',
        store=True,
        digits=(12, 2)
    )
    diff_percent = fields.Float(
        string='差值百分比(%)',
        compute='_compute_diff',
        store=True,
        digits=(5, 2)
    )
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)

    # 显式定义 display_name
    display_name = fields.Char(
        string='显示名称',
        compute='_compute_display_name',
        store=True
    )

    @api.depends('circuit_id.code', 'circuit_id.name')
    def _compute_display_name(self):
        for record in self:
            if record.circuit_id.code and record.circuit_id.name:
                record.display_name = f"{record.circuit_id.code} - {record.circuit_id.name}"
            else:
                record.display_name = ''

    @api.depends('child_ids.current_energy')
    def _compute_child_energy(self):
        for record in self:
            record.child_energy = sum(
                child.current_energy for child in record.child_ids
            )

    @api.depends('current_energy', 'child_energy')
    def _compute_diff(self):
        for record in self:
            total = record.current_energy + record.child_energy
            record.energy_diff = record.current_energy - record.child_energy
            record.diff_percent = (record.energy_diff / total * 100) if total != 0 else 0.0

    def name_get(self):
        return [(rec.id, f"{rec.circuit_id} [{rec.record_date}]") for rec in self]
