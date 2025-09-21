# -*- coding: utf-8 -*-
{
    'name': 'Car Wash Management',
    'description': 'This module allows managing types of car washes and related activities.',
    'author': "Datavalley",
    'website': "https://www.datavalley.in",
    'category': 'Services',
    'summary': 'Manage car wash types and operations',
    'version': '17.0.0.0.1',
    'depends': ['base', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/car_wash_views.xml',
        'views/car_detailing_views.xml',
        'views/car_wash_appoinment_views.xml',
        'views/vehicle_type_views.xml',
        'views/vehicle_details_views.xml',
        'views/detailing_appoinment_views.xml',
        'views/home_page.xml'

    ],
    'assets': {
        'web.assets_backend': [
            # 'car_wash_management/static/src/css/form_background.css',
            'car_wash_management/static/src/css/home_page.css',

        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3',

}
