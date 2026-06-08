{
    'name': 'Parking Management',
    'version': '1.0',
    'depends': ['base'],
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_menus.xml',
        'views/reservation_wizard_views.xml',
    ],
    'installable': True,
}