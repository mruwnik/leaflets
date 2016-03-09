import pytest

from mock import Mock

from leaflets.views import AddressListHandler


@pytest.mark.parametrize('rows', (
    (
        (1, 12.2, 43.3, 'dw', 're',  '23-433', '432', '34'),
    ),
    (
        (1, 12.2, 43.3, 'dw', 're',  '23-433', '432', '34'),
        (2, 232.2, 43.3, 'sdfdw', 'gre',  '23-435', '442', '34')
    ),
    (
        (1, 12.2, 43.3, 'dw', 're',  '23-433', '432', '34'),
        (2, 232.2, 43.3, 'sdfdw', 'gre',  '23-435', '442', '34'),
        (3, 2.2, 73.3, 's89dw', 'g8e',  '27-165', '4fgh', '56'),
    ),
))
def test_to_dict(app, rows):
    """Check whether converting rows to dicts works."""
    handler = AddressListHandler(app, Mock())
    as_dict = handler.as_dict(rows)

    for row in rows:
        id, lat, lon, country, town, postcode, street, house = row
        assert as_dict[id] == {
            'lat': lat, 'lon': lon, 'country': country, 'town': town,
            'postcode': postcode, 'street': street, 'house': house
        }
