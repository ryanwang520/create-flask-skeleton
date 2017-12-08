from setuptools import setup
from create_flask_skeleton import __version__

setup(
    version=__version__,
    name='create-flask-skeleton',
    packages=['create_flask_skeleton'],
    include_package_data=True,
    install_requires=[
        'pyyaml',
        'jinja2',
        'click',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points='''
    [console_scripts]
    create-flask-skeleton=create_flask_skeleton:main
    '''
)
