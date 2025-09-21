{
    'name': 'POS Product Order History',
    'version': '17.0.1.0',
    'category': 'Sales/Point of Sale',
    'summary': 'View recent POS sales directly in the product form view',
    'author': 'Uday Sankar K',
    'website': 'https://uday0sankar.github.io/',
    'maintainer': 'Uday Sankar K',
    'license': 'LGPL-3',
    'depends': ['point_of_sale', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
    ],
      # Optional: for marketing look
    'installable': True,
    'auto_install': False,
    'application': True,
}
