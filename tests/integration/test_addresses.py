import csv
import json
from io import StringIO

import pytest
from bs4 import BeautifulSoup

from leaflets.views import AddressSearchHandler
from leaflets.models import Address


def generate_address(i):
    """Generate a dummy address for the given number."""
    return (
        (50 - i) * 0.01,
        (50 - i) * 0.01,
        'town %d' % i,
        str(10000 + i * 150),
        'street %d' % (i % 20),
        str(i % 50)
    )


@pytest.mark.gen_test
@pytest.mark.parametrize('addresses_list, count', (
    ([(50.4671732, 19.6581435, 'Pilica', '42-436', 'Armii Krajowej', '2')], 1),
    ([generate_address(i % 50) for i in range(100)], 50),
    ([generate_address(i) for i in range(100)], 100),
))
def test_add_addresses(admin, xsrf_client, base_url, app, addresses_list, count):
    """Check whether addresses are correctly imported."""
    url = app.reverse_url('csv_addresses')

    # generate a csv file
    csv_data = StringIO()
    writer = csv.writer(csv_data, delimiter='\t')
    for address in addresses_list:
        writer.writerow(address)
    csv_data.seek(0)

    # send the file
    request = yield xsrf_client.multipart_request(
        base_url + url, None, {'csv': ('bla', csv_data.read())})

    response = yield xsrf_client.fetch(request)
    assert response.code == 200

    addresses = Address.query.all()
    assert len(addresses) == count

    for db_address, address in zip(addresses, addresses_list):
        lat, lon, town, postcode, street, house = address
        # check whether the lats and lons are the same
        assert round(db_address.lat, 4) == round(lat, 4)
        assert round(db_address.lon, 4) == round(lon, 4)
        # check the rest of the fields
        assert db_address.town == town
        assert db_address.postcode == postcode
        assert db_address.street == street
        assert db_address.house == house


@pytest.mark.gen_test
@pytest.mark.parametrize('addresses_list', (
    '', 'asdasd',
    '50.4671732, 19.6581435, Pilica, 42-436, Armii Krajowej, 2',  # must be tab delineated
    '50.4671732	42-436	Armii Krajowej	2',  # missing fields
    '50.4671732	19.6581435	Pilica	42-436	Armii Krajowej	Pilica	42-436	Armii Krajowej	2',  # too many fields
    'dsa	19.6581435	Pilica	42-436	Armii Krajowej	2',  # invalid lat
    '50.4671732	1fewew	Pilica	42-436	Armii Krajowej	2',  # invalid lon
))
def test_add_addresses_bad(admin, xsrf_client, base_url, app, database, addresses_list):
    """Check whether bad addresses are correctly skipped."""
    url = app.reverse_url('csv_addresses')

    async def send_addresses(addresses, expected_count):
        # send the file
        request = await xsrf_client.multipart_request(
            base_url + url, None, {'csv': ('bla', addresses)})

        response = await xsrf_client.fetch(request)
        assert response.code == 200

        with database.cursor() as c:
            c.execute("SELECT count(*) FROM addresses")
            assert c.fetchone() == (expected_count,)

    # bad address - dont save
    yield send_addresses(addresses_list, 0)

    # the 2 good addresses should be saved
    yield send_addresses(
        '49.8277328	19.0502823	Bielsko-Biała		Mostowa	5\n'
         + addresses_list + '\n'
        '49.8273954	19.0501131	Bielsko-Biała		Mostowa	2\n', 2
    )


@pytest.mark.gen_test
def test_list_addresses(addresses, admin, http_client, base_url, app, database):
    """Check whether the list of addresses is correctly generated."""
    url = app.reverse_url('list_addresses')

    response = yield http_client.fetch(base_url + url + '?output=html')
    assert response.code == 200

    soup = BeautifulSoup(response.body, 'html.parser')

    for row, address in zip(soup.find_all('tr')[1:], addresses):
        lat, lon, country, town, postcode, street, house_number = [td.getText() for td in row.find_all('td')]
        assert address == (float(lat), float(lon), town, postcode, street, house_number)


@pytest.mark.parametrize('type', ('?output=json', ''))
@pytest.mark.gen_test
def test_list_addresses_json(addresses, admin, http_client, base_url, app, database, type):
    """Check whether the list of addresses is correctly generated when json is desired."""
    url = app.reverse_url('list_addresses')

    # get the json from the server
    response = yield http_client.fetch(base_url + url + type)
    assert response.code == 200
    results = json.loads(response.body.decode('utf8'))

    # get all rows from the database
    with database.cursor() as c:
        c.execute('SELECT id, lat, lon, country, town, postcode, street, house FROM addresses')
        rows = c.fetchall()

    # make sure that the amounts are correct
    assert rows
    assert len(rows) == len(results)

    # make sure the contents are correct
    for row in rows:
        address_dict = dict(zip(['lat', 'lon', 'country', 'town', 'postcode', 'street', 'house'], row[1:]))
        assert results[str(row[0])] == address_dict


def check_error(client, url, post_data, error):
    """Make sure that a correct error is returned."""
    request = yield client.xsrf_request(url, post_data)
    try:
        yield client.fetch(request)
    except Exception as e:
        assert e.response.code == 400
        assert e.response.reason == error
    else:
        assert False, 'A 400 code should have been raised'


@pytest.mark.gen_test
@pytest.mark.parametrize('lat, error', (
    (None, AddressSearchHandler.BAD_BOUNDING_BOX),
    ('qwdq', AddressSearchHandler.BAD_BOUNDING_BOX),
    (90.1, AddressSearchHandler.BAD_COORDS),
    (-90.1, AddressSearchHandler.BAD_COORDS),
    (91, AddressSearchHandler.BAD_COORDS),
    (71, AddressSearchHandler.OVERSIZED_BOUNDING_BOX),
))
def test_find_addresses_bad_lat(admin, xsrf_client, base_url, app, lat, error):
    """Check whether bad latitudes are validated."""
    url = base_url + app.reverse_url('search_addresses')

    check_error(xsrf_client, url, {'north': lat, 'south': 0.0, 'east': 0.3, 'west': 0.2}, error)
    check_error(xsrf_client, url, {'north': 0.0, 'south': lat, 'east': 0.3, 'west': 0.2}, error)


@pytest.mark.gen_test
@pytest.mark.parametrize('lon, error', (
    (None, AddressSearchHandler.BAD_BOUNDING_BOX),
    ('qwdq', AddressSearchHandler.BAD_BOUNDING_BOX),
    (180.1, AddressSearchHandler.BAD_COORDS),
    (-181, AddressSearchHandler.BAD_COORDS),
    (71, AddressSearchHandler.OVERSIZED_BOUNDING_BOX),
))
def test_find_addresses_bad_lon(admin, xsrf_client, base_url, app, lon, error):
    """Check whether bad longitudes are validated."""
    url = base_url + app.reverse_url('search_addresses')

    check_error(xsrf_client, url, {'north': 0.0, 'south': 0.0, 'east': 0.3, 'west': lon}, error)
    check_error(xsrf_client, url, {'north': 0.0, 'south': 0.0, 'east': lon, 'west': 0.2}, error)


@pytest.mark.parametrize('dir', ('north', 'south', 'east', 'west'))
def test_find_addresses_missing_direction(admin, xsrf_client, base_url, app, dir):
    """Check whether missing paramaters cause an error."""
    url = base_url + app.reverse_url('search_addresses')
    params = {key: 1 for key in ('north', 'south', 'east', 'west') if key != dir}

    check_error(xsrf_client, url, params, AddressSearchHandler.NO_BOUNDING_BOX)
