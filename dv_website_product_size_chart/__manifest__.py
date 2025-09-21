# -*- coding: utf-8 -*-
{
    'name': "Datavalley Website Product Size Chart",
    'summary': "The Website Product Size Chart is designed to enhance the product listing pages on your Odoo website by displaying size charts for products. It allows customers to easily determine the appropriate size for their needs, thereby improving their shopping experience.",
    'description': """The Website Product Size Chart is designed to display size charts for products.""",
    'author': "Datavalley",
    'website': "https://www.datavalley.in",
    'category': 'website',
    'version': '17.0.0.0.1',
    'depends': ['base', 'website_sale'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/website_product_size_chart_views.xml',
        'views/templates.xml',
        'views/website_sale_templates.xml',
    ],
    # 'images': ['static/description/banner.png'],
'icon': '/dv_website_product_size_chart/static/description/icon.png',
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3',

}
