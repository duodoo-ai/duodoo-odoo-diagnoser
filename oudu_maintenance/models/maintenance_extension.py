from odoo import models, fields, api, _
from datetime import datetime, timedelta
import logging, time
import base64
from io import BytesIO
import qrcode

# 获取日志记录器
_logger = logging.getLogger(__name__)


class MaintenanceEquipmentExtension(models.Model):
    """设备模型扩展，继承自 Odoo 标准维护设备模型。"""
    _inherit = 'maintenance.equipment'

    # 设备分类字段，定义不同类型的设备
    equipment_category = fields.Selection([
        ('control', 'Control'),  # 控制类
        ('motor', 'Motor'),  # 电机类
        ('sensor', 'Sensor'),  # 传感类
        ('relay', 'Relay'),  # 继电类
        ('electronic', 'Electronic'),  # 电子类
        ('protocol', 'Protocol'),  # 协议类
        ('serial', 'Serial'),  # 串口类
        ('other', 'Other')  # 其他类
    ], string='Equipment Category',  # 字段显示名称
        help="Category of equipment")  # 字段帮助信息 - 设备分类

    # 设备状态字段，跟踪设备当前运行状态
    status = fields.Selection([
        ('active', 'Active'),  # 活跃 - 设备正常运行
        ('inactive', 'Inactive'),  # 停用 - 设备暂时停用
        ('maintenance', 'Under Maintenance'),  # 维护中 - 设备正在维修
        ('scrapped', 'Scrapped')  # 报废 - 设备已报废
    ], string='Status',  # 字段显示名称
        default='active',  # 默认值：活跃
        help='Current status of the equipment.')  # 字段帮助信息 - 设备的当前状态

    # 二维码字段，用于存储设备的二维码图像
    qr_code = fields.Binary(string='QR Code',  # 字段显示名称
                            attachment=True,  # 作为附件存储
                            help="QR code for equipment identification")  # 字段帮助信息 - 用于设备识别的二维码

    # 二维码生成状态字段，标记二维码是否已生成
    qr_code_generated = fields.Boolean(string='QR Generated',  # 字段显示名称
                                       default=False,  # 默认未生成
                                       help="Indicates if QR code is generated")  # 字段帮助信息 - 指示二维码是否已生成

    # 设备技术数据字段，存储设备的技术规格信息
    technical_data = fields.Text(string='Technical Data',  # 字段显示名称
                                 help="Technical specifications of equipment")  # 字段帮助信息 - 设备技术规格

    # 驱动类型字段，记录设备的驱动机构类型
    drive_type = fields.Char(string='Drive Type',  # 字段显示名称
                             help="Type of drive mechanism")  # 字段帮助信息 - 驱动机构类型

    # 电机功率字段，记录设备电机的额定功率
    motor_power = fields.Float(string='Motor Power (kW)',  # 字段显示名称
                               help="Power rating of motor")  # 字段帮助信息 - 电机额定功率

    # 额定转速字段，记录设备的额定运行速度
    rated_speed = fields.Integer(string='Rated Speed (RPM)',  # 字段显示名称
                                 help="Nominal operating speed")  # 字段帮助信息 - 额定运行速度

    # 轴承类型字段，记录设备使用的轴承类型
    bearing_type = fields.Char(string='Bearing Type',  # 字段显示名称
                               help="Type of bearings used")  # 字段帮助信息 - 使用的轴承类型

    # 预期寿命字段，记录设备的预期使用寿命
    expected_life = fields.Integer(string='Expected Life (years)',  # 字段显示名称
                                   help="Expected service life")  # 字段帮助信息 - 预期使用寿命

    # 润滑周期字段，记录设备的润滑间隔周期
    lubrication_period = fields.Integer(string='Lubrication Period (days)',  # 字段显示名称
                                        help="Interval between lubrication")  # 字段帮助信息 - 润滑间隔周期

    # 联轴器类型字段，记录设备轴联轴器的类型
    coupling_type = fields.Char(string='Coupling Type',  # 字段显示名称
                                help="Type of shaft coupling")  # 字段帮助信息 - 轴联轴器类型

    # 电气参数字段，记录设备的电气特性信息
    electrical_params = fields.Text(string='Electrical Parameters',  # 字段显示名称
                                    help="Electrical characteristics")  # 字段帮助信息 - 电气特性

    # 告警规则字段，一对多关联设备告警规则模型
    alert_rule_ids = fields.One2many('equipment.alert.rule', 'equipment_id',  # 一对多关系
                                     string='Alert Rules')  # 字段显示名称 - 告警规则

    # 巡检记录字段，一对多关联设备巡检记录模型
    inspection_ids = fields.One2many('equipment.inspection', 'equipment_id',  # 一对多关系
                                     string='Inspection Records')  # 字段显示名称 - 巡检记录

    # 监测数据字段，一对多关联设备监测数据模型
    monitoring_data_ids = fields.One2many('equipment.monitoring.data', 'equipment_id',  # 一对多关系
                                          string='Monitoring Data')  # 字段显示名称 - 监测数据

    def _generate_qr_code(self):
        """内部方法：为单个设备生成二维码（带错误处理）"""
        try:
            import qrcode
            import base64
            from io import BytesIO

            # 获取 Odoo 实例的基础 URL
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if not base_url:
                raise ValueError("无法获取系统基础URL")

            # 创建设备详情页的URL
            equipment_url = f"{base_url}/web#id={self.id}&model=maintenance.equipment&view_type=form"

            # 创建 QRCode 对象
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )

            # 添加设备详情页面的 URL 到二维码数据中
            qr.add_data(equipment_url)
            qr.make(fit=True)

            # 创建二维码图像
            img = qr.make_image(fill_color="black", back_color="white")

            # 将图像保存到字节缓冲区
            buffered = BytesIO()
            img.save(buffered, format="PNG")

            # 将图像编码为 base64 并保存到设备记录
            self.qr_code = base64.b64encode(buffered.getvalue())
            self.qr_code_generated = True
            _logger.info(f"二维码生成完成：{self.name} (ID: {self.id})")
            return True

        except ImportError:
            _logger.error("生成二维码失败：缺少qrcode库。请安装: pip install qrcode[pil]")
            return False
        except Exception as e:
            _logger.error(f"生成二维码失败：{str(e)}")
            return False

    def generate_qr_code(self):
        """为设备生成二维码（带通知反馈）"""
        success_count = 0
        error_count = 0

        for equipment in self:
            try:
                if not equipment.qr_code_generated:
                    if equipment._generate_qr_code():
                        success_count += 1
                    else:
                        error_count += 1
            except Exception as e:
                _logger.error(f"生成设备 {equipment.name} 二维码时出错: {str(e)}")
                error_count += 1

        # 更新UI显示结果
        if len(self) == 1:
            if success_count == 1:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': '成功',
                        'message': f'已为设备 {self.name} 生成二维码',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': '错误',
                        'message': f'生成二维码失败: 请检查日志获取详细信息',
                        'type': 'danger',
                        'sticky': True,
                    }
                }
        else:
            message = f"操作完成: 成功生成 {success_count} 个二维码"
            if error_count > 0:
                message += f", {error_count} 个失败"

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '批量生成结果',
                    'message': message,
                    'type': 'success' if error_count == 0 else 'warning',
                    'sticky': error_count > 0,
                }
            }

    def action_print_qr(self):
        """设备二维码打印动作（单设备）"""
        # 确保二维码已生成
        if not self.qr_code_generated:
            if not self._generate_qr_code():
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': '错误',
                        'message': '二维码生成失败，无法打印',
                        'type': 'danger',
                        'sticky': True,
                    }
                }

        # 返回报表动作
        return {
            'type': 'ir.actions.report',
            'report_name': 'equipment_management.report_equipment_qr',
            'model': 'maintenance.equipment',
            'report_type': 'qweb-pdf',
            'context': {
                'active_id': self.id,
                'active_ids': [self.id],
            },
            'data': {
                'model': 'maintenance.equipment',
                'ids': [self.id],
            },
            'name': f'设备二维码 - {self.name}'
        }

    # 优化批量打印方法
    def batch_generate_selected(self):
        """批量打印选中设备的二维码（带错误处理）"""
        if not self:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': '请先选择要打印的设备',
                    'type': 'warning',
                    'sticky': False,
                }
            }

        success_ids = []
        error_equipments = []

        for equipment in self:
            try:
                if not equipment.qr_code_generated:
                    if equipment._generate_qr_code():
                        success_ids.append(equipment.id)
                    else:
                        error_equipments.append(equipment.name)
                else:
                    success_ids.append(equipment.id)
            except Exception as e:
                _logger.error(f"设备 {equipment.name} 生成二维码失败: {str(e)}")
                error_equipments.append(equipment.name)

        # 显示操作结果通知
        message = f"成功生成 {len(success_ids)} 个二维码"
        if error_equipments:
            message += f"，失败设备: {', '.join(error_equipments)}"

        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '批量操作结果',
                'message': message,
                'type': 'success' if not error_equipments else 'warning',
                'sticky': bool(error_equipments),
            }
        }

        # 仅当有成功生成的设备时才返回打印动作
        if success_ids:
            return {
                'type': 'ir.actions.report',
                'report_name': 'equipment_management.report_equipment_qr_batch',
                'report_type': 'qweb-pdf',
                'data': {'model': 'maintenance.equipment', 'ids': success_ids},
                'context': {'active_ids': success_ids},
                'name': f'设备二维码批量打印 - {datetime.now().strftime("%Y%m%d%H%M%S")}'
            }
        return notification

