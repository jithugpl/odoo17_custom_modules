{
    'name': 'Website Customer Registration',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Customer registration form on the website with admin notification',
    'depends': ['base', 'website', 'mail','sale_management','project'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/customer_registration_template.xml',
        # 'data/email_template.xml',
        # 'views/customer_reg.xml',
        'views/customer_form_custom_view.xml',
    ],
    'installable': True,
    'application': True,
}
