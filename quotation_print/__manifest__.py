{
    'name': 'Quotation Print',
    'version': '17.0.1.0.0',
    'summary': 'Quotation Print',
    'author': 'Divergent Catalist ERP Solutions',
    'company': 'Divergent Catalist ERP Solutions',
    'maintainer': 'Divergent Catalist ERP Solutions',
    'sequence': 10,
    'description': """'Quotation Print""",
    'category': 'sale',
    'website': 'https://www.catalisterp.com/',
    'depends': ['sale','sale_management','stock','mail','package_template','report_qweb_pdf_watermark','print_header_footer'],
    'data': [
        'report/quotation_report_action.xml',
        'report/quotation_report_view.xml',
        'report/file.xml',

            ],
    'licenSe': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False
}