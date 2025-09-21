{
    'name': 'rabill_print',
    'version': '1.0',
    'summary': 'Module to print RA bill',
    'sequence': 10,
    'author': 'catalist',
    'license': 'LGPL-3',
    'depends': ['mail', 'account', 'base', 'sale_management', 'sale', 'construction_material_management',
                'sale_project','print_header_footer'],
    'data': ['views/rabillview.xml',
        'views/rareports.xml'

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}