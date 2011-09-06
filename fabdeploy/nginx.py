from fabric.api import sudo, settings

from fabdeploy.containers import conf
from fabdeploy.task import Task
from fabdeploy.utils import upload_config_template
from fabdeploy import system


__all__ = ['install', 'restart', 'push_apache_config',
           'push_gunicorn_config', 'push_uwsgi_config']


class Install(Task):
    def do(self):
        options = {'lenny': '-t lenny-backports'}
        system.aptitude_install.run(packages='nginx',
                                    options=options.get(self.conf.os, ''))
        sudo('rm --force /etc/nginx/sites-enabled/default')

install = Install()


class PushConfigTask(Task):
    @conf
    def config(self):
        return '/etc/nginx/sites-available/%(instance_name)s' % self.conf

    @conf
    def enabled_config(self):
        return '/etc/nginx/sites-enabled/%(instance_name)s' % self.conf

    def do(self):
        upload_config_template(self.conf.config_template, self.conf.config,
            context=self.conf, use_sudo=True)
        with settings(warn_only=True):
            sudo('ln --symbolic %(config)s %(enabled_config)s' % self.conf)


class PushApacheConfig(PushConfigTask):
    @conf
    def config_template(self):
        return 'nginx_apache.config'

push_apache_config = PushApacheConfig()


class PushGunicornConfig(PushConfigTask):
    @conf
    def config_template(self):
        return 'nginx_gunicorn.config'

push_gunicorn_config = PushGunicornConfig()


class PushUwsgiConfig(PushConfigTask):
    @conf
    def config_template(Task):
        return 'nginx_uwsgi.config'

push_uwsgi_config = PushUwsgiConfig()


class Restart(Task):
    def do(self):
        sudo('invoke-rc.d nginx restart')

restart = Restart()
