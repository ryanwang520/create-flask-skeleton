import click
import os
import shutil
from jinja2 import Template


@click.command()
@click.option('--version', help='version', is_flag=True)
@click.argument('name', required=False)
def main(version, name):
    if version:
        click.echo('version 0.0.1')
        return
    bootstrap(name)


class File:
    def __init__(self, dir_path, file_name):
        self.dir_path = dir_path
        self.file_name = file_name

    @property
    def path(self):
        return os.path.join(self.dir_path, self.file_name)


def mkdirs(name, dir_paths):
    shutil.rmtree(name, ignore_errors=True)
    root_dir = os.path.join(os.getcwd(), name)
    os.mkdir(root_dir)

    for dir_path in dir_paths:
        if dir_path.startswith('app'):
            dir_path = name + dir_path[3:]
        path = os.path.join(os.getcwd(), name, dir_path)
        # print(path)
        # import pdb
        # pdb.set_trace()
        os.mkdir(path)


def copy_files(name, file_paths, template_path):
    for file_path in file_paths:
        relative_path = file_path.replace(template_path + '/', '')
        if relative_path.startswith('app'):
            relative_path = name + relative_path[3:]
        # pdb.set_trace()
        # import pdb
        # pdb.set_trace()
        dest = os.path.join(os.getcwd(), name, relative_path)

        if file_path.endswith('.pyc'):
            continue
        content = replace_template(name, file_path)
        with open(dest, 'w') as f:
            f.write(content)
        # shutil.copyfile(file_path, dest)


def replace_template(name, file_path):
    with open(file_path) as f:
        content = f.read()
        if file_path.endswith('.html'):
            return content
        template = Template(content)
        return template.render(app=name)


def bootstrap(name):
    templates_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'template'))
    base_dir = os.path.abspath(os.path.dirname(__file__))
    print(base_dir)
    # return
    dir_paths = []
    file_paths = []
    for root, dirs, files in os.walk(templates_path):
        root_path = os.path.abspath(root)
        for f in files:
            file_paths.append(os.path.join(root_path, f))
        if root != templates_path:
            # import pdb
            # pdb.set_trace()
            dir_paths.append(root.replace('{}/'.format(templates_path), ''))
    mkdirs(name, dir_paths)
    copy_files(name, file_paths, templates_path)
    # print(dirs)
    # print(files)
    #     print(root, "consumes", end=" ")
    #     print(sum(getsize(join(root, name)) for name in files), end=" ")
    #     print("bytes in", len(files), "non-directory files")
    #     if 'CVS' in dirs:
    #         dirs.remove('CVS')  # don't visit CVS directories


if __name__ == '__main__':
    main()
