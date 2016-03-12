from collections import OrderedDict

import pytest
from hypothesis import given
import hypothesis.strategies as st

from leaflets.views.adresses.address_utils import as_dict, avg, coords, geo_field, get_address, coords_center


@st.composite
def random_coords(draw):
    """Genereate a random (lat, lon) pair."""
    return (
        draw(st.floats(min_value=-180.0, max_value=180.0)),
        draw(st.floats(min_value=-90.0, max_value=90.0))
    )


@st.composite
def json_feature(draw):
    """Generate a json address feature and its center."""
    point_type = draw(st.sampled_from(['Point', 'Linestring']))

    if point_type == 'Linestring':
        # the feature geometry points are saved as (lon, lat), so make sure to reverse the normal coords
        points = draw(st.lists(random_coords().map(lambda point: (point[1], point[0]))))
        # calculate the center of the feature
        center = tuple(reversed(coords_center(points))) if points else (None, None)
    else:
        center = draw(random_coords())
        points = tuple(reversed(center))

    feature_def = {
        'geometry': {
            'type': point_type,
            'coordinates': points,
        },
        'properties': {
            'addr:city': draw(st.sampled_from(['Caer Morhen', 'Minas Tirith', 'Sietch Tabr', 'Gondolin'])),
            'addr:housenumber': str(draw(st.integers(max_value=500))),
            'addr:postcode': '%02d-%03d' % (draw(st.integers(max_value=999)), draw(st.integers(max_value=999))),
            'addr:street': draw(st.sampled_from([None, 'Prosta', 'Penny Lane', 'Main', 'Millers'])),
            'amenity': draw(st.sampled_from([None, 'library', 'school', 'college', 'bench'])),
            'email': draw(st.sampled_from([None, 'bla@bel.ds', 'jow@now.ds', 'foo@bar.com'])),
            'fax': draw(st.integers(min_value=100000, max_value=999999)),
            'name': draw(st.sampled_from([None, 'Sceas', 'Geeas', 'WWfaol'])),
        }
    }
    return feature_def, center


@given(vals=st.sampled_from([[], 0, '', None]))
def test_avg_empty(vals):
    """Check whether empty lists return 0."""
    assert avg(vals) == 0


@given(vals=st.lists(st.integers() | st.floats(allow_infinity=False, allow_nan=False), min_size=1))
def test_avg_floats(vals):
    """Check whether the average works."""
    assert avg(vals) == float(sum(vals)) / len(vals)


@given(points=st.lists(random_coords(), min_size=1))
def test_coords_center(points):
    """Check whether the center of the feature is correctly calculated."""
    end_lat, end_lon = 0, 0
    for lat, lon in points:
        end_lat += lat
        end_lon += lon
    assert coords_center(points) == [end_lat / len(points), end_lon / len(points)]


@given(feature=json_feature())
def test_coords(feature):
    """Check whether the coordinates of an address are correctly approximated."""
    feature_def, center = feature
    assert coords(feature_def) == center


@pytest.mark.parametrize('field, feature', (
    ('nodeId', {'id': 'bla'}),
    ('town', {'properties': {'addr:city': 'bla'}}),
    ('house', {'properties': {'addr:housenumber': 'bla'}}),
    ('postcode', {'properties': {'addr:postcode': 'bla'}}),
    ('street', {'properties': {'addr:street': 'bla'}}),
    ('amenity', {'properties': {'amenity': 'bla'}}),
    ('email', {'properties': {'email': 'bla'}}),
    ('fax', {'properties': {'fax': 'bla'}}),
    ('name', {'properties': {'name': 'bla'}}),
))
def test_geo_field(feature, field):
    """Check whether getting the values of varirous feature fields works."""
    assert geo_field(feature, field) == 'bla'


@given(feature=json_feature())
def test_get_addresses(feature):
    feature_def, center = feature
    lat, lon = center
    town = feature_def['properties']['addr:city']
    postcode = feature_def['properties']['addr:postcode']
    street = feature_def['properties']['addr:street']
    house = feature_def['properties']['addr:housenumber']

    assert get_address(feature_def) == [lat, lon, town, postcode, street, house]


@st.composite
def sample_row(draw):
    """Get a sample database row."""
    return OrderedDict((
        ('lat', draw(st.floats(min_value=-180, max_value=180))),
        ('lon', draw(st.floats(min_value=-90, max_value=90))),
        ('country', draw(st.sampled_from(['Cintra', 'Arnor', 'Arrakis', 'Gondor']))),
        ('town', draw(st.sampled_from(['Caer Morhen', 'Minas Tirith', 'Sietch Tabr', 'Gondolin']))),
        ('postcode', draw(st.sampled_from(['123123', '23423', '123122', '43223', '231232']))),
        ('street', draw(st.sampled_from(['street1', 'street2', 'street3', 'street4', 'street5']))),
        ('house', draw(st.integers(max_value=500))),
    ))


@given(results=st.lists(sample_row()))
def test_as_dict(results):
    """Check whether rows are correctly converted to dicts."""
    rows_w_ids = [[i] + list(row.values()) for i, row in enumerate(results)]
    assert as_dict(rows_w_ids) == {i: dict(row) for i, row in enumerate(results)}
