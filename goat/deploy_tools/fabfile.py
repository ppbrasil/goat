from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run
import random
import os

REPO_URL = 'https://github.com/ppbrasil/goat'
#local_key_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + 'keys'
#key_name = 'ppbrasil-20170831.pem'
#aws_user = 'ubuntu'

def deploy(site):
    site_folder = '/home/{}/sites/{}'.format(env.user, site)
    source_folder = site_folder + '/source'
    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _update_settings(source_folder, env.host)
    _update_virtualenv(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)


def _create_directory_structure_if_necessary(site_folder):
        for subfolder in ('virtualenv', 'source'):
            run('mkdir -p {}/{}'.format(site_folder,subfolder))

def _get_latest_source(source_folder):
    if exists(source_folder + './git'):
        run('cd {} && git fetch'.format(source_folder))
    else:
        run('git clone {} {}'.format(REPO_URL, source_folder))
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('cd {} && git reset --hard {}'.format(source_folder, current_commit))

def _update_settings(source_folder, site_name):
    settings_path = source_folder + '/source/goat/goat/settings.py'
    sed(settings_path, "DEBUG = True", "DEBUG = False")
    sed(settings_path,
        'ALLOWED_HOSTS =.+$',
        'ALLOWED_HOSTS = ["{}"]'.format(site_name)
        )
    secret_key_file = source_folder + '/goat/secret_key.py'
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, 'SECRET_KEY = {}'.format(key))
    append(settings_path, '\nfrom .secret_key import SECRET_KEY')

def _update_virtualenv(source_folder):
    virtualenv_folder = source_folder + '/../virtualenv'
    if not exists(virtualenv_folder + 'bin/pip'):
        run('python3.6 -m venv {}'.format(virtualenv_folder))
    run('{}/bin/pip install -r {}/requirements.txt'.format, virtualenv_folder, source_folder)

def _update_static_files(source_folder):
    run(
        'cd {}/goat && ../virtualenv/bin/python manage.py colectstatic --noinput'.format(source_folder)
    )

def _update_database(source_folder):
    run(
        'cd {}/goat && ../virtualenv/bin/python manage.py migrate --noinput'.format(source_folder)
    )