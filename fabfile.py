from getpass import getpass
from io import StringIO

from fabric.api import settings, local, abort, run, cd, env,\
    prefix, sudo, prompt, put, shell_env, task
from fabric.contrib.console import confirm 

# these can have arbitrary values
env.sources_directory = '/var/www/meetup-facebook-bot'
env.socket_path = '/tmp/meetup-facebook-bot.socket'
env.app_ini_filepath = '%s/meetup-facebook-bot.ini' % env.sources_directory
env.uwsgi_service_file_name = 'meetup_facebook_bot.service'
env.ssl_params_path = '/etc/nginx/snippets/ssl-params.conf'

# these are are not arbitrary
env.venv_folder = 'venv'
env.venv_directory = '%s/%s' % (env.sources_directory, env.venv_folder)
env.venv_activate_command = 'source %s/bin/activate' % env.venv_directory

# these will be set later
DATABASE_URL = None
ACCESS_TOKEN = None


def install_python():
    sudo('apt-get update')
    sudo('apt-get install python3-pip python3-dev python3-venv')


def get_sources():
    repository_url = 'https://github.com/Stark-Mountain/meetup-facebook-bot.git'  
    with settings(warn_only=True):
        source_existence_check = run('test -d %s' % env.sources_directory)
    if source_existence_check.succeeded:
        print('The sources alrady exist. We\'ll remove them before cloning.')
        sudo('rm -rf %s' % env.sources_directory)
    sudo('git clone %s %s' % (repository_url, env.sources_directory))


def setup_venv():
    with cd(env.sources_directory):
        sudo('python3 -m venv %s' % env.venv_folder)


def install_modules():
    requirements_path = '%s/requirements.txt' % env.sources_directory
    with prefix(env.venv_activate_command):
        sudo('pip install wheel')
        sudo('pip install -r %s' % requirements_path)


def prepare_sources():
    get_sources()
    setup_venv()
    install_modules()


def install_nginx():
    sudo('apt-get update')
    sudo('apt-get install nginx')
    run('echo "0 */12 * * * systemctl restart nginx" | sudo tee --append /etc/crontab')


def install_database():
    sudo('apt-get update')
    sudo('apt-get install postgresql postgresql-contrib')


def setup_database():
    db_username = env.user
    db_name = env.user
    with settings(warn_only=True):
        run('sudo -u postgres createuser %s -s' % db_username)
        run('sudo -u postgres createdb %s' % db_name)
    global DATABASE_URL
    DATABASE_URL = 'postgresql://%s@/%s' % (db_username, db_name)

def setup_firewall():
    sudo('ufw allow "Nginx Full"')
    sudo('ufw allow OpenSSH')
    sudo('ufw enable')


def create_ini_file():
    global DATABASE_URL
    if not DATABASE_URL:
        DATABASE_URL = prompt('Enter DATABASE_URL:')
    global ACCESS_TOKEN
    ACCESS_TOKEN = getpass('Enter ACCESS_TOKEN:')
    page_id = prompt('Enter PAGE_ID:')
    app_id = prompt('Enter APP_ID:')
    verify_token = getpass('Enter VERIFY_TOKEN:')
    put(StringIO(
u'''[uwsgi]
env = DATABASE_URL={db_url}
env = ACCESS_TOKEN={access_token}
env = PAGE_ID={page_id}
env = APP_ID={app_id}
env = VERIFY_TOKEN={verify_token}

module = wsgi:app
master = true
processes = 4
socket = {socket_path}
chmod-socket = 660
vacuum = true
die-on-term = true'''.format(
                db_url=DATABASE_URL,
                access_token=ACCESS_TOKEN,
                page_id=page_id,
                app_id=app_id,
                verify_token=verify_token,
                socket_path=env.socket_path
            )
        ), 
        env.app_ini_filepath,
        use_sudo=True
    )


def create_uwsgi_service_file():
    put(StringIO(
u'''[Unit]
Description=uWSGI instance to serve meetup_facebook_bot
After=network.target

[Service]
User={user}
Group=www-data
WorkingDirectory={work_dir}
Environment="PATH={env_bin_dir}"
ExecStart={uwsgi_path} --ini {app_ini_path}

[Install]
WantedBy=multi-user.target'''.format(
                user=env.user,
                work_dir=env.sources_directory,
                env_bin_dir='%s/bin' % env.venv_directory,
                uwsgi_path = '%s/bin/uwsgi' % env.venv_directory,
                app_ini_path=env.app_ini_filepath
            )
        ),
        '/etc/systemd/system/%s' % env.uwsgi_service_file_name,
        use_sudo=True
    )


