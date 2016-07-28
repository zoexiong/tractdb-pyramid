import configparser
import invoke
import jinja2
import re
import sys
import tests.docker_base as docker_base
import yaml


def check_result(result, description):
    if result.failed:
        print('========================================')
        print('Failed to {}'.format(description))
        print('')
        print('========================================')
        print('STDOUT:')
        print('========================================')
        print(result.stdout)
        print('========================================')
        print('STDERR:')
        print('========================================')
        print(result.stderr)
        print('========================================')
        raise Exception('Failed to {}'.format(description))


@invoke.task
def update_dependencies():
    # Parameters to keep everything silent
    params_silent = {
        'encoding': sys.stdout.encoding,
        'hide': 'both',
        'warn': True
    }

    # Parse our compile config
    with open('_compile-config.yml') as f:
        compile_config_yaml = yaml.safe_load(f)

    # Python dependencies
    print('Checking Python dependencies')

    # Ensure we have a current version of pip, as needed by pip-tools
    pip_version_desired = compile_config_yaml['config']['local']['python']['pip_version']
    result = invoke.run('pip --disable-pip-version-check show pip', **params_silent)
    check_result(result, 'check pip version')

    pip_version_current = re.search('^Version: ([\d\.]+)', result.stdout, re.MULTILINE).group(1)
    if pip_version_current != pip_version_desired:
        result = invoke.run(
            'python -m pip install --upgrade pip=={}'.format(
                pip_version_desired
            ),
            **params_silent
        )
        check_result(result, 'update pip version')

    # Ensures we have pip-tools, which will be in our requirements file
    # pip-sync also does not respect options in the requirements file,
    # so installing the entire file ensures pip-sync only needs to delete
    result = invoke.run('pip --disable-pip-version-check install -r requirements3.txt', **params_silent)
    check_result(result, 'install pip requirements')
    # Ensure we have exactly our dependencies
    result = invoke.run('pip-sync requirements3.txt', **params_silent)
    check_result(result, 'sync pip requirements')


@invoke.task()
def compile_config():
    # Parse our compile config
    with open('_compile-config.yml') as f:
        compile_config_yaml = yaml.safe_load(f)

    # Compile each jinja2 file
    for jinja2_entry in compile_config_yaml['jinja2']['entries']:
        jinja2_environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(searchpath='.'),
            undefined=jinja2.StrictUndefined
        )
        template = jinja2_environment.get_template(jinja2_entry['in'])
        with open(jinja2_entry['out'], 'w') as f:
            f.write(template.render(compile_config_yaml['config']))


@invoke.task()
def compile_requirements():
    # Compile the requirements file
    invoke.run(
        'pip-compile --upgrade --output-file requirements3.txt requirements3.in',
        encoding=sys.stdout.encoding
    )


@invoke.task()
def docker_machine_console():
    docker_base.machine_console()


@invoke.task()
def docker_machine_ensure():
    docker_base.machine_ensure()


@invoke.task()
def docker_machine_ip():
    print(docker_base.ip())


@invoke.task()
def docker_machine_start():
    docker_base.machine_ensure()
    docker_base.compose_run('tests/test-compose.yml', 'build')
    docker_base.compose_run('tests/test-compose.yml', 'up -d')


@invoke.task()
def docker_machine_stop():
    docker_base.compose_run('tests/test-compose.yml', 'stop')


def _config_combine(list_file_config, file_config_combined):
    # Combine the multiple config files
    config_combined = configparser.ConfigParser()
    for file_config_current in list_file_config:
        config_combined.read(file_config_current)

    with open(file_config_combined, 'w') as f:
        config_combined.write(f)


def _config_localize(file_config_combined, file_config_localized):
    # Compile our configuration into a localized version
    jinja2_environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(searchpath='.'),
        undefined=jinja2.StrictUndefined
    )
    template = jinja2_environment.get_template(file_config_combined)
    with open(file_config_localized, 'w') as f:
        f.write(template.render({
            'DOCKER_IP': docker_base.ip()
        }))


@invoke.task(pre=[update_dependencies, docker_machine_start])
def serve_test():
    _config_combine(
        [
            'pyramid_config.ini',
            'pyramid_config.test.ini'
        ],
        'pyramid_config.combined.ini'
    )
    _config_localize(
        'pyramid_config.combined.ini',
        'pyramid_config.combined.localized.ini'
    )

    invoke.run(
        'python setup.py develop',
        encoding=sys.stdout.encoding
    )
    invoke.run(
        'pserve pyramid_config.combined.localized.ini',
        encoding=sys.stdout.encoding
    )


@invoke.task(pre=[update_dependencies])
def serve_production():
    _config_combine(
        [
            'pyramid_config.ini',
            'pyramid_config.production.ini'
        ],
        'pyramid_config.combined.ini'
    )

    invoke.run(
        'python setup.py develop',
        encoding=sys.stdout.encoding
    )
    invoke.run(
        'pserve pyramid_config.combined.ini',
        encoding=sys.stdout.encoding
    )


@invoke.task
def update_base():
    invoke.run(
        'git pull https://github.com/fogies/testwithdocker-base.git master',
        encoding=sys.stdout.encoding
    )
