# -*- coding: utf-8 -*-
{
    'name': "Odoo IEEMS (RTX)",

    'summary': """
        Odoo Integrated Energy Efficiency Management System
    """,

    'description': """Odoo Integrated Energy Efficiency Management System
                    More Support：
                    18951631470
                    zou.jason@qq.com
                    """,

    'author': "Jason Zou",
    "website": "www.duodoo.tech",

    'category': 'oudu',
    'version': '1.0',

    'depends': ['base', 'mail', 'project', 'project_todo', 'oudu_core'],
    'data': [
        'data/circuit_data.xml',
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/circuit_name_views.xml',
        'views/electrical_safety_views.xml',
        'views/energy_analysis_views.xml',
        'views/energy_statistics_views.xml',
        'views/power_monitoring_views.xml',
        'views/circuit_views.xml',
        'views/mom_views.xml',
        'views/yoy_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "AGPL-3",
}
