# -*- coding: utf-8 -*-
{
    'name': 'Base Extensions',
    'version': '18.0.1.0.0',
    'summary': 'Core company-wide Odoo customizations',
    'category': 'Tools',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'OPL-1',
    'depends': ['base', 'web'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/base_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'description': """
Core Customizations
===================
This module contains common utilities, mixins, and base field extensions 
used across other custom modules.
""",
}
