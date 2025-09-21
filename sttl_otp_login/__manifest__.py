# -*- coding: utf-8 -*-
{
    "name": "DV Email SMS OTP Authentication",
    "version": "17.0.1.0",
    "author": "Datavalley",
    'category': 'Website',
    "website": "https://datavalley.co.in/",
    "description": """
- User authentication via OTP for secure login and signup.
- SMS and Email notifications when a sales order is placed or confirmed
""",
    "summary": """
        This module allows the user authentication of the database via OTP.
    """,
    'depends': ['base', 'mail', 'web', 'website', 'auth_signup','sale','auth_oauth'],
    'data': [
        "security/ir.model.access.csv",
        "security/security_group.xml",
        "views/otp_verification.xml",
        "views/login_view.xml",
        "views/otp_signup.xml",
        "views/signup_page_view.xml",
        "data/cron.xml"
    ],
    "price": 0,
    "currency": "USD",
    "license": "LGPL-3",
    'installable': True,
    'application': False,
    'images': ['static/description/banner.png']
}
