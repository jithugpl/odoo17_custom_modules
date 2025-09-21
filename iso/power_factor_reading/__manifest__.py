#power_factor_reading/__manifest__.py
# -*- coding: utf-8 -*-
{
    'name': 'Power Factor Reading',
    'version': '17.0',
    'summary': 'Module to track power factor readings ',
    'description': ' Track power factor readings associated with shifts.',
    'author': 'Divergent Catalist ERP Solutions',
    'company': 'Divergent Catalist ERP Solutions',
    'maintainer': 'Divergent Catalist ERP Solutions',
    'category': 'Project',
    'depends': ['base','mail','iso_masters'],
    'website': 'https://www.catalisterp.com/',
    'data': [
        'security/ir.model.access.csv',
        'views/power_factor_reading_views.xml',
        "security/security.xml"
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3'
}
