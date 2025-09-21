{
    'name': 'Datavalley Product Automatic Internal Reference with Barcode and Stylecode',
    'version': '1.0',
    'summary': 'Automatically sync internal reference with barcode and style code',
    'sequence': 10,
    'author': 'Datavalley Web Service',
    'website': 'https://www.datavalley.in',
    'images': ['static/description/product_categories_arborescence.png'],
    'description': "This module extends the product form to automatically update the product barcode and a new style code field.based on the internal reference, Both fields are marked as read-only",
    'category': 'Inventory/Inventory',
    'depends': ['stock'],
    'data': [
        'views/product_category_views.xml',
        'views/product_product_views.xml',
        'views/product_template_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
