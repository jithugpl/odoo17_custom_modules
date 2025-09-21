{
    'name': 'Datavalley Product Codes',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Automatically sync internal reference with barcode and style code',
    'description': 'This module extends the product form to automatically update the product barcode and a new style code field.based on the internal reference, Both fields are marked as read-only',
    'author': 'Datavalley Web Service',
    'website': "https://www.datavalley.in",
    "category": "Website",
    'depends': ['product'],
    'data': [

        'views/product_template_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,

}
