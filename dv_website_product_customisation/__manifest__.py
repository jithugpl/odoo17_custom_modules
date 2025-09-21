# -*- coding: utf-8 -*-
{
    'name': "Datavalley Website Product Customisation",
    'summary': "The Website Product Size Chart is designed to enhance the product listing pages on your Odoo website by displaying size charts for products. It allows customers to easily determine the appropriate size for their needs, thereby improving their shopping experience.",
    'description': """The Website Product Size Chart is designed to enhance the product listing pages on your Odoo website by displaying size charts for products. It allows customers to easily determine the appropriate size for their needs, thereby improving their shopping experience.""",
    'author': "Datavalley",
    'website': "https://www.datavalley.in",
    'category': 'website',
    'version': '17.0.0.0.1',
    'depends': ['base', 'website_sale','crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/inherit_button.xml',
        # 'views/wizard_action.xml',
        'views/modal_form.xml',
        # 'views/form_template.xml'

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3',

}
