import logging

from tornado import gen
from momoko.exceptions import PartiallyConnectedError

from leaflets.views.base import BaseHandler
from leaflets.views.adresses.parse import as_dict, BoundingBox
from leaflets.models import Address


logger = logging.getLogger()


class AddressListHandler(BaseHandler, BoundingBox):

    """Import address CSV files."""

    url = '/addresses/list'
    name = 'list_addresses'

    @gen.coroutine
    def get(self):
        """Return all addresses that are in the provided bounding box.

        All addresses that lie between (north, west) and (south, east) will
        be returned, where north, south, east and west are get parameters. The
        output is JSON by default, but it can be changed to HTML by setting 'output=html'
        """
        south, west, north, east = self.get_bounds()

        try:
            addresses = Address.query.filter(
                Address.lat < north, Address.lat > south, Address.lon < east, Address.lon > west
            ).order_by(Address.id).all()
        except PartiallyConnectedError:
            addresses = []

        if self.get_argument('output', None) == 'html':
            self.render('addresses/list_addresses.html', addresses=addresses)
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
            addresses = Address.query.filter(Address.id.in_(address_ids)).all()
        except PartiallyConnectedError:
            addresses = []
        except ValueError:
            logger.error('Invalid ids provided: %s', address_ids)

        self.write(as_dict(addresses))
