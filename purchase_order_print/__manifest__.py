{
    'name': 'Purchase_order_print',
    'version': '17.0.1.0.0',
    'summary': 'Module to print purchase order ',
    'author': 'Divergent Catalist ERP Solutions',
    'company': 'Divergent Catalist ERP Solutions',
    'maintainer': 'Divergent Catalist ERP Solutions',
    'sequence': -1,
    'description': """Purchase Order Print""",
    'category': 'Purchase',
    'website': 'https://www.catalisterp.com/',
    'depends': ['purchase','project'],
    'data': [
        'report/report.xml',
        'report/purchase_template.xml',

    ],
    'licenSe': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False
}