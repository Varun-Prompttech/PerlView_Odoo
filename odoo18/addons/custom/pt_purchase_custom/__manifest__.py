{
    'name': 'Prompttech Purchase Custom',
    'version': '18.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Prompttech Purchase Custom',
    'description': 'Prompttech Purchase Custom',
    'author': 'Prompttech Global',
    'company': 'Prompttech Global',
    'maintainer': 'Prompttech Global',
    'depends': ['base','contacts', 'sale', 'purchase', 'account','purchase_request','stock'],
    'data': [
        'security/security.xml',
        'views/purchase_order_line.xml',
        'views/account_move_line.xml',
        'views/purchase_request.xml',
        'views/inherit_res_partner.xml',
        'views/stock_picking.xml',
        'views/stock_picking_type.xml',
        'wizard/purchase_request_line_make_purchase_order_item.xml',
    ],
    'license': 'LGPL-3',
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# -*- coding: utf-8 -*-

