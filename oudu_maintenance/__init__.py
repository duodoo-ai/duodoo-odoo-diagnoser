# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from . import controllers
from . import report
from . import models

# 在 models/__init__.py 中添加
import logging
_logger = logging.getLogger(__name__)

# 添加定时索引维护任务
# 在__init__.py中添加
from . import models


def post_init_hook(cr, registry):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    # 创建每周索引优化任务
    cron_model = env['ir.cron']
    cron_model.create({
        'name': 'Weekly Index Optimization',
        'model_id': env.ref('model_equipment_monitoring_data').id,
        'state': 'code',
        'code': 'model.optimize_indexes()',
        'interval_number': 1,
        'interval_type': 'weeks',
        'numbercall': -1,
        'active': True,
    })

    # 创建每日归档任务
    cron_model.create({
        'name': 'Daily Data Archiving',
        'model_id': env.ref('model_equipment_monitoring_data').id,
        'state': 'code',
        'code': 'model.archive_old_data(180)',  # 归档180天前的数据
        'interval_number': 1,
        'interval_type': 'days',
        'numbercall': -1,
        'active': True,
    })

    _logger.info("Equipment monitoring module initialized with cron jobs")