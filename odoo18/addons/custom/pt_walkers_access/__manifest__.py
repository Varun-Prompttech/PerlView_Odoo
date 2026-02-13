# -*- coding: utf-8 -*-
{
    'name': "pt_walkers_access",
    'version': '18.0',
    'category': 'Uncategorized',
    'summary': "Custom module for access rights in pos",
    'description':'Custom module for access rights in pos',
    'author': "Prompt Tech",

    'company': "Prompt Tech",
    'maintainer': "Prompt Tech",
    'website': "https://prompttechsolutions.com/",

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale','sh_pos_all_in_one_retail','web','account'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/pos_custom_access.xml',
        'views/account_move.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pt_walkers_access/static/src/js/DiscountLimitPopup.js',
        ],
    },


    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],

}

