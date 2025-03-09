{
    'name': 'Real Estate Management',
    'version': '1.0',
    'category': 'Real Estate',
    'summary': 'Manage real estate properties and advertisements',
    'description': """
Real Estate Management
=====================
This module allows you to manage real estate properties including:
- Property listings with detailed information
- Property types and tags
- Property offers and status tracking
- Property image galleries
- Advanced search functionality
    """,
    'author': 'Tinotenda Happy Biningu',
    'website': 'https://tinobiningu.netlify.app',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/real_estate_security.xml',
        'security/ir.model.access.csv',
        'views/property_views.xml',
        'views/property_type_views.xml',
        'views/property_tag_views.xml',
        'views/property_offer_views.xml',
        'views/res_users_views.xml',
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'real_estate/static/src/js/property_kanban.js',
            'real_estate/static/src/scss/real_estate.scss',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
