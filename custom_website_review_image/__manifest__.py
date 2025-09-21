{
    'name': 'Custom Website Review Image',
    'version': '1.0',
    'summary': 'Ensures uploaded images in website reviews are visible.',
    'description': 'A custom module to make uploaded images visible in the website review section of Odoo 17.',
    'author': 'Your Name',
    'category': 'Website',
    'depends': ['website', 'rating','website_sale','portal'],
    'data': [
        'views/website_review_template.xml',
    ],
    'installable': True,
    'application': False,
}
