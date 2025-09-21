# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'SMBG Sales Invoice Report',
    'version': '17.0.1.0.0',
    'summary': 'SMBG Sales Invoice Report',
    'author': 'Divergent Catalist ERP Solutions',
    'company': 'Divergent Catalist ERP Solutions',
    'maintainer': 'Divergent Catalist ERP Solutions',
    'sequence': -1,
    'description': """SMBG Sales Invoice Report""",
    'category': 'Accounting',
    'website': 'https://www.catalisterp.com/',
    'depends': ['base', 'account', 'l10n_ae', 'website_cancel_sale_order', 'smbg_report'],
    'data': [
        'views/res_company.xml',
        'views/tax_invoice_excel.xml',
        'views/res_partner_bank.xml',
        'report/tax_invoice_report.xml',
        'report/tax_invoice_report_temp.xml'
    ],
    'licenSe': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False
}
