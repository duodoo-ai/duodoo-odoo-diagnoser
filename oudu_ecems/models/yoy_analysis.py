
from odoo import models, fields, api


class YoyAnalysis(models.Model):
    _name = 'ecems.yoy'
    _description = '同比分析'

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
    analysis_month = fields.Selection([
        ('1', '一月'),
        ('2', '二月'),
        ('3', '三月'),
        ('4', '四月'),
        ('5', '五月'),
        ('6', '六月'),
        ('7', '七月'),
        ('8', '八月'),
        ('9', '九月'),
        ('10`', '十月'),
        ('11', '十一月'),
        ('12', '十二月')],
        string='分析月份')

    current_year = fields.Integer('当前年度', default=lambda self: fields.Date.today().year)
    current_value = fields.Float('本期用量')
    compare_value = fields.Float('同期用量')
    yoy_rate = fields.Float('同比率(%)', compute='_compute_rate')
    trend_values = fields.Json('趋势值', compute='_compute_trend_values')
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)

    @api.depends('current_value', 'compare_value')
    def _compute_rate(self):
        for rec in self:
            if rec.compare_value != 0:
                rec.yoy_rate = ((rec.current_value - rec.compare_value) / rec.compare_value) * 100
            else:
                rec.yoy_rate = 0.0

    @api.depends('current_value', 'compare_value')
    def _compute_trend_values(self):
        for rec in self:
            rec.trend_values = [rec.current_value, rec.compare_value]

    @api.depends('current_value', 'compare_value')
    def _compute_trend_values(self):
        for rec in self:
            rec.trend_values = [rec.current_value, rec.compare_value]