import os

from fabric.api import env, run
from fabric.colors import green, red, yellow
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project
from fabric.context_managers import prefix
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
env.r_proj_dir = '/opt/helixproject'
env.r_proj_dir_owner = 'root'
env.r_proj_dir_group = 'helixproject'
env.r_proj_dir_perms = '750'

env.r_app_dir = os.path.join(env.r_proj_dir, 'helixauth')
env.r_app_activate = '%s/.env/bin/activate' % env.r_app_dir

#env.remote_uwsgi = '~/opt/bin/uwsgi'
#env.rsync_exclude = ['.*', '*.sh', '*.pyc',
#    'reports', 'fabfile.py', 'requirements-ci.txt',
#    'uwsgi/*_ci.*']
print green("Production environment configured")


def config_virt_env():
    r_env_dir = os.path.join(env.remote_dir, '.env')
    if not exists(r_env_dir):
        print green('Virtualenv creation')
        run('virtualenv %s' % r_env_dir)

    print green('Installing packages')
    r_pip = os.path.join(env.remote_dir, '.env', 'bin', 'pip')

    print green("Workaround with uwsgi")
    r_uwsgi_dst = os.path.join(r_env_dir, 'bin', 'uwsgi')
    run('ln -sf %s %s' % (env.remote_uwsgi, r_uwsgi_dst))

    print green('Installing requires')
    run('%s install -r %s/requirements.txt' % (r_pip, env.remote_dir))


def collectstatic():
    print green('Collecting static')
    with prefix('. %s' % env.remote_activate):
        manage_p = os.path.join(env.remote_dir, 'manage.py')
        cmd = '%s collectstatic --noinput --settings=msite.settings_prod' % manage_p
        run(cmd)
    print green('Static collected')


def _check_rd_owner(rd, owner_exp):
    owner_act = run('stat -c %%U %s' % rd)
    if owner_act != owner_exp:
        abort(red("Owner of %s is %s. Expected %s" % (
            rd, owner_act, owner_exp)))


def _check_rd_group(rd, group_exp):
    group_act = run('stat -c %%G %s' % rd)
    if group_act != group_exp:
        abort(red("Group of %s is %s. Expected %s" % (
            rd, group_act, group_exp)))

def _check_rd_perms(rd, perms_exp):
    perms_act = run('stat -c %%a %s' % rd)
    if perms_act != perms_exp:
        abort(red("Permissions of %s is %s. Expected %s" % (
            rd, perms_act, perms_exp)))


def check_proj_dirs():
    print green("Checking project dir is created")
    if exists(env.r_proj_dir):
        _check_rd_owner(env.r_proj_dir, env.r_proj_dir_owner)
        _check_rd_group(env.r_proj_dir, env.r_proj_dir_group)
        _check_rd_perms(env.r_proj_dir, env.r_proj_dir_perms)
        print green("ok")
    else:
        abort(red("Directory %s is not exists" % env.remote_project_dir))
    abort(yellow("Stopped"))


def sync():
    print green("Files syncronization started")
    print green("Project files syncronization")
    rsync_project(env.remote_dir, local_dir='%s/' % _project_dir(),
        exclude=env.rsync_exclude, delete=True, extra_opts='-q -L')
    run('chmod 700 %s' % env.r88888888emote_dir)
    run('mkdir -p %s' % os.path.join(env.remote_dir, 'log'))
    print green("Files syncronization complete")


def restart_uwsgi():
    print green('Restarting uwsgi')
    run('touch %s/uwsgi/uwsgi.xml' % env.remote_dir)
    print green('Uwsgi restarted')


def deploy():
    print yellow("Welcome back, commander!")
    print green("Deployment started")
    sync()
    config_virt_env()
    collectstatic()
    restart_uwsgi()
    print green("Deployment complete")
