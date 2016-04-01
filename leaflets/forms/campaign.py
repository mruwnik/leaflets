from datetime import datetime

from wtforms import StringField, DateTimeField, SelectMultipleField
from wtforms.validators import DataRequired
from wtforms_tornado import Form

from leaflets.models import CampaignAddress, Campaign
from leaflets import database


class CampaignForm(Form):

    name = StringField('campaign_name', validators=[DataRequired()])
    desc = StringField('description')
    start = DateTimeField('start_date', default=datetime.now())
    addresses = SelectMultipleField('addresses[]', validators=[DataRequired('No addresses selected')])

    def __init__(self, *args, **kwargs):
        """Initialise this form."""
        super(CampaignForm, self).__init__(*args, **kwargs)

        # set up the addresses field. This is done this way, as the addresses are
        # a variable list of hidden fields, so there is no decent way to set them up
        # as a static field
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

    def save(self, user_id):
        """Save the campaign in this form to the database.

        :param int user_id: the id of the user to which this campaign should be attached.
        :return: the resulting campaign
        """
        campaign = Campaign(
            name=self.name.data,
            desc=self.desc.data,
            start=self.start.data,
            user_id=user_id,
        )
        database.session.add(campaign)
        for addr_id in self.addresses.data:
            database.session.add(
                CampaignAddress(campaign=campaign, address_id=addr_id))
        database.session.commit()
        return campaign

    def update(self, campaign):
        """Update the given campaign.

        :param campaign: the campaign to be updated
        :return: the campaign
        """
        campaign.name = self.name.data
        campaign.desc = self.desc.data
        campaign.start = self.start.data

        selected_ids = set(map(int, self.addresses.data))

        for addr in campaign.campaign_addresses:
            if addr.address_id not in selected_ids:
                database.session.delete(addr)

        campaign_addresses = {addr.address_id for addr in campaign.campaign_addresses}
        for addr_id in selected_ids - campaign_addresses:
            database.session.add(
                CampaignAddress(campaign=campaign, address_id=addr_id))
        database.session.commit()
        return campaign
