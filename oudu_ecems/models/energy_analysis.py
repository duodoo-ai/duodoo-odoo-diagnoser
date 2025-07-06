from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class EnergyAnalysis(models.Model):
    _name = 'ecems.energy_analysis'
    _description = 'Energy Analysis'

    project_id = fields.Many2one(
        'project.project',
        string='项目',
        help='关联的项目'
    )
    # 看板所需字段
    current_month_usage = fields.Float('当月用电量')
    last_month_usage = fields.Float('上月用电量')
    year_total_usage = fields.Float('年度累计')
    hourly_trend_data = fields.Json('趋势数据', default={
        "00:00": {"energy": 0.0, "cost": 0.0},
        "01:00": {"energy": 0.0, "cost": 0.0},
        "02:00": {"energy": 0.0, "cost": 0.0},
        "03:00": {"energy": 0.0, "cost": 0.0},
        "04:00": {"energy": 0.0, "cost": 0.0},
        "05:00": {"energy": 0.0, "cost": 0.0},
        "06:00": {"energy": 0.0, "cost": 0.0},
        "07:00": {"energy": 0.0, "cost": 0.0},
        "08:00": {"energy": 0.0, "cost": 0.0},
        "09:00": {"energy": 0.0, "cost": 0.0},
        "10:00": {"energy": 0.0, "cost": 0.0},
        "11:00": {"energy": 0.0, "cost": 0.0},
        "12:00": {"energy": 0.0, "cost": 0.0},
        "13:00": {"energy": 0.0, "cost": 0.0},
        "14:00": {"energy": 0.0, "cost": 0.0},
        "15:00": {"energy": 0.0, "cost": 0.0},
        "16:00": {"energy": 0.0, "cost": 0.0},
        "17:00": {"energy": 0.0, "cost": 0.0},
        "18:00": {"energy": 0.0, "cost": 0.0},
        "19:00": {"energy": 0.0, "cost": 0.0},
        "20:00": {"energy": 0.0, "cost": 0.0},
        "21:00": {"energy": 0.0, "cost": 0.0},
        "22:00": {"energy": 0.0, "cost": 0.0},
        "23:00": {"energy": 0.0, "cost": 0.0},
        # ...其他小时数据
    })
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)

    # 看板视图动作
    def action_refresh_dashboard(self):
        # 更新看板数据的逻辑
        pass

# 同比分析模型
class YearCompare(models.Model):
    _name = 'ecems.year_compare'
    _description = 'Year-on-Year Analysis'

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
        ('12', '十二月')
    ], string='月份')
    current_period = fields.Float('本期用量')
    same_period = fields.Float('同期用量')
    compare_rate = fields.Float('同比率', compute='_compute_compare_rate')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)

    @api.depends('current_period', 'same_period')
    def _compute_compare_rate(self):
        for record in self:
            if record.same_period != 0:
                record.compare_rate = ((record.current_period - record.same_period) / record.same_period) * 100
            else:
                record.compare_rate = 0.0

    # 添加导出动作
    def action_export(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/ecems/export/year_compare',
            'target': 'new'
        }

    def check_and_send_alert(self):
        for record in self:
            if not record.project_id:
                _logger.warning("Year compare record %s has no associated project. Skipping alert.", record.id)
                continue
            if record._has_exception():
                todo_model = self.env['project.task']
                alert_message = _(
                    "同比分析检测到异常，记录 ID: %(record_id)s，同比率: %(compare_rate).2f%%",
                    record_id=record.id,
                    compare_rate=record.compare_rate
                )
                try:
                    # 指定受指派人，这里以当前用户为例，可按需修改
                    assignee = self.env.user
                    todo_model.create({
                        # 对于适用于个人任务告警，不建议指定项目，直接到待办事项中查看（待办事项与我的任务数据是一致的）
                        # 'project_id': record.project_id.id,
                        'name': _("同比分析异常告警"),
                        'description': alert_message,
                        # 使用多对多字段正确的赋值格式
                        'user_ids': [(6, 0, [assignee.id])],
                    })
                    _logger.info("Alert created for year compare record %s in project %s", record.id,
                                 record.project_id.id)
                except Exception as e:
                    _logger.error("Failed to create alert for year compare record %s. Error: %s", record.id, str(e))

    def _has_exception(self):
        # 假设同比率超过 50% 或低于 -50% 为异常
        return abs(self.compare_rate) > 50

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.check_and_send_alert()
        return records

    def write(self, vals):
        res = super().write(vals)
        self.check_and_send_alert()
        return res


# 环比分析模型
class ChainCompare(models.Model):
    _name = 'ecems.chain_compare'
    _description = 'Chain Analysis'

    project_id = fields.Many2one(
        'project.project',
        string='项目',
        help='关联的项目'
    )
    circuit_name = fields.Char('回路名称')
    analysis_type = fields.Selection([
        ('day', '日'),
        ('week', '周'),
        ('month', '月')], string='分析周期')
    current_usage = fields.Float('当期用量')
    previous_usage = fields.Float('上期用量')
    increase_value = fields.Float('增长值', compute='_compute_increase')
    chain_rate = fields.Float('环比率', compute='_compute_chain_rate')
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)

    @api.depends('current_usage', 'previous_usage')
    def _compute_increase(self):
        for record in self:
            record.increase_value = record.current_usage - record.previous_usage

    @api.depends('current_usage', 'previous_usage')
    def _compute_chain_rate(self):
        for record in self:
            if record.previous_usage != 0:
                record.chain_rate = ((record.current_usage - record.previous_usage) / record.previous_usage) * 100
            else:
                record.chain_rate = 0.0

    def check_and_send_alert(self):
        for record in self:
            if not record.project_id:
                _logger.warning("Chain compare record %s has no associated project. Skipping alert.", record.id)
                continue
            if record._has_exception():
                todo_model = self.env['project.task']
                alert_message = _(
                    "环比分析检测到异常，记录 ID: %(record_id)s，环比率: %(chain_rate).2f%%",
                    record_id=record.id,
                    chain_rate=record.chain_rate
                )
                try:
                    # 指定受指派人，这里以当前用户为例，可按需修改
                    assignee = self.env.user
                    todo_model.create({
                        # 对于适用于个人任务告警，不建议指定项目，直接到待办事项中查看（待办事项与我的任务数据是一致的）
                        # 'project_id': record.project_id.id,
                        'name': _("环比分析异常告警"),
                        'description': alert_message,
                        # 使用多对多字段正确的赋值格式
                        'user_ids': [(6, 0, [assignee.id])],
                    })
                    _logger.info("Alert created for chain compare record %s in project %s", record.id,
                                 record.project_id.id)
                except Exception as e:
                    _logger.error("Failed to create alert for chain compare record %s. Error: %s", record.id, str(e))

    def _has_exception(self):
        # 假设环比率超过 50% 或低于 -50% 为异常
        return abs(self.chain_rate) > 50

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.check_and_send_alert()
        return records

    def write(self, vals):
        res = super().write(vals)
        self.check_and_send_alert()
        return res
