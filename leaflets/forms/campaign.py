from datetime import datetime

from wtforms import StringField, DateTimeField, SelectMultipleField
from wtforms.validators import DataRequired
from wtforms_tornado import Form


class CampaignForm(Form):

    def __init__(self, *args, **kwargs):
        super(CampaignForm, self).__init__(*args, **kwargs)
        try:
            if args:
                addresses = args[0].get('addresses[]', [])
            else:
                addresses = kwargs.get('addresses', [])

            addresses = list(map(int, addresses))
            self.addresses.data = addresses
            self.addresses.choices = [(a, a) for a in addresses]
        except (TypeError, IndexError):
            self.addresses.data = self.addresses.choices = []

    name = StringField('name', validators=[DataRequired()])
    desc = StringField('desc')
    start = DateTimeField('start', default=datetime.now())
    addresses = SelectMultipleField('addresses[]', validators=[DataRequired('No addresses selected')])
