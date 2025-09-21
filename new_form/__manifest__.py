{
    'name': 'NEW FORM',
    'version': '17.0.1.0.0',
    'summary': 'Create new form in sale',
    'author': 'Datavalley',
    'company': 'Datavalley',
    'maintainer': 'Datavalley',
    'sequence': -1,
    'description': """New Form""",
    'category': 'Sale',
    'website': 'https://www.catalisterp.com/',
    'depends': ['base','sale', 'mail','stock','product'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/menu.xml',
        'views/form_view.xml',
        'views/stage.xml'



    ],
    'licenSe': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False
}
