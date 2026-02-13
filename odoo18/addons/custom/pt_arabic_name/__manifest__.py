# -*- coding: utf-8 -*-
{
    'name': "pt_arabic_name",
    'version': '18.0',
    'category': 'Uncategorized',
    'summary': "Custom module for arabic name in pos",
    'description':'Custom module for arabic name in pos and pos receipt',
    'author': "Prompt Tech",

    'company': "Prompt Tech",
    'maintainer': "Prompt Tech",
    'website': "https://prompttechsolutions.com/",

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'point_of_sale',],

    # always loaded
    'data': [
        'views/product_name.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            "pt_arabic_name/static/src/js/pos_receipt.js",
            "pt_arabic_name/static/src/js/product_screen.js",
            "pt_arabic_name/static/src/xml/pos_receipt.xml",
            "pt_arabic_name/static/src/xml/pos_ui.xml",
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

