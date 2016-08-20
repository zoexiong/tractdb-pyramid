import os
import subprocess
import sys
import yaml


def _check_result(command, result):
    if result.returncode != 0:
        print(
            (
                '========================================\n'
                'Command failed with error code: {}\n'
                '{}'
                '\n'
                '========================================\n'
                'STDOUT:\n'
                '========================================\n'
                '{}'
                '\n'
                '========================================\n'
                'STDERR:\n'
                '========================================\n'
                '{}'
                '\n'
                '========================================\n'
            ).format(
                result.returncode,
                command,
                result.stdout,
                result.stderr
            ),
            file=sys.stderr, flush=True
        )

        raise subprocess.CalledProcessError(
            result.returncode,
            command
        )


def compose_ensure_up(file_compose, service):
    machine_ensure()
    compose_run(file_compose, 'build {}'.format(service))
    compose_run(file_compose, 'up -d {}'.format(service))


def compose_run(file_compose, compose_command, check_result=True):
    # Parse our compile config
    with open('_compile-config.yml') as f:
        compile_config_yaml = yaml.safe_load(f)

    # Assemble our command
    if 'BASE_DOCKER_ON_TRAVIS' in os.environ:
        command = 'docker-compose -f "{}" {}'.format(
            file_compose,
            compose_command
        )
    else:
        command = '"{}" "{}" docker-compose -f "{}" {}'.format(
            compile_config_yaml['config']['local']['docker']['cmd_bash'],
            os.path.normpath(os.path.join(os.getcwd(), 'base/docker-machine/machine_bash.sh')).replace('\\', '/'),
            os.path.normpath(os.path.join(os.getcwd(), file_compose)).replace('\\', '/'),
            compose_command
        )

    # Call the command
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    for line in process.stdout:
        flag_print = line.startswith('Step ')

        if flag_print:
            print(line, end='', flush=True)


def docker_run(docker_command, check_result=True):
    # Parse our compile config
    with open('_compile-config.yml') as f:
        compile_config_yaml = yaml.safe_load(f)

    # Assemble our command
    if 'BASE_DOCKER_ON_TRAVIS' in os.environ:
        command = 'docker {}'.format(
            docker_command
        )
    else:
        command = '"{}" "{}" docker {}'.format(
            compile_config_yaml['config']['local']['docker']['cmd_bash'],
            os.path.normpath(os.path.join(os.getcwd(), 'base/docker-machine/machine_bash.sh')).replace('\\', '/'),
            docker_command
        )

    # Call the command
    result = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if check_result:
        _check_result(command, result)

    return result


def machine_console():
    # Parse our compile config
    with open('_compile-config.yml') as f:
        compile_config_yaml = yaml.safe_load(f)

    # Assemble our command
    command = 'cmd /c start "{}" "{}"'.format(
        compile_config_yaml['config']['local']['docker']['cmd_bash'],
        os.path.normpath(os.path.join(os.getcwd(), 'base/docker-machine/machine_console.sh')).replace('\\', '/')
    )

    # Call the command, noting that this cannot be piped
    subprocess.run(
        command
    )


def machine_ensure():
    # On Travis, docker is already available
    if 'BASE_DOCKER_ON_TRAVIS' in os.environ:
        return

    # Parse our compile config
    with open('_compile-config.yml') as f:
        compile_config_yaml = yaml.safe_load(f)

    # Assemble our command
    command = '"{}" "{}"'.format(
        compile_config_yaml['config']['local']['docker']['cmd_bash'],
        os.path.normpath(os.path.join(os.getcwd(), 'base/docker-machine/machine_ensure.sh')).replace('\\', '/')
    )

    # Call the command
    result = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    _check_result(command, result)


def ip():
    # On Travis, docker is already available
    if 'BASE_DOCKER_ON_TRAVIS' in os.environ:
        return 'localhost'

    # Parse our compile config
    with open('_compile-config.yml') as f:
        compile_config_yaml = yaml.safe_load(f)

    # Assemble our command
    command = '"{}" ip default'.format(
        compile_config_yaml['config']['local']['docker']['cmd_dockermachine']
    )

    # Call the command
    result = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    _check_result(command, result)

    ip_address = result.stdout.decode('utf-8', 'backslashreplace').strip()

    return ip_address
