# custom_sms_integration/__manifest__.py

{
    'name': 'DV - Custom SMS Integration',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Integrate SMS notifications for sales orders',
    'author': 'Datavalley',

    'depends': ['sale','stock','auth_signup'],
    'data': [

        'views/templates.xml',
        'views/add_reset_password_button.xml'
    ],

    'installable': True,
    'application': False,
}
