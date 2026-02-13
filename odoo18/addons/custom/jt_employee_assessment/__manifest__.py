{
    'name': 'Employee Assessment',
    'summary': 'Employee Assessment Management System',
    'version': '18.0.1.0.0',
    'category': 'hr',
    'author': 'Jupical Technologies Pvt. Ltd.',
    'maintainer': 'Jupical Technologies Pvt. Ltd.',
    'contributors': ['Anil Kesariya <anil.r.kesariya@gmail.com>'],
    'website': 'https://www.jupical.io',
    'live_test_url': 'http://jupical.com/contactus',
    'depends': ['base', 'hr', 'web'],
    'data': [
        'security/hr_employee_security.xml',
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'data/sequence.xml',
        'views/assessment_parameter_view.xml',
        'views/assessment_store.xml',
        'views/hr_employee_view.xml',
        'views/hr_assessment_view.xml',
        'report/employee_assessment_report.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'jt_employee_assessment/static/scss/tree_style.scss',
        ],
    },

    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'images': ['static/description/poster_image.gif'],
    'price': 30.00,
    'currency': 'EUR',
}
