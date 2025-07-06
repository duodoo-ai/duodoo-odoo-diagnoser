from odoo import models, fields, api

class CircuitName(models.Model):
    _name = 'ecems.circuit.name'
    _description = '回路主数据'
    _rec_name = 'code'  # 显示名称字段

    code = fields.Char('回路编码', required=True, index=True)
    name = fields.Char('回路名称', required=True)
    voltage_level = fields.Selection([
        ('low', '低压'),
        ('medium', '中压'),
        ('high', '高压')], string='电压等级', default='low')
    identification = fields.Selection([
        ('P', '电源回路'),
        ('C', '控制回路'),
        ('L', '照明回路'),
        ('D', '动力回路'),
        ('S', '信号回路')
    ], string='类型标识', default='P', help='一般组成：类型标识-区域标识-序号')
    location = fields.Char('安装位置')
    parent_id = fields.Many2one('ecems.circuit.name', string='上级回路')
    child_ids = fields.One2many('ecems.circuit.name', 'parent_id', string='子回路')
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)

    _sql_constraints = [
        ('code_uniq', 'unique (code)', '回路编码必须唯一!')
    ]

    # 显式定义 display_name
    display_name = fields.Char(
        string='显示名称',
        compute='_compute_display_name',
        store=True
    )

    @api.depends('code', 'name')
    def _compute_display_name(self):
        for record in self:
            if record.code and record.name:
                record.display_name = f"{record.code} - {record.name}"
            else:
                record.display_name = ''