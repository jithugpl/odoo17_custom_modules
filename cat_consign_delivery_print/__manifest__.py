# -*- coding: utf-8 -*-
{
    'name': "cat_consign_delivery_print",
    'summary': "Delivery Consignment Print Module",
    'description': """
    Used in Inventory module to print Consignment Delivery
    """,
    'author': "TechTurtles@Catalist",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0',
    # any module necessary for this one to work correctly
    'depends': ['base','stock','sale','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'report/consign_delivery_template.xml',
        'report/consign_delivery_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'sequence': -80,
    'auto install': False,
    'application': True,
    'license': 'LGPL-3'
}

