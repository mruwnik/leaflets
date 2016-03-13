from sqlalchemy.exc import IntegrityError
from tornado import gen
from tornado.web import authenticated, HTTPError

from leaflets.views.base import BaseHandler
from leaflets.views.adresses.address_utils import as_dict
from leaflets.forms.campaign import CampaignForm
from leaflets.models import Campaign, CampaignAddress, AddressStates
from leaflets import database


class AddCampaignHandler(BaseHandler):
    """Create new campaigns."""

    url = '/campaign/add'

    def get(self):
        self.render('campaign/add.html', form=CampaignForm())

    @authenticated
    @gen.coroutine
    def post(self):
        form = CampaignForm(self.request.arguments)
        if not form.validate():
            return self.render('campaign/add.html', form=form)

        try:
            form.save(self.get_current_user())
        except IntegrityError:
            form.name.errors += ['There already is a campaign with this name']
            self.render('campaign/add.html', form=form)

        self.redirect(self.reverse_url('list_campaigns'))


class ListCampaignsHandler(BaseHandler):
    """Show all campaigns for the given user."""

    url = '/campaign/list'

    @authenticated
    def get(self):
        self.render(
            'campaign/list.html',
            campaigns=Campaign.query.filter(Campaign.user_id == self.get_current_user()).all()
        )


class CampaignHandler(BaseHandler):
    """The base class for campaign handlers."""

    @property
    def campaign(self):
        """Get the campaign to be shown."""
        campaign = Campaign.query.filter(
            Campaign.id == self.get_argument('campaign'),
            Campaign.user_id == self.get_current_user()
        ).scalar()

        if not campaign:
            raise HTTPError(403, reason='No such campaign found')
        return campaign


class ShowCampaignsHandler(CampaignHandler):
    """Show a given campaign."""

    url = '/campaign'

    @authenticated
    def get(self):
        self.render('campaign/show.html', campaign=self.campaign)


class CampaignAddressesHandler(CampaignHandler):
    """Get a campaign's addresses."""

    url = '/campaign/addresses'

    @authenticated
    def get(self):
        self.write(as_dict(self.campaign.addresses))

    @authenticated
    def post(self):
        is_selected = self.get_argument('selected')
        if is_selected is None:
            raise HTTPError(403, reason='No selection provided')

        campaign = self.campaign

        address = CampaignAddress.query.filter(
            CampaignAddress.campaign == campaign,
            CampaignAddress.address_id == self.get_argument('address')
        ).scalar()

        if not address:
            raise HTTPError(403, reason='No such address found')

        address.state = AddressStates.marked if is_selected else AddressStates.selected
        database.session.commit()
        self.write({'result': 'ok'})