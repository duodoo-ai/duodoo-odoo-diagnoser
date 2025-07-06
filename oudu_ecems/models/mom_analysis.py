from odoo import models, fields, api

class Mom(models.Model):
    _name = 'ecems.mom'
    _description = '环比分析模型'

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
    period_type = fields.Selection([
        ('daily', '日报'),
        ('monthly', '月报'),
        ('yearly', '年报')],
        string='周期类型',
        required=True
    )
    current_date = fields.Date(string='当前日期', required=True)
    current_usage = fields.Float(string='当前用量 (kW·h)', digits=(12, 2))
    previous_usage = fields.Float(string='前一次用量 (kW·h)', digits=(12, 2))
    increase_value = fields.Float(string='增加量 (kW·h)', digits=(12, 2), compute='_compute_increase_value', store=True)
    mom_rate = fields.Float(string='环比增长率 (%)', digits=(12, 2), compute='_compute_mom_rate', store=True)
    trend_arrow = fields.Binary(string='趋势箭头', compute='_compute_trend_arrow')
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)

    @api.depends('current_usage', 'previous_usage')
    def _compute_increase_value(self):
        for record in self:
            record.increase_value = record.current_usage - record.previous_usage

    @api.depends('increase_value', 'previous_usage')
    def _compute_mom_rate(self):
        for record in self:
            if record.previous_usage != 0:
                record.mom_rate = (record.increase_value / record.previous_usage) * 100
            else:
                record.mom_rate = 0.0

    @api.depends('mom_rate')
    def _compute_trend_arrow(self):
        for record in self:
            if record.mom_rate > 0:
                # 假设你有一个绿色向上箭头的图片路径
                record.trend_arrow = self.env.ref('ecems.up_arrow_image').datas
            elif record.mom_rate < 0:
                # 假设你有一个红色向下箭头的图片路径
                record.trend_arrow = self.env.ref('ecems.down_arrow_image').datas
            else:
                record.trend_arrow = False