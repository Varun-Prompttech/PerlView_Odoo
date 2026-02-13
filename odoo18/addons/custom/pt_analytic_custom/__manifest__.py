# -*- coding: utf-8 -*-

{
    'name': 'Prompttech Analytic Custom',
    'version': '18.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Prompttech Analytic Custom',
    'description': 'Prompttech Analytic Custom',
    'author': 'Prompttech Global',
    'company': 'Prompttech Global',
    'maintainer': 'Prompttech Global',
    'depends': ['base', 'sale', 'purchase', 'account', 'purchase_request'],
    'data': [
        'views/sale_order.xml',
        'views/purchase_order.xml',
        'views/purchase_request.xml',
        'views/res_users.xml',
        'views/account_move.xml',
        'views/account_payment.xml',
        'views/stock_location.xml',
        # 'views/res_config_settings.xml',
    ],
    'license': 'LGPL-3',
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
