from setuptools import setup

setup(
    name="keycloak_cli",
    version='0.1',
    py_modules=['keycloak_cli'],
    install_requires=[
        'Click',
        'requests==2.23.0',
        'PyYAML==5.3.1'
    ],
    entry_points='''
        [console_scripts]
        keycloak_cli=keycloak_cli:cli
    ''',
)