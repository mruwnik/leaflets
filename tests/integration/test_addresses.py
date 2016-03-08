import csv
from io import StringIO

import pytest
from bs4 import BeautifulSoup


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
def asd_test_add_addresses(admin, xsrf_client, base_url, app_with_db, database, addresses_list, count):
    """Check whether addresses are correctly imported."""
    url = app_with_db.reverse_url('import_addresses')

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

    with database.cursor() as c:
        c.execute("SELECT count(*) FROM addresses")
        assert c.fetchone() == (count,)

        c.execute("SELECT lat, lon, town, postcode, street, house FROM addresses ORDER BY id")
        for row, address in zip(c.fetchall(), addresses_list):
            # check whether the lats and lons are the same
            assert round(row[0], 4) == round(address[0], 4)
            assert round(row[1], 4) == round(address[1], 4)
            # check the rest of the fields
            assert row[2:] == address[2:]


@pytest.mark.gen_test
@pytest.mark.parametrize('addresses_list', (
    '', 'asdasd',
    '50.4671732, 19.6581435, Pilica, 42-436, Armii Krajowej, 2',  # must be tab delineated
    '50.4671732	42-436	Armii Krajowej	2',  # missing fields
    '50.4671732	19.6581435	Pilica	42-436	Armii Krajowej	Pilica	42-436	Armii Krajowej	2',  # too many fields
    'dsa	19.6581435	Pilica	42-436	Armii Krajowej	2',  # invalid lat
    '50.4671732	1fewew	Pilica	42-436	Armii Krajowej	2',  # invalid lon
))
def asd_test_add_addresses_bad(admin, xsrf_client, base_url, app_with_db, database, addresses_list):
    """Check whether bad addresses are correctly skipped."""
    url = app_with_db.reverse_url('import_addresses')

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
def test_list_addresses(addresses, admin, http_client, base_url, app_with_db, database):
    """Check whether the list of addresses is correctly generated."""
    url = app_with_db.reverse_url('list_addresses')

    response = yield http_client.fetch(base_url + url)
    assert response.code == 200

    soup = BeautifulSoup(response.body, 'html.parser')

    for row, address in zip(soup.find_all('tr')[1:], addresses):
        lat, lon, country, town, postcode, street, house_number = [td.getText() for td in row.find_all('td')]
        assert address == (float(lat), float(lon), town, postcode, street, house_number)
