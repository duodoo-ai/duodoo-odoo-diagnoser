# -*- coding: utf-8 -*-
{
    'name': "Odoo Maintenance Extend (RTX)",

    'summary': """
        Intelligent Equipment Maintenance Management Platform
    """,

    'description': """
        Inherit Odoo 18 Maintenance module. Features include equipment management, 
        maintenance, repair, fault management, repair cost management, work order 
        management, data collection, visualization analysis, data backup, import/export, 
        permission control and audit tracking.
        More Support：
        18951631470
        zou.jason@qq.com
    """,
    'author': "Jason Zou",
    "website": "www.duodoo.tech",

    'category': 'oudu',
    'version': '1.0',

    'depends': [
        'base',
        'mail',
        'project',
        'project_todo',
        'oudu_core',
        'maintenance',
        ],
    'external_dependencies': {
            'python': ['qrcode', 'PIL'],
        },
    'data': [
        'data/maintenance_data.xml',
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
        # 'views/maintenance_equipment.xml',
        'views/maintenance_equipment_status_history_view.xml',
        'views/maintenance_equipment_category_views.xml',
        'views/maintenance_work_order.xml',
        'views/maintenance_work_order_history.xml',
        'views/maintenance_equipment_barcode.xml',
        'views/maintenance_equipment_inspection.xml',
        'wizards/maintenance_inspection_wizard_views.xml',
        'report/report_equipment_barcode.xml',
        'report/report_data.xml',
        # 'views/maintenance_equipment_inspection_item.xml',
        # 'views/maintenance_equipment_repair.xml',
        # 'views/maintenance_equipment_maintenance.xml',
        'views/menu_views.xml',
        'views/menu_hide_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # 'oudu_maintenance/static/src/js/barcode_scanner.js',
            # 'oudu_maintenance/static/src/xml/barcode_template.xml',
            'oudu_maintenance/static/src/css/qrcode_style.css',
            'oudu_maintenance/static/src/js/barcode_handler.js'
            # 'oudu_maintenance/static/src/js/instascan.min.js',
            # 'oudu_maintenance/static/src/css/qr_scanner.css',
            # 'oudu_maintenance/static/src/xml/qr_template.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "AGPL-3",
}