class EquipmentMonitoringData(models.Model):
    """设备监测数据模型，用于存储设备传感器采集的实时数据。"""
    _name = 'equipment.monitoring.data'
    _description = 'Equipment Monitoring Data'
    _order = 'timestamp desc'  # 默认按时间戳降序排序

    # 关联设备字段，多对一关联维护设备模型
    equipment_id = fields.Many2one('maintenance.equipment',  # 多对一关系
                                   required=True,  # 必填字段
                                   string='Equipment',  # 字段显示名称
                                   help="Related equipment")  # 字段帮助信息 - 关联设备

    # 时间戳字段，记录数据采集的时间
    timestamp = fields.Datetime(string='Timestamp',  # 字段显示名称
                                default=fields.Datetime.now,  # 默认当前时间
                                help="Data collection time")  # 字段帮助信息 - 数据采集时间

    # 设备转速字段，记录设备的旋转速度
    rotation_speed = fields.Float(string='Rotation Speed (RPM)',  # 字段显示名称
                                  help="Equipment rotation speed")  # 字段帮助信息 - 设备转速

    # 振动速度字段，记录设备的振动速度测量值
    vibration_velocity = fields.Float(string='Vibration Velocity (mm/s)',  # 字段显示名称
                                      help="Vibration velocity measurement")  # 字段帮助信息 - 振动速度测量

    # 第一段加速度包络字段，记录设备的第一段加速度包络值
    acceleration_env1 = fields.Float(string='Acceleration Envelope 1 (g)',  # 字段显示名称
                                     help="First acceleration envelope")  # 字段帮助信息 - 第一段加速度包络

    # 第二段加速度包络字段，记录设备的第二段加速度包络值
    acceleration_env2 = fields.Float(string='Acceleration Envelope 2 (g)',  # 字段显示名称
                                     help="Second acceleration envelope")  # 字段帮助信息 - 第二段加速度包络

    # 设备温度字段，记录设备的温度值
    temperature = fields.Float(string='Temperature (°C)',  # 字段显示名称
                               help="Equipment temperature")  # 字段帮助信息 - 设备温度

    # 索引设备 ID 字段，用于优化查询性能
    index_equipment_id = fields.Many2one(
        'maintenance.equipment',
        string='Index Equipment',  # 字段显示名称
        index=True,  # 创建数据库索引
        compute='_compute_index_fields',  # 计算字段
        store=True  # 存储到数据库
    )

    # 索引日期字段，用于优化查询性能
    index_date = fields.Date(
        string='Index Date',  # 字段显示名称
        index=True,  # 创建数据库索引
        compute='_compute_index_fields',  # 计算字段
        store=True  # 存储到数据库
    )

    # 记录激活状态字段，用于数据生命周期管理
    active = fields.Boolean(string='Active',  # 字段显示名称
                            default=True,  # 默认激活状态
                            help="Indicates if the record is active")  # 字段帮助信息 - 指示记录是否激活

    # 归档日期字段，记录数据归档的日期
    archive_date = fields.Date(string='Archive Date',  # 字段显示名称
                               help="Date when the record was archived")  # 字段帮助信息 - 记录归档日期


    @api.depends('equipment_id', 'timestamp')  # 依赖字段变化时重新计算
    def _compute_index_fields(self):
        """计算索引字段的值，以优化查询性能。"""
        for record in self:
            # 设备 ID 直接复制
            record.index_equipment_id = record.equipment_id.id
            # 从时间戳提取日期部分
            if record.timestamp:
                record.index_date = record.timestamp.date()

    def optimize_indexes(self):
        """优化数据库索引，提高查询性能。"""
        _logger.info("Starting to optimize monitoring data indexes...")

        try:
            # 重建关键索引
            self.env.cr.execute("""
                REINDEX INDEX monitoring_data_equipment_index;
                REINDEX INDEX monitoring_data_timestamp_index;
                REINDEX INDEX monitoring_data_equipment_timestamp_index;
            """)

            # 更新表统计信息，帮助查询优化器
            self.env.cr.execute("ANALYZE equipment_monitoring_data;")

            _logger.info("Index optimization completed")
            return True
        except Exception as e:
            _logger.error("Index optimization failed: %s", str(e))
            return False

    def index_usage_report(self):
        """生成索引使用情况报告，用于性能分析。"""
        try:
            # 查询 PostgreSQL 索引使用统计
            self.env.cr.execute("""
                SELECT 
                    relname AS table_name,
                    indexrelname AS index_name,
                    idx_scan AS scans,
                    idx_tup_read AS tuples_read,
                    idx_tup_fetch AS tuples_fetched
                FROM 
                    pg_stat_user_indexes
                WHERE 
                    relname = 'equipment_monitoring_data'
                ORDER BY 
                    idx_scan DESC;
            """)
            results = self.env.cr.dictfetchall()

            # 构建报告文本
            report = "Index usage report:\n"
            report += "-" * 50 + "\n"
            for row in results:
                report += (f"Index name: {row['index_name']}\n"
                           f"Scan count: {row['scans']}\n"
                           f"Tuples read: {row['tuples_read']}\n"
                           f"Tuples fetched: {row['tuples_fetched']}\n"
                           "-" * 50 + "\n")

            _logger.info(report)
            return results
        except Exception as e:
            _logger.error("Failed to generate index report: %s", str(e))
            return []

    def archive_old_data(self, days=180, batch_size=10000):
        """分批归档旧数据，避免内存溢出。

        :param days: 归档多少天前的数据，默认 180 天。
        :param batch_size: 每次处理的记录数量，默认 10000 条。
        :return: 归档的记录总数。
        """
        date_limit = fields.Date.today() - timedelta(days=days)
        total_archived = 0

        while True:
            # 每次处理一批记录
            records = self.search([
                ('timestamp', '<', date_limit),
                ('active', '=', True)
            ], limit=batch_size)

            if not records:
                break

            records.write({
                'active': False,
                'archive_date': fields.Date.today()
            })
            total_archived += len(records)
            self.env.cr.commit()  # 提交事务释放内存

            # 防止长时间占用资源
            if total_archived > batch_size * 5:
                _logger.info("Archived %d records, pausing for 10 seconds...", total_archived)
                time.sleep(10)

        _logger.info("Total %d records archived", total_archived)
        return total_archived


