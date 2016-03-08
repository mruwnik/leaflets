import re

from urllib.parse import urlencode

import pytest
from mock import patch
from path import Path
from pytest_dbfixtures import factories
from tornado import gen
from tornado.httpclient import HTTPRequest

from alembic.config import Config
from alembic import command as alembic_command

from leaflets.app import setup_app, attach_database
from leaflets.views import BaseHandler  # noqa
from leaflets.etc import options

options.DB_USER = 'postgres'
options.DB_PASSWORD = None
options.DB_PORT = 15533
options.DB_HOST = '127.0.0.1'

postgres_proc = factories.postgresql_proc(
        executable=options.POSTGRES_LOCATION + '9.3/bin/pg_ctl', port=options.DB_PORT,
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


@pytest.yield_fixture
def app_with_db(app, io_loop, database):
    """Get the application with the database attached."""
    attach_database(io_loop, app)
    yield app
    app.db.close()


def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be
    uploaded as files.
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for key, value in fields.items():
        L += ['--' + BOUNDARY, 'Content-Disposition: form-data; name="%s"' % key, '', value]
    for key, (filename, value) in files.items():
        filename = filename.encode("utf8")
        L += [
            '--' + BOUNDARY,
            'Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename),
            'Content-Type: multipart/form-data',
            '', value
        ]
    L += ['--' + BOUNDARY + '--', '']
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body


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
    def xsrf_request(url, data, headers=None):
        """Post the given data to the given url."""
        xsrf_token = yield get_xsrf_token()

        if data:
            data['_xsrf'] = xsrf_token

        headers = headers or {}
        headers.update({'cookie': '_xsrf=' + xsrf_token})

        request = HTTPRequest(
            url, 'POST',
            body=urlencode(data),
            headers=headers,
        )
        return request

    @gen.coroutine
    def multipart_request(url, fields, files):
        """Post fields and files to an http host as multipart/form-data.

        fields is a dict of form fields.
        files is a dict of {name: (filename, value)} elements for data to be
        uploaded as files.

        :returns: the server's response page.
        """
        xsrf_token = yield get_xsrf_token()

        fields = fields or {}
        fields['_xsrf'] = xsrf_token

        content_type, body = encode_multipart_formdata(fields, files)
        headers = {
            "Content-Type": content_type,
            'content-length': str(len(body)),
            'cookie': '_xsrf=' + xsrf_token
        }
        return HTTPRequest(url, "POST", headers=headers, body=body)

    http_client.xsrf_token = get_xsrf_token
    http_client.xsrf_request = xsrf_request
    http_client.multipart_request = multipart_request

    return http_client


@pytest.yield_fixture
def admin(database):
    with database.cursor() as c:
        c.execute("INSERT INTO users VALUES (1, 'test', 'test@asd.sd', 'test', True)")

    async def is_admin(self):
        return 1

    with patch('leaflets.views.BaseHandler.get_current_user', return_value=1), \
         patch('leaflets.views.BaseHandler.is_admin', property(is_admin)):
        yield
