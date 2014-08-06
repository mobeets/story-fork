import os
CURDIR = os.path.dirname(os.path.abspath(__file__))
ROOTDIR = os.path.abspath(os.path.join(CURDIR, '..'))

"""
Need to add things here, like morse_gen's OUTDIR, and elsewhere's MEDIADIR
"""

settings = {
    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': int(os.environ.get('PORT', '5000')),
        'server.environment': 'development',
    },
}

root_settings = {
    '/': {
        'tools.staticdir.root': ROOTDIR,
    },
    '/favicon.ico': {
        'tools.staticfile.on': True,
        'tools.staticfile.filename': os.path.join(ROOTDIR, 'static', 'favicon.ico')
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': 'static'
    },
    '/media': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': 'media'
    },
}

morse_gen_settings = {
    'dbfile': os.path.join(ROOTDIR, 'db', 'morse_gen.db'),
    'exec_path': os.path.join(ROOTDIR, 'apps', 'morse_gen', 'morse_wav_gen.py'),
    'media_dir': 'media/morse_gen'
}

story_fork_settings = {
    'dbfile': os.path.join(ROOTDIR, 'db', 'story_fork.db'),
}

elsewhere_settings = {
    'media_dir': 'media',
    'abs_media_dir': os.path.join(ROOTDIR, 'media'),
    'data_dir': os.path.join(ROOTDIR, 'static', 'elsewhere-data.csv'),
}

unfulfilled_settings = {
    'media_dir': 'media/unfulfilled',
    'abs_media_dir': os.path.join(ROOTDIR, 'media', 'unfulfilled')
}

pdf_helper_settings = {
    'media_dir': 'media/tmp',
    'full_media_dir': os.path.join(ROOTDIR, 'media', 'tmp'),
    'exe_path': os.path.join(ROOTDIR, 'apps', 'pdf_booklet', 'pdf_booklet.py')
}