class EquipmentAlertRule(models.Model):
    """设备告警规则模型，用于定义设备参数的告警阈值。"""
    _name = 'equipment.alert.rule'
    _description = 'Equipment Alert Rule'

    # 规则名称字段，唯一标识告警规则
    name = fields.Char(string='Rule Name',  # 字段显示名称
                       required=True,  # 必填字段
                       help="Name of alert rule")  # 字段帮助信息 - 告警规则名称

    # 关联设备字段，多对一关联维护设备模型
    equipment_id = fields.Many2one('maintenance.equipment',  # 多对一关系
                                   required=True,  # 必填字段
                                   string='Equipment',  # 字段显示名称
                                   help="Related equipment")  # 字段帮助信息 - 关联设备

    # 监测参数字段，定义要监测的设备参数
    parameter = fields.Selection([
        ('rotation_speed', 'Rotation Speed'),  # 转速
        ('vibration_velocity', 'Vibration Velocity'),  # 振动速度
        ('acceleration_env1', 'Acceleration Envelope 1'),  # 第一段加速度包络
        ('acceleration_env2', 'Acceleration Envelope 2'),  # 第二段加速度包络
        ('temperature', 'Temperature')  # 温度
    ], string='Parameter',  # 字段显示名称
        required=True,  # 必填字段
        help="Parameter to monitor")  # 字段帮助信息 - 要监测的参数

    # 告警条件字段，定义告警触发的条件
    condition = fields.Selection([
        ('>', 'Greater Than'),  # 大于
        ('<', 'Less Than'),  # 小于
        ('=', 'Equal To'),  # 等于
        ('>=', 'Greater or Equal'),  # 大于等于
        ('<=', 'Less or Equal')  # 小于等于
    ], string='Condition',  # 字段显示名称
        required=True,  # 必填字段
        help="Condition for alert")  # 字段帮助信息 - 告警条件

    # 阈值字段，定义告警触发的值
    threshold = fields.Float(string='Threshold',  # 字段显示名称
                             required=True,  # 必填字段
                             help="Threshold value")  # 字段帮助信息 - 阈值

    # 严重级别字段，定义告警的严重程度
    severity = fields.Selection([
        ('low', 'Low'),  # 低 - 一般告警
        ('medium', 'Medium'),  # 中 - 需要注意
        ('high', 'High')  # 高 - 紧急告警
    ], string='Severity',  # 字段显示名称
        default='medium',  # 默认中等严重级别
        help="Severity level")  # 字段帮助信息 - 严重级别


