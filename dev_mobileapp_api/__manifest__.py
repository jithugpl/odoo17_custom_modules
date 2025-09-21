{
    'name': "DV Mobile App API",

    'summary': "REST API for Mobile E-commerce Integration",

    'description': """
DV Mobile App API Module""",

    'author': "DV",
    'website': "https://datavalley.co.in/",

    'category': 'Tools',
    'version': '1.0.0',

    'license': 'LGPL-3',

    'depends': ['base', 'web', 'sttl_otp_login','product','stock','sale_management','website_sale',
    'rating',],


    'data': [
        'views/res_users_views.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}