import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    WS_AUTH = os.environ.get('WS_AUTH') or 'no-password'