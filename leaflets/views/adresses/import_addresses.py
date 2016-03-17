import csv
import re
import logging
from urllib.parse import urlencode

from tornado import gen
from tornado.web import authenticated, HTTPError

from leaflets.views.base import BaseHandler
from leaflets.views.adresses.address_utils import find_addresses
from leaflets import database
from leaflets.models import Address

logger = logging.getLogger()


class AddressImportHandler(BaseHandler):

    """Import addresses."""

    url = '/addresses/import'

    @authenticated
    def get(self):
        """Show the import form."""
        self.render('addresses/upload_addresses.html')

    def import_addresses(self, addresses):
        for row in addresses:
            try:
                lat, lon, town, postcode, street, house = row
                country = 'Polska'

                address = Address(
                    lat=float(lat), lon=float(lon), town=town, postcode=postcode,
                    street=street, house=house, country=country
                )

                if address.is_unique:
                    database.session.add(address)
                else:
                    logger.warn('found duplicate for %s', row)
            except (ValueError, TypeError, UnboundLocalError):
                logger.warn('invalid address provided: %s', row)

        database.session.commit()


class CSVImportHandler(AddressImportHandler):

    """Import address CSV files."""

    url = '/addresses/import_csv'
    name = 'csv_addresses'

    def bytes_split(self, to_split, delimeter='\w'):
        """Split the given bytes stream like str.split() would.

        :param bytes to_split: the bytes to be split
        :param str delimeter: what to split on
        :yields: the resulting split items
        """
        for match in re.finditer(b'[^%s]+' % delimeter.encode(), to_split):
            yield match.group(0).decode('utf8')

    @authenticated
    @gen.coroutine
    def post(self):
        """Import the given csv file."""
        is_admin = self.is_admin
        if not is_admin:
            raise HTTPError(403)

        csv_data = self.request.files.get('csv')
        if not csv_data:
            return self.render('addresses/upload_addresses.html')

        upload_file, = csv_data
        reader = csv.reader(self.bytes_split(upload_file['body'], '\n'), delimiter='\t')
        self.import_addresses(reader)

        self.redirect("/")


class AddressSearchHandler(AddressImportHandler):

    """Search for addresses using the Overpass API."""

    url = '/addresses/search'

    BAD_BOUNDING_BOX = 'bad bounding args'
    OVERSIZED_BOUNDING_BOX = 'the provided bounding box is too large'
    NO_BOUNDING_BOX = 'no bounding box'
    BAD_COORDS = 'invalid coordinartes provided'

    @authenticated
    @gen.coroutine
    def post(self):
        """Find all addresses within the given bounding box."""
        is_admin = self.is_admin
        if not is_admin:
            raise HTTPError(403)

        try:
            north = float(self.get_argument('north'))
            south = float(self.get_argument('south'))
            east = float(self.get_argument('east'))
            west = float(self.get_argument('west'))
        except ValueError:
            raise HTTPError(400, reason=self.BAD_BOUNDING_BOX)

        if not all([-90.0 < north < 90.0, -90.0 < south < 90.0, -180.0 < east < 180.0, -180.0 < west < 180.0]):
            raise HTTPError(400, reason=self.BAD_COORDS)

        if abs(north) - abs(south) + abs(east) - abs(west) > 0.05:
            raise HTTPError(400, reason=self.OVERSIZED_BOUNDING_BOX)

        self.import_addresses(find_addresses((south, west, north, east)))

        url_params = urlencode({'north': north, 'south': south, 'east': east, 'west': west})
        self.redirect(self.reverse_url('list_addresses') + '?' + url_params)
