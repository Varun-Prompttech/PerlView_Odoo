# -*- coding: utf-8 -*-
{
    'name': 'Prompttech Walkers Z Report',
    'version': '18.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Prompttech Walkers Z Report',
    'description': 'Prompttech Walkers Z Report',
    'author': 'Prompttech Global',
    'company': 'Prompttech Global',
    'maintainer': 'Prompttech Global',
    'depends': ['base','point_of_sale','sale','product'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/z_report.xml',
        'report/template.xml',
        'wizard/fast_moving_product_wizard.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'pt_walkers_z_report/static/src/css/style.css',
            'pt_walkers_z_report/static/src/js/z_report_preview.js',
        ],
    },

    'license': 'LGPL-3',
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
