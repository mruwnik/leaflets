from setuptools import setup, find_packages


packages = find_packages()

# add doublevision/alembic/versions folder manually
# https://bitbucket.org/zzzeek/alembic/issue/95/__init__py-file-in-versions-directory

packages += [
    'leaflets.alembic.versions',
]

setup(
    name='leaflets',
    version='0.1',
    description='Display addresses to have leaflets delivered to them',
    author='Daniel O\'Connell',
    author_email='tojad99@gmail.com',
    packages=packages,
    install_requires=[
        'WTForms==2.1',
        'tornado==4.3',
        'wtforms-tornado==0.0.2',
        'alembic==0.8.4',
        'overpass==0.3.1',
    ],
    tests_require=[
        'pytest==2.7.3',
        'pytest-cov==2.2.0',
        'pytest-dbfixtures==0.12.0',
        'pylama==6.3.4',
        'pylama_gjslint==0.0.7',
        'pylama_pylint==2.0.0',
        'pylint==1.4.4',
        'pytest-tornado==0.4.5',
        'mock==1.3.0',
        'beautifulsoup4==4.4.1',
        'hypothesis==3.1.0',
    ],
    entry_points={
        'pytest11': [
            'leaflets = tests.pytest_plugin',
        ]
    },
)
