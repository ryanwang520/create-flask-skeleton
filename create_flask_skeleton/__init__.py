from contextlib import contextmanager

import re
import os
import sys

import click
from jinja2 import Template

TEMPLATE_NAME = "app"

__version__ = "0.1.6"


@click.command()
@click.option("--version", help="version", is_flag=True)
@click.argument("name", required=False)
def main(version, name):
    if version:
        click.echo(f"version {__version__}")
        return
    if not name:
        click.echo("Please give a project name.")
        sys.exit(2)
    bootstrap(name)


def mkdirs(name, dir_paths):
    if os.path.exists(name):
        click.echo(
            f"The directory {name} already exists, try using a new directory name"
        )
        sys.exit(1)
    root_dir = os.path.join(os.getcwd(), name)
    os.mkdir(root_dir)
    package_name = get_package_name(name)

    for dir_path in dir_paths:
        if dir_path.startswith(TEMPLATE_NAME):
            dir_path = package_name + dir_path[len(TEMPLATE_NAME) :]
        path = os.path.join(os.getcwd(), name, dir_path)
        os.mkdir(path)


def copy_files(name, file_paths, template_path):
    package_name = get_package_name(name)
    for file_path in file_paths:
        relative_path = file_path.replace(template_path + "/", "")
        if relative_path.startswith(TEMPLATE_NAME):
            relative_path = package_name + relative_path[len(TEMPLATE_NAME) :]
        dest = os.path.join(os.getcwd(), name, relative_path)

        if file_path.endswith(".pyc"):
            continue
        content = replace_template(package_name, file_path)
        with open(dest, "w") as f:
            f.write(content)


def replace_template(name, file_path):
    with open(file_path) as f:
        content = f.read()
        if file_path.endswith(".html"):
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


def install_packages(name):
    with cd(name):
        if os.system("poetry > /dev/null 2>&1") != 0:
            os.system("pip install poetry")
        os.system("poetry install")
    click.echo("Install requirements successfully")
    click.echo(
        f"Now cd to {name} directory and run `poetry run flask run` to start development,"
        " you may need to run `poetry run flask db init` to get a initial sqlite database setup"
        ""
    )


package_pattern = re.compile("[a-zA-Z][a-zA-Z0-9_-]+$")


def get_package_name(name):
    return name.replace("-", "_")


def bootstrap(name):
    if not package_pattern.match(name):
        click.echo(f"Can not create package based on name {name}")
        sys.exit(2)
    templates_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "template")
    )
    dir_paths = []
    file_paths = []
    for root, dirs, files in os.walk(templates_path):
        root_path = os.path.abspath(root)
        for f in files:
            file_paths.append(os.path.join(root_path, f))
        if root != templates_path:
            dir_paths.append(root.replace(f"{templates_path}/", ""))
    mkdirs(name, dir_paths)
    copy_files(name, file_paths, templates_path)
    install_packages(name)


if __name__ == "__main__":
    main()