class EquipmentInspection(models.Model):
    """设备巡检记录模型，用于存储设备检查结果。"""
    _name = 'equipment.inspection'
    _description = 'Equipment Inspection Record'

    # 参考编号字段，作为巡检记录的唯一标识
    name = fields.Char(string='Reference',
                       required=True,
                       default=lambda self: self.env['ir.sequence'].next_by_code('equipment.inspection'))

    # 关联设备字段，多对一关联维护设备模型
    equipment_id = fields.Many2one('maintenance.equipment',
                                   required=True,
                                   string='Equipment',
                                   help="Inspected equipment")

    # 检查日期字段，记录巡检执行的时间
    inspection_date = fields.Datetime(string='Inspection Date',
                                      default=fields.Datetime.now,
                                      help="Date of inspection")

    # 检查人员字段，多对一关联用户模型
    inspector_id = fields.Many2one('res.users',
                                   string='Inspector',
                                   default=lambda self: self.env.user,
                                   help="Person performing inspection")

    # 检查结果字段，记录巡检的结论
    result = fields.Selection([
        ('pass', 'Pass'),  # 通过 - 设备正常
        ('fail', 'Fail'),  # 失败 - 发现问题
        ('na', 'N/A')  # 不适用 - 未检查
    ], string='Result',
                             help="Inspection result")

    # 检查说明字段，记录巡检的详细信息
    notes = fields.Text(string='Notes',
                        help="Inspection findings")

    # 关联维护工单字段，多对一关联维护请求模型
    request_id = fields.Many2one('maintenance.request',
                                 string='Maintenance Request')

    def create_request(self):
        """为当前巡检记录创建维护请求。"""
        for record in self:
            # 确保尚未创建请求
            if not record.request_id:
                # 创建维护请求
                request = self.env['maintenance.request'].create({
                    'name': f'Inspection Maintenance Request: {record.name}',
                    'equipment_id': record.equipment_id.id,
                    'description': record.notes or '',
                    'maintenance_type': 'cm',  # 纠正性维护
                    'inspection_id': record.id,  # 关联当前巡检记录
                    'user_id': record.inspector_id.id if record.inspector_id else False,
                    'schedule_date': fields.Datetime.now(),
                })
                # 更新当前记录的请求 ID
                record.request_id = request.id
                _logger.info("Maintenance request %s created for inspection record %s", request.name, record.name)

                # 返回通知消息
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Maintenance Request Created',
                        'message': f'Maintenance request {request.name} created successfully',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            # 如果请求已存在，返回警告
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Operation Failed',
                    'message': 'This inspection record is already associated with a maintenance request',
                    'type': 'warning',
                    'sticky': False,
                }
            }


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    # 关联巡检记录字段，多对一关联设备巡检记录模型
    inspection_id = fields.Many2one('equipment.inspection',
                                    string='Inspection Record',
                                    ondelete='set null')
    # 维护类型字段，定义维护的类型
    maintenance_type = fields.Selection(
        selection_add=
            [('cm', 'Corrective Maintenance'), ('pm', 'Preventive Maintenance'), ('pd', 'Predictive Maintenance')],
            string='Maintenance Type',
            default='cm'
    )