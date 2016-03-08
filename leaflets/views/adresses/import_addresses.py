import csv
import re
import logging

from psycopg2 import IntegrityError
from tornado import gen
from tornado.web import authenticated, HTTPError

from leaflets.views.base import BaseHandler

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
        conn = yield self.application.db.connect()
        reader = csv.reader(self.bytes_split(upload_file['body'], '\n'), delimiter='\t')

        for row in reader:
            try:
                lat, lon, town, postcode, street, house = row
                yield conn.execute(
                    "INSERT INTO addresses (lat, lon, country, town, postcode, street, house) "
                    "VALUES (%s, %s, 'Polska', %s, %s, %s, %s)",
                    (float(lat), float(lon), town, postcode, street, house)
                )
            except (ValueError, TypeError, UnboundLocalError):
                logger.warn('invalid address provided: %s', row)
            except IntegrityError:
                logger.warn('found duplicate for %s', row)
        self.redirect("/")
