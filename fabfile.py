import os

from fabric.api import env, cd, run, settings, local
from fabric.context_managers import prefix
from fabric.colors import green, red, yellow
from fabric.contrib.console import confirm
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project
from fabric.utils import abort


def _project_dir():
    return os.path.realpath(os.path.dirname(__file__))


def _get_env():
    p_dir = _project_dir()
    ci_path = os.path.join(p_dir, '.env')
    dev_path = os.path.join(p_dir, '..', '.venv_helix')
    if os.path.exists(ci_path):
        return ci_path
    elif os.path.exists(dev_path):
        return dev_path
    else:
        print red('Environment not found')


print green('Configuring production environment')
env.hosts = ['hostinghost']
env.activate = '. %s/bin/activate' % _get_env()
env.remote_dir = '/home/helixauth/project/helixauth-malina/'
env.remote_project_env = os.path.join(env.remote_dir, '.env', 'bin')
#env.remote_virtualenv = '/home/irs/bin/virtualenv'
#env.remote_uwsgi = '/export/home/irs/bin/uwsgi'
env.rsync_exclude = ['*.pyc', '.env', 'log', '.settings', '.*',
    'fabfile.py', '*.sh', 'uwsgi/uwsgi_test.xml']
print green('Production environment configured')


def run_tests():
    with prefix(env.activate):
        print green('Starting tests')
        with settings(warn_only=True):
            t_run = os.path.join(_get_env(), 'bin', 'nosetests')
            result = local('%s %s' % (t_run, _project_dir()))
        if result.failed and not confirm(red('Tests failed. Continue anyway?')):
            print red("Aborting at user request.")
            abort()
        print green('Tests passed')


def sync():
    print green('Files syncronization started')
    print green('Project dir creation')
    run('mkdir -p %s' % env.remote_dir)

    print green('Project files syncronization')
    rsync_project(env.remote_dir, local_dir='%s/' % _project_dir(),
        exclude=env.rsync_exclude, delete=True, extra_opts='-q')

    r_log_dir = os.path.join(env.remote_dir, 'log')
    if not exists(r_log_dir):
        print green('Log directory creation')
        run('mkdir -p %s' % r_log_dir)

    print green('Files syncronization complete')


def config_virt_env():
    r_env_dir = os.path.join(env.remote_dir, '.env')
    if not exists(r_env_dir):
        print green('Virtualenv creation')
        run('%s --no-site-packages %s' %
            (env.remote_virtualenv, r_env_dir))

    print green('Installing packages')
    r_pip = os.path.join(env.remote_dir, '.env', 'bin', 'pip')
    with settings(warn_only=True):
        print green('Removing helixcore')
        run('%s uninstall --yes helixcore' % r_pip)

    print green('Workaround with uwsgi')
    r_uwsgi_dst = os.path.join(r_env_dir, 'bin', 'uwsgi')
    run('ln -sf %s %s' % (env.remote_uwsgi, r_uwsgi_dst))

    print green('Installing requires')
    run('%s install -r %s/pip-requirements.txt' % (r_pip, env.remote_dir))


def update_db():
    print green('Installing db packages')

    run('export PYTHONPATH="%s/src" && %s/python %s/src/helixauth_install update' %
        (env.remote_dir, env.remote_project_env, env.remote_dir))
    print green('Db packages installed')


def restart_uwsgi():
    print green('Restarting uwsgi')
    run('touch %s/uwsgi/uwsgi.xml' % env.remote_dir)
    print green('Uwsgi restarted')


def deploy():
    print yellow('Welcome back, commander!')
    print green('Deployment started')
    run_tests()
    sync()
    config_virt_env()
    update_db()
    restart_uwsgi()
    print green('Deployment complete')
