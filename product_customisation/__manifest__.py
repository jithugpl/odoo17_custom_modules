{
    'name': 'Product Customisation',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Add customisation form for products.',
    'depends': ['crm', 'product','stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_customisation_views.xml',
        'views/product_template_inherit_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}
