import re
from urllib.parse import urlencode

import pytest
from path import Path
from pytest_dbfixtures import factories
from tornado import gen
from tornado.httpclient import HTTPRequest

from alembic.config import Config
from alembic import command as alembic_command

from leaflets.app import setup_app, attach_database
from leaflets.etc import options

options.DB_USER = 'postgres'
options.DB_PASSWORD = None
options.DB_PORT = 15533
options.DB_HOST = '127.0.0.1'

postgres_proc = factories.postgresql_proc(
        executable='/usr/lib64/postgresql/9.3/bin/pg_ctl', port=options.DB_PORT,
)
postgresdb = factories.postgresql('postgres_proc', db=options.DB_NAME)


@pytest.yield_fixture
def database(postgresdb):
    """Set up the database."""
    alembic_ini = '../tests/test_alembic.ini'
    alembic_cfg = Config(alembic_ini)

    with (Path(__file__).parent.parent / 'leaflets'):
        alembic_command.upgrade(alembic_cfg, "head")

    yield postgresdb

    with postgresdb.cursor() as c:
        c.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = c.fetchall()
        for table, in tables:
            c.execute('DROP TABLE %s' % table)


@pytest.fixture
def app(io_loop):
    """The application to be used for tests."""
    app = setup_app()
    return app


@pytest.fixture
def app_with_db(app, io_loop, database):
    """Get the application with the database attached."""
    attach_database(io_loop, app)
    return app


@pytest.fixture
def xsrf_client(http_client, app, base_url):
    """A http client that can handle xsrf forms."""

    @gen.coroutine
    def get_xsrf_token():
        """Return CSRF token extracted from the text of a page containing a form."""
        url = app.reverse_url('login')
        response = yield http_client.fetch(base_url + url)
        return re.search(
            '<input type="hidden" name="_xsrf" value="(.*?)"/>',
            str(response.body)).group(1)

    @gen.coroutine
    def xsrf_request(url, data):
        """Post the given data to the given url."""
        xsrf_token = yield get_xsrf_token()
        if data:
            data['_xsrf'] = xsrf_token

        request = HTTPRequest(
            url, 'POST',
            body=urlencode(data),
            headers={'cookie': '_xsrf=' + xsrf_token},
        )
        return request

    http_client.xsrf_token = get_xsrf_token
    http_client.xsrf_request = xsrf_request
    return http_client

