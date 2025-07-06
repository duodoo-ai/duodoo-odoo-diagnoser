import logging
from odoo import models, fields, api
_logger = logging.getLogger(__name__)


class CircuitEnergy(models.Model):
    _name = 'ecems.circuit'
    _description = '支路能耗统计'
    _order = 'record_time desc'

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
    record_type = fields.Selection([
        ('daily', '日报'),
        ('monthly', '月报'),
        ('yearly', '年报')],
        string='报表类型',
        required=True
    )
    start_time = fields.Datetime(
        string='开始时间',
        required=True
    )
    end_time = fields.Datetime(
        string='结束时间',
        required=True
    )
    record_time = fields.Datetime(
        string='记录时间',
        default=lambda self: fields.Datetime.now(),
        required=True
    )
    total_energy = fields.Float(
        string='总能耗 (kW·h)',
        digits=(12, 2),
        compute='_compute_total_energy',
        store=True
    )
    total_cost = fields.Float(
        string='总费用',
        digits=(12, 2)
    )
    hourly_data_ids = fields.One2many(
        comodel_name='ecems.hourly.data',
        inverse_name='circuit_id',
        string='每小时数据'
    )
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)

    @api.depends('hourly_data_ids.energy_data')
    def _compute_total_energy(self):
        for record in self:
            record.total_energy = sum(record.hourly_data_ids.mapped('energy_data'))

    def check_and_send_alert(self):
        for record in self:
            if not record.project_id:
                _logger.warning("Circuit record %s has no associated project. Skipping alert.", record.id)
                continue
            if record._has_exception():
                todo_model = self.env['project.task']
                alert_message = f"支路能耗统计模块检测到异常，记录 ID: {record.id}"
                try:
                    # 指定受指派人，这里以当前用户为例，可按需修改
                    assignee = self.env.user
                    todo_model.create({
                        # 对于适用于个人任务告警，不建议指定项目，直接到待办事项中查看（待办事项与我的任务数据是一致的）
                        # 'project_id': record.project_id.id,
                        'name': "Tekr Ecems 异常告警",
                        'description': alert_message,
                        # 使用多对多字段正确的赋值格式
                        'user_ids': [(6, 0, [assignee.id])],
                    })
                    _logger.info("Alert created for circuit record %s in project %s", record.id, record.project_id.id)
                except Exception as e:
                    _logger.error("Failed to create alert for circuit record %s. Error: %s", record.id, str(e))

    def _has_exception(self):
        # 异常检测逻辑
        # 1. 总能耗超过 10000 kW·h
        if self.total_energy > 10000:
            return True
        # 2. 总费用为负数
        if self.total_cost < 0:
            return True
        # 3. 每小时数据缺失
        if not self.hourly_data_ids:
            return True
        return False


class HourlyData(models.Model):
    _name = 'ecems.hourly.data'
    _description = 'Hourly Energy Data'

    circuit_id = fields.Many2one(
        comodel_name='ecems.circuit',
        string='Circuit',
        ondelete='cascade',
        required=True,
        index=True
    )
    hour = fields.Integer(
        string='Hour',
        required=True
    )
    energy_data = fields.Float(
        string='Energy Data (kW·h)',
        digits=(12, 2)
    )
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)

    def check_and_send_alert(self):
        for record in self:
            circuit = record.circuit_id
            if not circuit.project_id:
                _logger.warning("Hourly data record %s has no associated project. Skipping alert.", record.id)
                continue
            if record._has_exception():
                todo_model = self.env['project.task']
                alert_message = f"Tekr Ecems 模块的小时数据检测到异常，记录 ID: {record.id}"
                try:
                    todo_model.create({
                        'project_id': circuit.project_id.id,
                        'name': "Tekr Ecems 小时数据异常告警",
                        'description': alert_message,
                    })
                    _logger.info("Alert created for hourly data record %s in project %s", record.id,
                                 circuit.project_id.id)
                except Exception as e:
                    _logger.error("Failed to create alert for hourly data record %s. Error: %s", record.id, str(e))

    def _has_exception(self):
        # 异常检测逻辑
        # 1. 能耗数据为负数
        if self.energy_data < 0:
            return True
        # 2. 小时数不在 0 - 23 范围内
        if self.hour < 0 or self.hour > 23:
            return True
        return False

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.check_and_send_alert()
        return records

    def write(self, vals):
        res = super().write(vals)
        self.check_and_send_alert()
        return res