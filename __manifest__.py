# -*- coding: utf-8 -*-
{
    'name': 'Project Management (CSL)',
    'version': '17.0.1.0.0',
    'summary': 'Custom Project Management Form',
    'description': """
        This module adds a custom project management form with specific notebook pages
        and user groups.
        - Adds Scope of Work configuration.
        - Links Projects to Quotations, Invoices, and Purchase Orders.
    """,
    'category': 'Services/Project',
    'author': 'Concept Solutions ',
    'website': 'https://www.csloman.com',
    'depends': [
        'base', 
        'mail', 
        'base_setup',
        'sale_management',
        'account',
        'purchase',
        'hr'
    ],
    'data': [
        'security/project_management_security.xml',
        'security/ir.model.access.csv',
        
        'views/scope_work_views.xml',
        'views/project_csl_views.xml',
        'views/project_csl_menus.xml',
        'views/res_users_views.xml', 
        'views/project_ref_sales.xml', 
        'views/account_move_views.xml',
        'views/purchase_order_views.xml',

        'data/project_sequence.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}