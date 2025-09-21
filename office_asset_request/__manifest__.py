{
    'name': 'Office Asset Request',
    'version': '1.0',
    'category': 'HR',
    'summary': 'Employees can request office assets like laptops or chairs',
    'author': 'Jithu Gopal',
    'depends': ['base', 'hr'],
    'data': [

        'security/office_asset_groups.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/asset_request_views.xml',
    ],
    'installable': True,
    'application': True,
}
