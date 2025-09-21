{
    'name': 'Cleaning Form',
    'version': '17.0.1.0.0',
    'summary': 'Form for cleaning activity',
    'author': 'Divergent Catalist ERP Solutions',
    'company': 'Divergent Catalist ERP Solutions',
    'maintainer': 'Divergent Catalist ERP Solutions',
    'sequence': -1,
    'description': """Cleaning Form""",
    'category': 'Inventory',
    'website': 'https://www.catalisterp.com/',
    'depends': ['base', 'project', 'product', 'mail', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/cleaning_security.xml',
        'data/sequence.xml',
        'views/menu.xml',
        'views/cleaning_form_view.xml',
    ],
    'licenSe': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False
}
