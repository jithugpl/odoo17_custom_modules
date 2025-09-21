{
    'name': 'dv_brand_store',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'This module enhances the e-commerce experience by linking multiple brand stores to a product dynamically, making it easier for customers to navigate to their preferred brand store directly from the product page.',
    'description': 'This module adds a new tab in the Product Attribute Value form to store additional information.',
    'author': 'Datavalley Web Service',
    'website': "https://www.datavalley.in",
    "category": "Website",
    'depends': ['product'],
    'data': [

        'views/product_attribute_value_views.xml',
        'views/product_template.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
