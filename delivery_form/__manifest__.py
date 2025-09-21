{
    'name': 'Delivery Form',
    'version': '17.0.1.0.0',
    'summary': 'Delivery Form,Print,Dispatch Report',
    'author': 'Divergent Catalist ERP Solutions',
    'company': 'Divergent Catalist ERP Solutions',
    'maintainer': 'Divergent Catalist ERP Solutions',
    'sequence': -1,
    'description': """Delivery Note Form""",
    'category': 'Inventory',
    'website': 'https://www.catalisterp.com/',
    'depends': ['base', 'project', 'product', 'mail', 'stock', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'security/delivery_security.xml',
        'wizard/delivery_wizard_view.xml',
        'views/menu.xml',
        'views/form.xml',
        'views/dispatch_report_view.xml',
        'data/sequence_data.xml',
        'report/report.xml',
        'report/layout.xml',
        'report/delivery_slip.xml',


    ],
    'licenSe': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False
}
