{
    'name': 'Approvals Private Note',
    'author': 'Approvals',
    'version': '17.0.1.0.0',
    'category': 'Human Resources/Approvals',
    'summary': 'Private notes on approval requests, visible only to the author and mentioned users',
    'depends': ['approvals'],
    'assets': {
        'web.assets_backend': [
            'approvals_private_note/static/src/**/*',
        ],
    },
    'data': [
        'views/mail_message_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
