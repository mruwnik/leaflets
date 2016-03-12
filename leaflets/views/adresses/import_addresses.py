import csv
import re
import logging
from urllib.parse import urlencode

from psycopg2 import IntegrityError
from tornado import gen
from tornado.web import authenticated, HTTPError

from leaflets.views.base import BaseHandler
from leaflets.views.adresses.address_utils import find_addresses

logger = logging.getLogger()


class AddressImportHandler(BaseHandler):

    """Import address CSV files."""

    url = '/addresses/import'

    @authenticated
    def get(self):
        """Show the import form."""
        self.render('upload_addresses.html')

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
        is_admin = yield self.is_admin
        if not is_admin:
            raise HTTPError(403)

        csv_data = self.request.files.get('csv')
        if not csv_data:
            return self.render('upload_addresses.html')

        upload_file, = csv_data
        reader = csv.reader(self.bytes_split(upload_file['body'], '\n'), delimiter='\t')

        for row in reader:
            try:
                lat, lon, town, postcode, street, house = row
                yield self.application.db.execute(
                    "INSERT INTO addresses (lat, lon, country, town, postcode, street, house) "
                    "VALUES (%s, %s, 'Polska', %s, %s, %s, %s)",
                    (float(lat), float(lon), town, postcode, street, house)
                )
            except (ValueError, TypeError, UnboundLocalError):
                logger.warn('invalid address provided: %s', row)
            except IntegrityError:
                logger.warn('found duplicate for %s', row)

        self.redirect("/")


class AddressSearchHandler(BaseHandler):

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
        is_admin = yield self.is_admin
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

        for row in find_addresses((south, west, north, east)):
            try:
                lat, lon, town, postcode, street, house = row
                if not all([lat, lon, street, house]):
                    raise ValueError
                yield self.application.db.execute(
                    "INSERT INTO addresses (lat, lon, country, town, postcode, street, house) "
                    "VALUES (%s, %s, 'Polska', %s, %s, %s, %s)",
                    (float(lat), float(lon), town or '', postcode or '', street, house)
                )
            except (ValueError, TypeError, UnboundLocalError):
                logger.warn('invalid address found: %s', row)
            except IntegrityError:
                logger.warn('found a duplicate for %s', row)

        url_params = urlencode({'north': north, 'south': south, 'east': east, 'west': west})
        self.redirect(self.reverse_url('list_addresses') + '?' + url_params)
