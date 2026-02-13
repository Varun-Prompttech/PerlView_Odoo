# -*- coding: utf-8 -*-
{
    'name': "pt_pos_idletime",
    'version': '18.0',
    'category': 'Uncategorized',
    'summary': "Custom module for increasing pos idle screen time",
    'description':'Custom module for increasing pos idle screen time',
    'author': "Prompt Tech",

    'company': "Prompt Tech",
    'maintainer': "Prompt Tech",
    'website': "https://prompttechsolutions.com/",

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale',],

    'assets': {
        'point_of_sale._assets_pos': [
            "pt_pos_idletime/static/src/js/idle_timeout_patch.js",
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

