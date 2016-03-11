import logging

from tornado import gen
from momoko.exceptions import PartiallyConnectedError

from leaflets.views.base import BaseHandler
from leaflets.views.adresses.address_utils import as_dict

logger = logging.getLogger()


class AddressListHandler(BaseHandler):

    """Import address CSV files."""

    url = '/addresses/list'

    @gen.coroutine
    def get(self):
        """Return all addresses that are in the provided bounding box.

        All addresses that lie between (north, west) and (south, east) will
        be returned, where north, south, east and west are get parameters. The
        output is JSON by default, but it can be changed to HTML by setting 'output=html'
        """
        try:
            north = float(self.get_argument('north', 90))
            south = float(self.get_argument('south', -90))
            east = float(self.get_argument('east', 180))
            west = float(self.get_argument('west', -180))
        except ValueError:
            return self.write({'error': 'bad bounding args'})

        try:
            addresses = yield self.application.db.execute(
                'SELECT id, lat, lon, country, town, postcode, street, house FROM addresses '
                'WHERE lat < %s AND lat > %s AND lon < %s AND lon > %s', (north, south, east, west)
            )
        except PartiallyConnectedError:
            addresses = []

        if self.get_argument('output', None) == 'html':
            self.render('list_addresses.html', addresses=addresses)
        else:
            self.write(as_dict(addresses))

    @gen.coroutine
    def post(self):
        """Return all addresses with the provided ids.

        Each 'addresses[]' param should be a single address id.
        """
        address_ids = self.get_arguments('addresses[]')

        if not address_ids:
            return self.write({})

        try:
            addresses = yield self.application.db.execute(
                'SELECT id, lat, lon, country, town, postcode, street, house FROM addresses '
                'WHERE id IN %s', (tuple(map(int, address_ids)), )
            )
        except PartiallyConnectedError:
            addresses = []
        except ValueError:
            logger.error('Invalid ids provided: %s', address_ids)

        self.write(as_dict(addresses))