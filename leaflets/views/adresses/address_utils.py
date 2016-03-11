"""Various tools to find and manipulate addresses."""

import overpass


def avg(values):
    """Calculate the average of the given values.

    :param list values: the values for which the average is to be calculated
    :return: the average
    """
    return sum(values) / len(values) if values else 0


def coords(feature):
    """Get the coordinates from the given features dict.

    :param dict feature: a feature as is returned by overpass
    :return: (lat, lon)
    """
    geometry = feature['geometry']
    geo_type = geometry['type'].lower()
    if geo_type == 'point':
        lon, lat = geometry['coordinates']
    elif geo_type == 'linestring':
        lon, lat = list(map(avg, zip(*geometry['coordinates'])))
    return lat, lon


geo_to_address = {
    'nodeId': ('id',),
    'town': ('properties', 'addr:city'),
    'house': ('properties', 'addr:housenumber'),
    'postcode': ('properties', 'addr:postcode'),
    'street': ('properties', 'addr:street'),
    'amenity': ('properties', 'amenity'),
    'email': ('properties', 'email'),
    'fax': ('properties', 'fax'),
    'name': ('properties', 'name'),
}
"""A mapping that specifies how to get to specific fields in an GeoJSON feature."""


def geo_field(feature, field):
    """Get the specified field from the given feature.

    :param dict feature: a GeoJSON feature
    :param str field: a key from geo_to_address
    :return: the value of the given field
    """
    if field not in geo_to_address:
        return None

    def traverse_dict(container, keys):
        return traverse_dict(container.get(keys[0]), keys[1:]) if container and keys else container

    return traverse_dict(feature, geo_to_address.get(field))


def get_address(feature):
    """Get a list with the address from the given feature.

    :param dict feature: a GeoJSON feature
    :return: [lat, lon, town, postcode, street, housenumber]
    """
    return list(coords(feature)) + list(
        map(lambda field: geo_field(feature, field), ['town', 'postcode', 'street', 'house']))


def find_addresses(bbox):
    """Find all addresses in the given bounding box.

    :param tuple bbox: (south, west, north, east)
    :return: a map with all found addresses
    """
    api = overpass.API()
    points = api.Get(
        '(node["addr:street"]{0}; way["addr:street"]{0};)'.format(bbox), asGeoJSON=True)

    return map(get_address, points['features'])


def as_dict(rows):
    """Return the given rows as a dict."""
    def to_dict(row):
        return dict(zip(['lat', 'lon', 'country', 'town', 'postcode', 'street', 'house'], row[1:]))

    return {row[0]: to_dict(row) for row in rows}
