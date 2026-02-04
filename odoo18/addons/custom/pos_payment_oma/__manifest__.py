# -*- coding: utf-8 -*-
{
    'name': 'POS Payment - OMA Integration',
    'version': '18.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'OMA Payment Terminal Integration for Kiosk',
    'description': """
        Integrates OMA payment terminal with Odoo Point of Sale Kiosk.
        
        Features:
        - OMA payment terminal option in Payment Methods
        - "Pay by Card" button in Kiosk when OMA terminal is configured
        - Timer screen while waiting for ECR terminal response
        - Automatic payment processing via OMA ECR API
        - Automatic order completion on successful payment
    """,
    'author': 'Prompttech',
    'website': 'https://www.prompttech.ai',
    'depends': ['point_of_sale', 'pos_self_order'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_payment_method_views.xml',
        'views/oma_transaction_log_views.xml',
        'data/pos_payment_data.xml',
    ],
    'assets': {
        'pos_self_order.assets': [
            'pos_payment_oma/static/src/app/self_order_service.js',
            'pos_payment_oma/static/src/app/components/order_widget/order_widget.js',
            'pos_payment_oma/static/src/app/pages/payment_page/payment_page.js',
            'pos_payment_oma/static/src/app/pages/payment_page/payment_page.xml',
            'pos_payment_oma/static/src/app/pages/payment_page/payment_page.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
