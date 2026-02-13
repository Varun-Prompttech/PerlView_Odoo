# -*- coding: utf-8 -*-
{
    'name': "pt_hide_cash_pos_closing",
    'version': '18.0',
    'category': 'Uncategorized',
    'summary': "Custom module for hiding cash in pos closing popup",
    'description':'Custom module for hiding cash in pos closing popup',
    'author': "Prompt Tech",

    'company': "Prompt Tech",
    'maintainer': "Prompt Tech",
    'website': "https://prompttechsolutions.com/",

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale'],

    'assets': {
        'point_of_sale._assets_pos': [
            "pt_hide_cash_pos_closing/static/src/xml/closing_popup.xml",
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

