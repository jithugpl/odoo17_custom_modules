{
    'name': 'trial_form',
    'version': '17.0.1.0.0',
    'summary': 'Trial form for study purpose',
    'author': 'Divergent Catalist ERP Solutions',
    'company': 'Divergent Catalist ERP Solutions',
    'maintainer': 'Divergent Catalist ERP Solutions',
    'sequence': -1,
    'description': """Trial Form""",
    'category': 'Project',
    'website': 'https://www.catalisterp.com/',
    'depends': ['base', 'project', 'product',],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/menu.xml',
        'views/trial_form_view.xml',

    ],
    'licenSe': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False
}
