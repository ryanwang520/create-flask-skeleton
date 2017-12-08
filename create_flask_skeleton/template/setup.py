from setuptools import setup

setup(
    name='{{ app }}',
    dependency_links=[
        'git+https://github.com/pallets/flask.git@d08d96acbcabcde23307ed060f71f95ba9cb7b8d#egg=flask',
    ],
    packages=['{{ app }}'],
    include_package_data=True,
    install_requires=[
        'flask',
        'pyjwt',
        'sqlalchemy',
        'voluptuous',
        'pyyaml',
        'lazy-object-proxy'
    ],
    setup_requires=['pytest-runner', ],
    tests_require=['pytest', ],
)
