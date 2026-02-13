# -*- coding: utf-8 -*-

{
    'name': 'Prompttech Allowed Operations',
    'version': '18.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Prompttech Allowed Operations',
    'description': 'Prompttech Allowed Operations',
    'author': 'Prompttech Global',
    'company': 'Prompttech Global',
    'maintainer': 'Prompttech Global',
    'depends': ['base','sale','purchase','account','purchase_stock','purchase_request'],
    # 'depends': ['base','sale','purchase','account','pt_analytic_custom','purchase_stock'],
    'data': [
        'views/res_users.xml',
        'views/purchase_order.xml',
        'views/stock_picking.xml',
    ],
    'license': 'LGPL-3',
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
