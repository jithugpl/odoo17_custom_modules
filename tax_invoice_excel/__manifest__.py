# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'TAX Invoice Excel Report',
    'version': '17.0.1.0.0',
    'summary': 'TAX Invoice Excel Report',
    'author': 'Divergent Catalist ERP Solutions',
    'company': 'Divergent Catalist ERP Solutions',
    'maintainer': 'Divergent Catalist ERP Solutions',
    'sequence': -1,
    'description': """TAX Invoice Excel Report""",
    'category': 'Accounting',
    'website': 'https://www.catalisterp.com/',
    'depends': ['base', 'account', 'sale', ],
# 'website_cancel_sale_order', 'smbg_report'
    'data': [
        'view/tax_invoice_excel_views.xml'
    ],
    'licenSe': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False
}
