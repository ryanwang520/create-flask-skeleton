from contextlib import contextmanager

import click
import os
import sys
from jinja2 import Template

TEMPLATE_NAME = 'app'

__version__ = '0.0.2'


@click.command()
@click.option('--version', help='version', is_flag=True)
@click.option('--two', help='install python2 virtualenv', is_flag=True, default=False)
@click.argument('name', required=False)
def main(version, two, name):
    if version:
        click.echo('version {}'.format(__version__))
        return
    bootstrap(name, version=2 if two else 3)


class File:
    def __init__(self, dir_path, file_name):
        self.dir_path = dir_path
        self.file_name = file_name

    @property
    def path(self):
        return os.path.join(self.dir_path, self.file_name)


def mkdirs(name, dir_paths):
    if os.path.exists(name):
        click.echo('The directory {} already exists, try using a new directory name'.format(name))
        sys.exit(1)
    root_dir = os.path.join(os.getcwd(), name)
    os.mkdir(root_dir)

    for dir_path in dir_paths:
        if dir_path.startswith(TEMPLATE_NAME):
            dir_path = name + dir_path[len(TEMPLATE_NAME):]
        path = os.path.join(os.getcwd(), name, dir_path)
        os.mkdir(path)


def copy_files(name, file_paths, template_path):
    for file_path in file_paths:
        relative_path = file_path.replace(template_path + '/', '')
        if relative_path.startswith(TEMPLATE_NAME):
            relative_path = name + relative_path[len(TEMPLATE_NAME):]
        dest = os.path.join(os.getcwd(), name, relative_path)

        if file_path.endswith('.pyc'):
            continue
        content = replace_template(name, file_path)
        with open(dest, 'w') as f:
            f.write(content)


def replace_template(name, file_path):
    with open(file_path) as f:
        content = f.read()
        if file_path.endswith('.html'):
            return content
        template = Template(content)
        return template.render(app=name)


@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


def install_packages(name, version):
    with cd(name):
        if os.system("pipenv > /dev/null 2>&1") != 0:
            os.system("pip install pipenv")
        if version == 2:
            os.system('pipenv --two')
        os.system("pipenv install")
    click.echo("install requirements successfully")
    click.echo("cd to {} directory and run pipenv run flask run to start development".format(name))


def bootstrap(name, version):
    templates_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'template'))
    dir_paths = []
    file_paths = []
    for root, dirs, files in os.walk(templates_path):
        root_path = os.path.abspath(root)
        for f in files:
            file_paths.append(os.path.join(root_path, f))
        if root != templates_path:
            dir_paths.append(root.replace('{}/'.format(templates_path), ''))
    mkdirs(name, dir_paths)
    copy_files(name, file_paths, templates_path)
    install_packages(name, version)


if __name__ == '__main__':
    main()
