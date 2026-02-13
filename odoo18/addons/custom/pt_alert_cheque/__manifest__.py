# -*- coding: utf-8 -*-
{
    'name': "pt_alert_cheque",
    'version': '18.0',
    'category': 'Uncategorized',
    'summary': "Custom module for creating alert for post upcoming cheque dates.",
    'description':'Custom module for creating alert for post upcoming cheque dates.',
    'author': "Prompt Tech",

    'company': "Prompt Tech",
    'maintainer': "Prompt Tech",
    'website': "https://prompttechsolutions.com/",

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'mail'],

    # always loaded
    'data': [
        'data/scheduled_action.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],

}

