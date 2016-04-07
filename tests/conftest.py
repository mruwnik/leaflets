import re
from datetime import datetime
from urllib.parse import urlencode

import pytest
from mock import patch
from path import Path
from pytest_dbfixtures import factories
from tornado import gen
from tornado.httpclient import HTTPRequest

from alembic.config import Config
from alembic import command as alembic_command

from leaflets.app import setup_app
from leaflets.views import BaseHandler  # noqa
from leaflets.models import User, Address, CampaignAddress, Campaign
from leaflets.etc import options
from leaflets.dev import add_users
from leaflets import database as db

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

    db.session.close_all()
    db.engine.dispose()


@pytest.yield_fixture
def db_session(database):
    from leaflets import database
    session = database.session()

    yield session

    session.close()


@pytest.fixture
def app(io_loop):
    """The application to be used for tests."""
    app = setup_app()
    return app


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
            body=urlencode({k: v for k, v in data.items() if v}, doseq=True),
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
def admin(db_session):
    user = User(username='test', email='test@sdf.df', password_hash='test', admin=True)
    db_session.add(user)
    db_session.commit()

    async def is_admin(self):
        return user.id

    with patch('leaflets.views.BaseHandler.get_current_user', return_value=user.id), \
         patch('leaflets.views.BaseHandler.is_admin', property(is_admin)):  # noqa
        yield user


ADDRESSES = [
    (50.4569326, 19.2629951, 'Siewierz', '42-470', 'Długa', '2'),
    (50.4671732, 19.6581435, 'Pilica', '42-436', 'Armii Krajowej', '2'),
    (49.6979663, 19.1803986, 'Żywiec-Pietrzykowice', '34-300', 'Wesoła', '5'),
    (50.2987945, 18.6890583, 'Gliwice', '44-100', 'Generała Jarosława Dąbrowskiego', '18'),
    (50.2831121, 18.6633475, 'Gliwice', '', 'Rybnicka', '31'),
    (50.2227530, 18.6750804, 'Knurów', '44-190', 'Księdza Alojzego Koziełka', '8'),
    (50.4083606, 19.4800624, 'Ogrodzieniec', '', 'Centuria', ''),
    (49.8277328, 19.0502823, 'Bielsko-Biała', '', 'Mostowa', '5'),
    (49.8273954, 19.0501131, 'Bielsko-Biała', '', 'Mostowa', '5'),
    (49.8272465, 19.0494004, 'Bielsko-Biała', '', 'Mostowa', '5'),
    (50.3082116, 18.6776321, 'Gliwice', '44-100', 'Warszawska', '35'),
    (50.3177967, 18.7708699, 'Zabrze', '41-819', 'Gdańska', '22'),
    (50.3863792, 18.5754243, '', '44-120', 'Węgorza', '1'),
    (50.2971028, 18.6492137, '', '', 'Generała Władysława Andersa', '12'),
    (50.3054516, 18.6318022, '', '', 'Kozielska', '128'),
    (50.2938838, 18.8192230, 'Zabrze', '41-806', 'Jerzego Wyciska', '1'),
    (50.3167368, 18.5902134, '', '', 'Kozielska', '297'),
    (50.3115804, 18.7580428, 'Zabrze', '41-819', 'Grunwaldzka', '46'),
    (50.5260720, 19.5087337, 'Zawiercie', '42-400', 'Skarżycka', '11'),
    (50.2700593, 18.3703886, 'Kotlarnia', '47-246', 'Dębowa', '3'),
    (50.2221554, 19.0670677, 'Katowice', '40-467', 'Plac Pod Lipami', '1'),
    (50.2214011, 19.0644236, 'Katowice', '40-476', 'Plac Pod Lipami', '9'),
]


@pytest.fixture
def addresses(db_session):
    """Static addresses in the database."""
    addresses = [
        Address(lat=lat, lon=lon, town=town, postcode=postcode, street=street, house=house)
        for lat, lon, town, postcode, street, house in ADDRESSES
    ]
    db_session.add_all(addresses)
    db_session.commit()
    return addresses


@pytest.fixture
def campaign(db_session, addresses, admin):
    """Static addresses in the database."""
    camp = Campaign(
        name='斑尾高原スキー場',
        desc='test campaign dęść→ß→þłπóęœ',
        start=datetime.utcnow(),
        user=admin,
    )
    db_session.add(camp)
    db_session.add_all([CampaignAddress(campaign=camp, address_id=addr.id) for addr in addresses])
    db_session.commit()
    return camp


@pytest.fixture
def users(admin, db_session):
    """Add a load of fake users."""
    add_users(admin)
    db_session.commit()
    return db_session.query(User).all()
