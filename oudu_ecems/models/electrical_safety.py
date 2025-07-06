# models/electrical_safety.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class ElectricalSafety(models.Model):
    _name = 'ecems.electrical_safety'
    _description = '电气安全监测'
    _order = 'collection_time desc'

    project_id = fields.Many2one(
        'project.project',
        string='项目',
        help='关联的项目'
    )
    # 基础字段
    circuit_id = fields.Many2one(
        'ecems.circuit.name',
        string='监测点名称',
        required=True,
        ondelete='restrict',  # 防止误删
        index=True
    )
    collection_time = fields.Datetime(
        string='采集时间',
        default=lambda self: fields.Datetime.now(),
        required=True
    )

    # 温度参数
    temperature_a = fields.Float(
        string='A相温度(℃)',
        digits=(3, 1),
        help="A相线缆接点温度"
    )
    temperature_b = fields.Float(
        string='B相温度(℃)',
        digits=(3, 1)
    )
    temperature_c = fields.Float(
        string='C相温度(℃)',
        digits=(3, 1)
    )
    temperature_n = fields.Float(
        string='N相温度(℃)',
        digits=(3, 1)
    )

    # 状态标记
    is_overheat = fields.Boolean(
        string='超温报警',
        compute='_compute_temperature_status',
        store=True
    )
    max_temperature = fields.Float(
        string='最高温度(℃)',
        compute='_compute_max_temperature',
        store=True,
        digits=(3, 1)
    )

    # 历史数据关联
    history_ids = fields.One2many(
        'ecems.electrical_safety.history',
        'safety_id',
        string='历史温度记录'
    )

    # 阈值配置
    temperature_threshold = fields.Float(
        string='温度阈值(℃)',
        default=70.0,
        help="温度报警临界值"
    )

    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)

    @api.depends('temperature_a', 'temperature_b', 'temperature_c', 'temperature_n')
    def _compute_max_temperature(self):
        for record in self:
            temps = [
                record.temperature_a,
                record.temperature_b,
                record.temperature_c,
                record.temperature_n
            ]
            record.max_temperature = max(temps) if temps else 0.0

    @api.depends('max_temperature', 'temperature_threshold')
    def _compute_temperature_status(self):
        for record in self:
            record.is_overheat = record.max_temperature > record.temperature_threshold

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

    # 历史数据查看动作
    def action_view_history(self):
        self.ensure_one()
        return {
            'name': _('历史温度数据'),
            'type': 'ir.actions.act_window',
            'res_model': 'ecems.electrical_safety.history',
            'view_mode': 'list,form',
            'domain': [('safety_id.circuit_id', '=', self.circuit_id.id)],
            'context': {
                'default_safety_id': self.id,
                'search_default_group_by_point': True
            }
        }

    def check_and_send_alert(self):
        for record in self:
            if not record.project_id:
                _logger.warning("Electrical safety record %s has no associated project. Skipping alert.", record.id)
                continue
            if record._has_exception():
                todo_model = self.env['project.task']
                alert_message = _(
                    "监测点 名称: %(circuit_code)s + %(circuit_name)s，电气安全监测检测到超温异常，记录 ID: %(record_id)s，最高温度: %(max_temp).1f℃，阈值: %(threshold).1f℃",
                    circuit_code=record.circuit_id.code,
                    circuit_name=record.circuit_id.name,
                    record_id=record.id,
                    max_temp=record.max_temperature,
                    threshold=record.temperature_threshold
                )
                try:
                    # 指定受指派人，这里以当前用户为例，可按需修改
                    assignee = self.env.user
                    todo_model.create({
                        # 对于适用于个人任务告警，不建议指定项目，直接到待办事项中查看（待办事项与我的任务数据是一致的）
                        # 'project_id': record.project_id.id,
                        'name': _("电气安全超温告警"),
                        'description': alert_message,
                        # 使用多对多字段正确的赋值格式
                        'user_ids': [(6, 0, [assignee.id])],
                    })
                    _logger.info("Alert created for electrical safety record %s in project %s", record.id,
                                 record.project_id.id)
                except Exception as e:
                    _logger.error("Failed to create alert for electrical safety record %s. Error: %s", record.id,
                                  str(e))

    def _has_exception(self):
        return self.is_overheat

    def save_to_history(self):
        """
        将当前记录的数据保存到历史记录模型中
        """
        history_model = self.env['ecems.electrical_safety.history']
        for record in self:
            history_model.create({
                'safety_id': record.id,
                'project_id': record.project_id.id,
                'collection_time': record.collection_time,
                'temperature_a': record.temperature_a,
                'temperature_b': record.temperature_b,
                'temperature_c': record.temperature_c,
                'temperature_n': record.temperature_n,
                'temperature_threshold': record.temperature_threshold,
                'max_temperature': record.max_temperature,
                'company_id': record.company_id.id
            })

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.save_to_history()
        records.check_and_send_alert()
        return records

    def write(self, vals):
        res = super().write(vals)
        self.save_to_history()
        self.check_and_send_alert()
        return res


class ElectricalSafetyHistory(models.Model):
    _name = 'ecems.electrical_safety.history'
    _description = '历史温度记录'
    _order = 'collection_time desc'

    safety_id = fields.Many2one(
        'ecems.electrical_safety',
        string='主记录',
        ondelete='cascade'
    )
    project_id = fields.Many2one(
        'project.project',
        string='项目',
        help='关联的项目'
    )
    circuit_id = fields.Many2one(
        related='safety_id.circuit_id',
        comodel_name='ecems.circuit.name',
        string='监测点名称',
        store=True,
        index=True
    )
    collection_time = fields.Datetime(
        string='采集时间',
        required=True
    )
    temperature_a = fields.Float(
        string='A相温度(℃)',
        digits=(3, 1)
    )
    temperature_b = fields.Float(
        string='B相温度(℃)',
        digits=(3, 1)
    )
    temperature_c = fields.Float(
        string='C相温度(℃)',
        digits=(3, 1)
    )
    temperature_n = fields.Float(
        string='N相温度(℃)',
        digits=(3, 1)
    )
    temperature_threshold = fields.Float(
        related='safety_id.temperature_threshold',
        string='温度阈值(℃)',
        store=True
    )
    is_overheat = fields.Boolean(
        string='超温报警',
        compute='_compute_overheat_status',
        store=True
    )
    max_temperature = fields.Float(
        string='最高温度(℃)',
        digits=(3, 1)
    )
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)

    @api.depends('temperature_a', 'temperature_b', 'temperature_c', 'temperature_n', 'temperature_threshold')
    def _compute_overheat_status(self):
        for record in self:
            max_temp = max([
                record.temperature_a,
                record.temperature_b,
                record.temperature_c,
                record.temperature_n
            ])
            record.is_overheat = max_temp > record.temperature_threshold
