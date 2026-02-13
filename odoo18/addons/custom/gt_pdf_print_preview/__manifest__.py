# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Pdf Viewer",
    "version": "18.0.3.1",
    "category": "General",
    "summary": "Our app offers effortless PDF preview for single or multiple records, providing clear and comprehensive previews",
    "description": "Experience streamlined PDF previews in our app. With a single click for a single record or when selecting multiple records, users can effortlessly access clear and comprehensive previews, ensuring a smooth and informed printing process",
    "author": "GritXi Technologies Pvt. Ltd.",
    "company": "GritXi Technologies Pvt. Ltd.",
    "maintainer": "GritXi Technologies Pvt. Ltd.",
    "website": "https://www.gritxi-tech.com",
    "sequence": 1000,
    "depends": ["web"],
    "images": ["static/description/banner.jpg"],
    "data": [
        "views/res_users_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "gt_pdf_print_preview/static/xml/website_views.xml",
            "gt_pdf_print_preview/static/src/webclient/actions/reports/utils.js",
            "gt_pdf_print_preview/static/src/webclient/actions/action_service.js",
            "gt_pdf_print_preview/static/src/search/action_menus/action_menus.js",
        ],
    },
    "price": 24,
    "currency": "USD",
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "OPL-1",
}
