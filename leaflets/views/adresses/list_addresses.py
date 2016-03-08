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
            conn = yield self.application.db.connect()
            addresses = yield conn.execute(
                'SELECT lat, lon, country, town, postcode, street, house FROM addresses'
            )
        except PartiallyConnectedError:
            addresses = []
        self.render('list_addresses.html', addresses=addresses)