def create_ssl_params_file():
    dhparam_path = '/etc/ssl/certs/dhparam.pem'
    with settings(warn_only=True):
        dhparam_existence_check = run('test -f %s' % dhparam_path)
    if dhparam_existence_check.succeeded:
        print('dhparam file exists, skipping this step')
        return;
    sudo('openssl dhparam -out %s 2048' % dhparam_path)
    put(StringIO(
        u'''# from https://cipherli.st/
ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
ssl_prefer_server_ciphers on;
ssl_ciphers "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH";
ssl_ecdh_curve secp384r1;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
# Disable preloading HSTS for now.  You can use the commented out header line that includes
# the "preload" directive if you understand the implications.
#add_header Strict-Transport-Security "max-age=63072000; includeSubdomains; preload";
add_header Strict-Transport-Security "max-age=63072000; includeSubdomains";
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
ssl_dhparam {dhparam_path};'''.format(
                dhparam_path=dhparam_path,
            )
        ),
        env.ssl_params_path,
        use_sudo=True
    )


def remove_trailing_slash_if_present(path):
    return path[:-1] if path[-1] == '/' else path


def configure_letsencrypt():
    sudo("mkdir -p /tmp/git")
    sudo("rm -rf /tmp/git/letsencrypt")
    with cd("/tmp/git"):
        sudo("git clone https://github.com/letsencrypt/letsencrypt")
    with cd("/tmp/git/letsencrypt"):
        run('./letsencrypt-auto certonly --standalone')
    sudo('rm -rf /tmp/git')
    env.letsnecrypt_folder = remove_trailing_slash_if_present(
        prompt('What\'s your letsencrypt directory? (e.g. /etc/letsencrypt/live/example.com, see above)')
    )
    print('OK, it\'s %s' % env.letsnecrypt_folder)
    create_ssl_params_file()


def create_nginx_config():
    configure_letsencrypt()
    domain_name = prompt('Enter your domain name:', default='metup_facebook_bot')
    nginx_config_path = '/etc/nginx/sites-available/%s' % domain_name
    put(StringIO(
        u'''server {{
    listen 80;
    listen [::]:80;

    server_name {domain};
    return 301 https://$server_name$request_uri;
}}

server {{
    listen 443 ssl default_server;
    listen [::]:443 ssl default_server;
    include {ssl_params_path};

    ssl_certificate {fullchain_path};
    ssl_certificate_key {privkey_path};

    root {source_dir};
    index index.html index.htm index.nginx-debian.html;

    location / {{
        include uwsgi_params;
        uwsgi_pass unix:{socket_path};
    }}
}}'''.format(
                source_dir=env.sources_directory,
                domain=domain_name,
                ssl_params_path=env.ssl_params_path,
                fullchain_path='%s/fullchain.pem' % env.letsnecrypt_folder,
                privkey_path='%s/privkey.pem' % env.letsnecrypt_folder,
                socket_path=env.socket_path
            )
        ),
        nginx_config_path,
        use_sudo=True
    )
    nginx_config_alias = '/etc/nginx/sites-enabled/%s' % domain_name
    sudo('ln -sf %s %s' % (nginx_config_path, nginx_config_alias))


def start_uwsgi():
    sudo('systemctl daemon-reload')
    sudo('systemctl restart %s' % env.uwsgi_service_file_name)


def start_nginx():
    sudo('systemctl restart nginx')


def run_setup_scripts():
    global ACCESS_TOKEN
    global DATABASE_URL
    environ_params = {
        'ACCESS_TOKEN': ACCESS_TOKEN,
        'DATABASE_URL': DATABASE_URL,
        'PAGE_ID': '1',  # this and the following are needed just to avoid syntax errors
        'APP_ID': '1',
        'VERIFY_TOKEN': '1',
    }
    with cd(env.sources_directory), shell_env(**environ_params), prefix(env.venv_activate_command):
        run('python3 %s/database_setup.py' % env.sources_directory)
        run('python3 %s/set_start_button.py' % env.sources_directory)


@task
def prepare_machine():
    install_python()
    prepare_sources()
    install_nginx()
    install_database()

    setup_database()
    setup_firewall()

    create_ini_file()
    create_uwsgi_service_file()
    create_nginx_config()

    start_uwsgi()
    start_nginx()
    run_setup_scripts()


def test():
    with settings(warn_only=True):
        result = local('python3 -m pytest tests', capture=True)
    if result.failed and not confirm('Tests failed. Continue anyway?'):
        abort('Aborting at user request.')


def commit():
    with settings(warn_only=True):
        local('git add -p && git commit')


def push(branch):
    local('git push origin %s' % branch)


@task
def prepare_deploy(branch):
    test()
    commit()
    push(branch)


@task
def deploy(branch='master'):
    with settings(warn_only=True):
        if run('test -d %s' % env.sources_directory).failed:
            abort('run prepare_machine first')
    with cd(env.sources_directory):
        sudo('git fetch origin %s' % branch)
        sudo('git checkout %s' % branch)
        sudo('git merge origin %s' % branch)
        install_modules()
        start_uwsgi()
        start_nginx()
