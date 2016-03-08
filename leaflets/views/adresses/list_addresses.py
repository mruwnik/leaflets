import logging

from tornado import gen
from momoko.exceptions import PartiallyConnectedError

from leaflets.views.base import BaseHandler

logger = logging.getLogger()


class AddressListHandler(BaseHandler):

    """Import address CSV files."""

    url = '/addresses/list'

    @gen.coroutine
    def get(self):
        try:
            north = float(self.get_argument('north', 90))
            south = float(self.get_argument('south', -90))
            east = float(self.get_argument('east', 180))
            west = float(self.get_argument('west', -180))
        except ValueError:
            return self.write({'error': 'bad bounding args'})

        try:
            conn = yield self.application.db.connect()
            addresses = yield conn.execute(
                'SELECT id, lat, lon, country, town, postcode, street, house FROM addresses '
                'WHERE lat < %s AND lat > %s AND lon < %s AND lon > %s', (north, south, east, west)
            )
        except PartiallyConnectedError:
            addresses = []

        def to_dict(row):
            return dict(zip(['lat', 'lon', 'country', 'town', 'postcode', 'street', 'house'], row[1:]))

        if self.get_argument('output', None) == 'html':
            self.render('list_addresses.html', addresses=addresses)
        else:
            self.write({addr[0]: to_dict(addr) for addr in addresses})
