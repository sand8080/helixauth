import os
import sys

from fabric.api import env, run, local
from fabric.colors import green, red, yellow
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project
from fabric.context_managers import prefix, settings, hide, show
from fabric.utils import abort


def _project_dir():
    return os.path.realpath(os.path.dirname(__file__))


sys.path.append(os.path.join(_project_dir(), '..', 'helixcore', 'src'))
from helixcore.deploy import _fix_r_res, _check_r_res


def _get_env():
    p_dir = _project_dir()
    env_path = os.path.join(p_dir, '.env')
    if os.path.exists(env_path):
        return env_path
    else:
        print red("Environment not found")
        raise Exception("Environment not found")


print green("Configuring production environment")
env.hosts = ['helixauth@78.47.11.201']
env.proj_root_dir = '/opt/helixproject/helixauth'
env.proj_root_dir_owner = 'helixauth'
env.proj_root_dir_group = 'helixproject'
env.proj_root_dir_perms = '750'
env.proj_dir = os.path.join(env.proj_root_dir, 'helixauth')
env.proj_dir_owner = 'helixauth'
env.proj_dir_group = 'helixproject'
env.proj_dir_perms = '700'
env.proj_settings_file_perms = '400'
env.run_dir = os.path.join(env.proj_root_dir, 'run')
env.run_dir_owner = 'helixauth'
env.run_dir_group = 'helixproject'
env.run_dir_perms = '770'
env.proj_pythonpath = 'export PYTHONPATH="%s:%s"' % (
    os.path.join(env.proj_dir, 'src'),
    os.path.join(env.proj_dir, '..', 'helixcore', 'src'))
env.local_pythonpath = 'export PYTHONPATH="%s:%s"' % (_project_dir(),
    os.path.join(_project_dir(), '..', 'helixcore', 'src'))
env.rsync_exclude = ['.*', '*.log*', '*.sh', '*.pyc',
    'fabfile.py', 'pip-requirements-dev.txt',
    'uwsgi/*_dev.*']
env.activate = '. %s/.env/bin/activate' % env.proj_root_dir
print green("Production environment configured")


def config_virt_env():
    proj_env_dir = os.path.join(env.proj_root_dir, '.env')
    if not exists(proj_env_dir):
        print green('Virtualenv creation')
        run('virtualenv %s --no-site-packages' % proj_env_dir)

    with prefix(env.activate):
        print green('Installing required python packages')
        run('pip install -r %s/pip-requirements.txt' % env.proj_dir)


def sync():
    print green("Files synchronization started")
    _check_r_res(env.proj_root_dir, env.proj_root_dir_owner,
        env.proj_root_dir_group, env.proj_root_dir_perms)

    print green("Project files synchronization")
    rsync_project(env.proj_dir, local_dir='%s/' % _project_dir(),
        exclude=env.rsync_exclude, delete=True, extra_opts='-q -L')

    print green("Cleaning files")
    run('find %s -name "*.pyc" -exec rm -f {} \;' % env.proj_dir)

    # project directory
    _fix_r_res(env.proj_dir, env.proj_dir_owner,
        env.proj_dir_group, env.proj_dir_perms)
    _check_r_res(env.proj_dir, env.proj_dir_owner,
        env.proj_dir_group, env.proj_dir_perms)
    # run directory
    run('mkdir -p %s' % env.run_dir)
    _fix_r_res(env.run_dir, env.run_dir_owner,
        env.run_dir_group, env.run_dir_perms)
    _check_r_res(env.run_dir, env.run_dir_owner,
        env.run_dir_group, env.run_dir_perms)
    # settings
    s_f = os.path.join(env.proj_dir, 'src', 'helixauth',
        'conf', 'settings.py')
    _fix_r_res(s_f, env.proj_dir_owner,
        env.proj_dir_group, env.proj_settings_file_perms)
    _check_r_res(s_f, env.proj_dir_owner,
        env.proj_dir_group, env.proj_settings_file_perms)
    print green("Files synchronization complete")


def restart_uwsgi():
    print green('Restarting uwsgi')
    run('touch %s/uwsgi/uwsgi.xml' % env.proj_dir)
    print green('Uwsgi restarted')


def deploy_helixcore():
    print green("Deploying helixcore")
    helixcore_fab = os.path.join(_project_dir(), '..', 'helixcore', 'fabfile.py')
    local_fab = os.path.join(_get_env(), 'bin', 'fab')
    local('%s -f %s sync_helixauth' % (local_fab, helixcore_fab))
    print green("Helixcore deployment finished")


def run_tests():
    with prefix(env.local_pythonpath):
        print green("Starting tests")
        with settings(warn_only=True):
            t_run = os.path.join(_get_env(), 'bin', 'nosetests')
            t_dir = os.path.join(_project_dir(), 'src', 'helixauth', 'test')
            result = local('%s %s' % (t_run, t_dir))
        if result.failed:
            abort(red("Tests failed"))
        else:
            print green("Tests passed")


def install_db_patches():
    with prefix(env.activate):
        with prefix(env.proj_pythonpath):
            with show('stdout'):
                print green("Installing db_patches")
                src = os.path.join(env.proj_dir, 'src', 'install_db_patches.py')
                run('python %s update' % src)


def deploy():
    with hide('running', 'stdout'):
        print yellow("Welcome back, commander!")
        print green("Deployment started")
        run_tests()
        deploy_helixcore()
        sync()
        config_virt_env()
        install_db_patches()
        restart_uwsgi()
        print green("Deployment complete")
        print yellow("Helixauth operational!")
