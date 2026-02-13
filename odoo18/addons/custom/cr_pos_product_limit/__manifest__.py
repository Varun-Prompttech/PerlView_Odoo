# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': "Pos Product Limit and All Product Loading",
    'summary': "Adds limited product loading with optional background loading in POS.",
    'description': """
        This module adds two configuration options to the POS settings:
        1) Limited Product Loading: When enabled, the POS loads only a limited number of products at startup, improving loading speed and performance.
        2) Load All Remaining Products in Background: When this is also enabled, the remaining products are automatically loaded in the background without interrupting POS usage.
    """,
    'author': "Candidroot Solution Pvt. Ltd.",
    'website': "https://candidroot.com",
    'license': 'LGPL-3',
    'category': 'Sales/Point Of Sale',
    'version': '18.0.0.0',
    'depends': ['base','point_of_sale'],
    'data': [
        'views/pos_config_views.xml'
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'cr_pos_product_limit/static/src/js/load_products.js'
        ]
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
}