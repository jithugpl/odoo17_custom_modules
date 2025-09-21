# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Sale Excel Report',
    'version': '17.0.1.0.0',
    'summary': 'Sale Excel Report',
    'author': 'Divergent Catalist',
    'company': 'Divergent Catalist ERP Solutions',
    'maintainer': 'Divergent Catalist ERP Solutions',
    'sequence': -5,
    'description': """Sale Excel Report""",
    'category': 'Sales',
    'website': 'https://www.catalisterp.com/',
    'depends': ['base','sale','account'],
    'data': [
        'views/sale_report_excel_views.xml'
    ],
    'licenSe': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False
}
