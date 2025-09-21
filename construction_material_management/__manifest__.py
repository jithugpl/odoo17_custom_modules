# -*- coding: utf-8 -*-
{
    'name': "Construction Material Management",
    'version': '17.0.0.1',
    'summary': 'Construction Material Management',
    'depends': ['crm', 'mail', 'account', 'stock', 'base', 'mrp', 'purchase', 'project', 'general_master',
                'purchase_stock'],
    'description': """Construction Material Management""",
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/site_material_transfer_sequence.xml',
        'views/account_move.xml',
        'views/actual_bom_views.xml',
        'views/amendment_request_views.xml',
        'views/material_request_views.xml',
        'views/stock_picking_type.xml',
        'views/stock_picking_views.xml',
        'views/purchase_order.xml',
        'views/project_project.xml',
        'views/material_purchase_requisition.xml',
        'views/site_material_transfer_view.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3'
}
