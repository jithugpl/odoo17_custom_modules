# -*- coding: utf-8 -*-
{
    'name': "Datavalley Task Management",
    'description': """""",
    'author': "Datavalley",
    'website': "https://www.datavalley.in",
    'category': 'website',
    'version': '17.0.0.0.1',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/task_management_security.xml',
        'views/task_type_views.xml',
        'views/trainee_type_views.xml',
        'views/task_manager_views.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3',

}
