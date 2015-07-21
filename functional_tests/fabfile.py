from os import environ

from fabric.api import env, run, prefix
from fabric.context_managers import shell_env

assert 'STAGING_DB' in environ, "STAGING_DB not set"
assert 'STAGING_DB_USERNAME' in environ, "STAGING_DB_USERNAME not set"
assert 'STAGING_DB_PASSWORD' in environ, "STAGING_DB_PASSWORD not set"

def _get_base_folder(host):
    return '~/sites/' + host

def _get_manage_dot_py(host):
    return '{path}/virtualenv/bin/python {path}/source/manage.py'.format(
        path=_get_base_folder(host)
    )

def reset_database():
    with shell_env(SUPERLISTS_DB=environ['STAGING_DB'],
                   SUPERLISTS_DB_USERNAME=environ['STAGING_DB_USERNAME'],
                   SUPERLISTS_DB_PASSWORD=environ['STAGING_DB_PASSWORD']):
        run('{manage_py} flush --noinput'.format(
            manage_py=_get_manage_dot_py(env.host)
        ))

def create_session_on_server(email):
    with shell_env(SUPERLISTS_DB=environ['STAGING_DB'],
                   SUPERLISTS_DB_USERNAME=environ['STAGING_DB_USERNAME'],
                   SUPERLISTS_DB_PASSWORD=environ['STAGING_DB_PASSWORD']):
        session_key = run('{manage_py} create_session {email}'.format(
            manage_py=_get_manage_dot_py(env.host),
            email=email,
        ))
        print(session_key)