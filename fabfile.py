import os

from fabric.api import env, run, local
from fabric.colors import green, red, yellow
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project
from fabric.context_managers import prefix, settings
from fabric.utils import abort


def _project_dir():
    return os.path.realpath(os.path.dirname(__file__))


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
env.proj_dir = os.path.join(env.proj_root_dir, 'helixauth')
env.proj_dir_owner = 'helixauth'
env.proj_dir_group = 'helixproject'
env.proj_dir_perms = '750'
env.activate = '. %s/bin/activate' % _get_env()
env.pythonpath = 'export PYTHONPATH="%s:%s"' % (_project_dir(),
    os.path.join(_project_dir(), '..', 'helixcore', 'src'))
env.rsync_exclude = ['.*', '*.log*', '*.sh', '*.pyc',
    'fabfile.py', 'pip-requirements-dev.txt',
    'uwsgi/*_dev.*']
print green("Production environment configured")


def config_virt_env():
    proj_env_dir = os.path.join(env.proj_dir, '.env')
    if not exists(proj_env_dir):
        print green('Virtualenv creation')
        run('virtualenv %s --no-site-packages' % proj_env_dir)

    print green('Installing packages')
    proj_pip = os.path.join(env.proj_dir, '.env', 'bin', 'pip')

    print green('Installing requires')
    run('%s install -r %s/pip-requirements.txt' % (proj_pip, env.proj_dir))


def _check_rd(rd, o_exp, g_exp, p_exp):
    if exists(rd):
        res = run('stat -c %%U,%%G,%%a %s' % rd)
        o_act, g_act, p_act = map(str.strip, res.split(','))
        if o_act != o_exp or g_act != g_exp or p_act != p_exp:
            abort(red("Directory %s params: %s. Expected: %s" % (
                rd, (o_act, g_act, p_act), (o_exp, g_exp, p_exp))))
        print green("Directory %s checking passed" % rd)
    else:
        abort(red("Directory %s is not exists" % env.proj_dir))


def _fix_rd(rd, o, g, p):
    print green("Setting project directory parameters")
    run('chown %s:%s %s' % (o, g, rd))
    run('chmod %s %s' % (p, rd))
    print green("Checking project directory parameters")


def sync():
    _check_rd(env.proj_root_dir, env.proj_dir_owner,
        env.proj_dir_group, env.proj_dir_perms)

    print green("Files synchronization started")
    print green("Project files synchronization")
    print green("Files synchronization complete")
    rsync_project(env.proj_dir, local_dir='%s/' % _project_dir(),
        exclude=env.rsync_exclude, delete=True, extra_opts='-q -L')
    _fix_rd(env.proj_dir, env.proj_dir_owner,
        env.proj_dir_group, env.proj_dir_perms)
    _check_rd(env.proj_dir, env.proj_dir_owner,
        env.proj_dir_group, env.proj_dir_perms)
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
    with prefix(env.pythonpath):
        print green("Starting tests")
        with settings(warn_only=True):
            t_run = os.path.join(_get_env(), 'bin', 'nosetests')
            t_dir = os.path.join(_project_dir(), 'src', 'helixauth', 'test')
            result = local('%s %s' % (t_run, t_dir))
        if result.failed:
            abort(red("Tests failed"))
        else:
            print green("Tests passed")


def deploy():
    print yellow("Welcome back, commander!")
    print green("Deployment started")
    run_tests()
    deploy_helixcore()
    sync()
    config_virt_env()
    restart_uwsgi()
    print green("Deployment complete")
