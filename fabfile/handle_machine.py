import os.path
from getpass import getpass
from io import BytesIO

from fabric.api import sudo, run, cd, prefix, settings, task, env, put, prompt, shell_env
from fabric.contrib.console import confirm


def install_python():
    sudo('apt-get update')
    sudo('apt-get install python3-pip python3-dev python3-venv')


def get_sources(repository_url, code_directory):
    with settings(warn_only=True):
        source_existence_check = run('test -d %s' % code_directory)
    if source_existence_check.succeeded:
        if not confirm('Code directory already exists. Remove it?'):
            print('Skipping git clone.')
            return
        sudo('rm -rf %s' % code_directory)
    sudo('git clone %s %s' % (repository_url, code_directory))


def setup_venv(code_directory):
    venv_folder = 'venv'
    with cd(code_directory):
        sudo('python3 -m venv %s' % venv_folder)
    return os.path.join(code_directory, venv_folder, 'bin')


def install_modules(code_directory, venv_bin_directory):
    requirements_path = os.path.join(code_directory, 'requirements.txt')
    venv_activate_path = os.path.join(venv_bin_directory, 'activate')
    with prefix('source %s' % venv_activate_path):
        sudo('pip install wheel')
        sudo('pip install -r %s' % requirements_path)


def install_nginx():
    sudo('apt-get update')
    sudo('apt-get install nginx')
    run('echo "0 */12 * * * systemctl restart nginx" | sudo tee --append /etc/crontab')


def install_postgres():
    sudo('apt-get update')
    sudo('apt-get install postgresql postgresql-contrib')


def setup_ufw():
    sudo('ufw allow "Nginx Full"')
    sudo('ufw allow OpenSSH')
    sudo('ufw enable')


def setup_postgres(username, database_name):
    with settings(warn_only=True):
        run('sudo -u postgres createuser %s -s' % username)
        run('sudo -u postgres createdb %s' % database_name)
    return 'postgresql://%s@/%s' % (username, database_name)


def load_text_from_file(filepath):
    with open(filepath) as text_file:
        return text_file.read()


def put_formatted_template_on_server(template, destination_file_path, **kwargs):
    formatted_template = template.format(**kwargs)
    put(BytesIO(formatted_template.encode('utf-8')), destination_file_path, use_sudo=True)


def create_dhparam_if_necessary(dhparam_path):
    with settings(warn_only=True):
        dhparam_existence_check = run('test -f %s' % dhparam_path)
    if dhparam_existence_check.succeeded:
        print('dhparam file exists, skipping this step')
        return
    sudo('openssl dhparam -out %s 2048' % dhparam_path)


def configure_letsencrypt():
    sudo("mkdir -p /tmp/git")
    sudo("rm -rf /tmp/git/letsencrypt")
    with cd("/tmp/git"):
        sudo("git clone https://github.com/letsencrypt/letsencrypt")
    with cd("/tmp/git/letsencrypt"):
        run('./letsencrypt-auto certonly --standalone')
    sudo('rm -rf /tmp/git')


def start_uwsgi(uwsgi_service_name):
    sudo('systemctl daemon-reload')
    sudo('systemctl restart %s' % uwsgi_service_name)


def start_nginx():
    sudo('systemctl restart nginx')


def run_setup_scripts(access_token, database_url, venv_bin_directory, code_directory):
    environ_params = {
        'ACCESS_TOKEN': access_token,
        'DATABASE_URL': database_url,
        'PAGE_ID': '1',  # this and the following are needed just to avoid syntax errors
        'APP_ID': '1',
        'VERIFY_TOKEN': '1',
    }
    venv_activate_path = os.path.join(venv_bin_directory, 'activate')
    venv_activate_command = 'source %s' % venv_activate_path
    with cd(code_directory), shell_env(**environ_params), prefix(venv_activate_command):
        run('python3 %s/database_setup.py' % code_directory)
        run('python3 %s/set_start_button.py' % code_directory)


@task
def prepare_machine():
    install_python()
    repository_url = 'https://github.com/Stark-Mountain/meetup-facebook-bot.git'
    code_directory = '/var/www/meetup-facebook-bot'
    get_sources(repository_url, code_directory)
    venv_bin_directory = setup_venv(code_directory)
    install_modules(code_directory, venv_bin_directory)

    install_nginx()
    install_postgres()
    setup_ufw()

    database_url = setup_postgres(username=env.user, database_name=env.user)
    access_token = getpass('Enter the app ACCESS_TOKEN: ')
    socket_path = '/tmp/meetup-facebook-bot.socket'
    ini_file_path = os.path.join(code_directory, 'meetup-facebook-bot.ini')
    put_formatted_template_on_server(
        template=load_text_from_file('fabfile/templates/meetup-facebook-bot.ini'),
        destination_file_path=ini_file_path,
        database_url=database_url,
        access_token=access_token,
        page_id=prompt('Enter PAGE_ID:'),
        app_id=prompt('Enter APP_ID:'),
        verify_token=getpass('Enter VERIFY_TOKEN: '),
        socket_path=socket_path
    )

    uwsgi_service_name = 'meetup-facebook-bot.service'
    put_formatted_template_on_server(
        template=load_text_from_file('fabfile/templates/meetup-facebook-bot.service'),
        destination_file_path=os.path.join('/etc/systemd/system/', uwsgi_service_name),
        user=env.user,
        work_dir=code_directory,
        env_bin_dir=venv_bin_directory,
        uwsgi_path=os.path.join(venv_bin_directory, 'uwsgi'),
        app_ini_path=ini_file_path
    )

    dhparam_path = '/etc/ssl/certs/dhparam.pem'
    create_dhparam_if_necessary(dhparam_path)
    ssl_params_path = '/etc/nginx/snippets/ssl-params.conf'
    put_formatted_template_on_server(
        template=load_text_from_file('fabfile/templates/ssl_params'),
        destination_file_path=ssl_params_path,
        dhparam_path=dhparam_path
    )
    configure_letsencrypt()
    letsnecrypt_folder = prompt('What\'s your letsencrypt directory? '
                                '(e.g. /etc/letsencrypt/live/example.com, see above)')
    print('Got it, it\'s %s' % letsnecrypt_folder)

    domain_name = prompt('Enter your domain name:', default='meetup_facebook_bot')
    nginx_config_path = os.path.join('/etc/nginx/sites-available', domain_name)
    put_formatted_template_on_server(
        template=load_text_from_file('fabfile/templates/nginx_config'),
        destination_file_path=nginx_config_path,
        source_dir=code_directory,
        domain=domain_name,
        ssl_params_path=ssl_params_path,
        fullchain_path=os.path.join(letsnecrypt_folder, 'fullchain.pem'),
        privkey_path=os.path.join(letsnecrypt_folder, 'privkey.pem'),
        socket_path=socket_path
    )
    nginx_config_alias = os.path.join('/etc/nginx/sites-enabled', domain_name)
    sudo('ln -sf %s %s' % (nginx_config_path, nginx_config_alias))

    start_uwsgi(uwsgi_service_name)
    start_nginx()
    run_setup_scripts(access_token, database_url, venv_bin_directory, code_directory)