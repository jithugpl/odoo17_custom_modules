# power_factor_reading/__manifest__.py
# -*- coding: utf-8 -*-
{
    'name': 'Iso Masters',
    'version': '17.0',
    'summary': '',
    'description': ' Track power factor readings associated with shifts.',
    'author': 'Divergent Catalist ERP Solutions',
    'company': 'Divergent Catalist ERP Solutions',
    'maintainer': 'Divergent Catalist ERP Solutions',
    'category': 'Project',
    'depends': ['base'],
    'website': 'https://www.catalisterp.com/',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/iso_masters.xml',
        'views/iso_master_meter.xml',
        'views/iso_document.xml',

    ],
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3'
}
