{
    'name': 'Package Template',
    'version': '17.0.1.0.0',
    'summary': 'Package Template',
    'author': 'Divergent Catalist ERP Solutions',
    'company': 'Divergent Catalist ERP Solutions',
    'maintainer': 'Divergent Catalist ERP Solutions',
    'sequence': 10,
    'description': """Package Template""",
    'category': 'sale',
    'website': 'https://www.catalisterp.com/',
    'depends': ['sale','sale_management','stock','mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/package_template_view.xml',
        'views/quotation_view.xml',

            ],
    'licenSe': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False
}