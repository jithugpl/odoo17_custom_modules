# -*- coding: utf-8 -*-
{
    'name': "RA Bill",
    'version': '17.0.0.1',
    'summary': 'RA Bill',
    'depends': ['mail', 'account', 'base', 'sale_management', 'sale', 'construction_material_management',
                'sale_project'],
    'description': """RA Bill""",
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/ra_bill_views.xml',
        'views/sale_order_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3'
}
