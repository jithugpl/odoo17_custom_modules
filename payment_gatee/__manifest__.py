# -*- coding: utf-8 -*-
# Copyright (c) 2024-Present Gate-E. (<https://www.Gate-E.com>)

{
    'name': 'Gate-e Payment | Easy - Secure - Advanced',
    'category': 'Accounting/Payment Acquirers',
    'version': '17.0',
    'license': 'OPL-1',
    'author': 'Sayed Hassan, Gate-E',
    'website': 'https://gate-e.com',
    'depends': ['account', 'payment'],
    'data': [
        'views/payment_gatee_templates.xml',
        'data/account_journal_data.xml',
        'views/payment_provider.xml',
        'data/payment_method_data.xml',
        'data/payment_provider_data.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'application': True,

    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',

    'description': """Gate-e Payment Provider""",
    'summary': '''
        Payment Provider: Gate-e Payment Gateway
        Online Payment
        E-commerce Payment
        Invoice Payment
        Bahrain Payment
        Debit Card Payment
    '''
}
