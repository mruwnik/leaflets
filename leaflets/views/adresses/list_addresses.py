import logging

from tornado import gen

from leaflets.views.base import BaseHandler

logger = logging.getLogger()


class AddressListHandler(BaseHandler):

    """Import address CSV files."""

    url = '/addresses/list'

    @gen.coroutine
    def get(self):
        conn = yield self.application.db.connect()
        addresses = yield conn.execute(
            'SELECT lat, lon, country, town, postcode, street, house FROM addresses'
        )
        self.render('list_addresses.html', addresses=addresses)
