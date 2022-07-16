from distutils.core import setup

setup(
    name='Watchdog test',
    version='0.1.0',
    description='Testing task with watchdog',
    author='Bezgin Alexandr',
    author_email='bezgin.sasha06@gmail.com',
    install_requires=[
        'watchdog',
        'sqlalchemy',
        'python-dateutil',
        'pysqlite3',
    ],
)
