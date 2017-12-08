from setuptools import setup

setup(
    version='0.0.1',
    name='create-flask-skeleton',
    packages=['create_flask_skeleton'],
    include_package_data=True,
    install_requires=[
        'flask',
        'pyjwt',
        'pyyaml'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points='''
    [console_scripts]
    create-flask-skeleton=create_flask_skeleton:main
    '''
)
