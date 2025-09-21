{
    "name": "Datavalley Ecommerce Product Attributes Fields",
    "summary": "html fields for product details in website",
    "version": "17.0.1.0.0",
    "category": "Datavalley",
    "author": "Datavalley Web Service ",
    "description": """
DV Ecommerce Clothing Product Attributes
========================================

This module enhances the product management experience for eCommerce clothing stores by adding new attributes to product templates. These attributes provide detailed product information, improving the customer shopping experience and assisting administrators in better managing their inventory.

Key Features:
- Material Information
- Care Guide
- Items Included
- Product Notes
    """,

    "depends": ['product', 'website_sale', 'stock', 'website'],
    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/fields_views.xml',
        'views/product_page_inherit.xml',
        'views/attribute_views.xml',
        'views/menu.xml',
        'views/is_active_attribute.xml'

    ],
    "installable": True,
    "license": "AGPL-3",
}
