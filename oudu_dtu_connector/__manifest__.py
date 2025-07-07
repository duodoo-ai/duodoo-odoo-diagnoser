# -*- coding: utf-8 -*-
{
    'name': "Odoo DTU Connector (RTX)",

    'summary': """
        给Odoo与DTU平台连接，以完成数据从DTU网关采集数据到Odoo平台
    """,

    'description': """给Odoo与平台连接，以完成数据从DTU网关采集数据到Odoo平台，以完成后续维检操作
                    更多支持：
                    18951631470
                    zou.jason@qq.com
                    """,

    'author': "Jason Zou",
    "website": "-",

    'category': 'oudu',
    'version': '1.0',

    'depends': ['iot'],

    'data': [
        'data/dtu_cron.xml',
        'data/dtu_data.xml',
        'data/dtu_demo.xml',
        'security/ir.model.access.csv',
        'views/dtu_data_views.xml',
        'views/dtu_menu_views.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "AGPL-3",
}
