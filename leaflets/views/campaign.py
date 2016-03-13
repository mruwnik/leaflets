from sqlalchemy.exc import IntegrityError
from tornado import gen
from tornado.web import authenticated, HTTPError

from leaflets.views.base import BaseHandler
from leaflets.views.adresses.address_utils import as_dict
from leaflets.forms.campaign import CampaignForm
from leaflets.models import Campaign


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


class ShowCampaignsHandler(BaseHandler):
    """Show a given campaign."""

    url = '/campaign'

    @authenticated
    def get(self):
        campaign = Campaign.query.filter(
            Campaign.id == self.get_argument('campaign'),
            Campaign.user_id == self.get_current_user()
        ).scalar()

        if not campaign:
            raise HTTPError(403, reason='No such campaign found')

        self.render('campaign/show.html', campaign=campaign)


class CampaignAddressesHandler(BaseHandler):
    """Show a given campaign."""

    url = '/campaign/addresses'

    @authenticated
    def get(self):
        campaign = Campaign.query.filter(
            Campaign.id == self.get_argument('campaign_id'),
            Campaign.user_id == self.get_current_user()
        ).scalar()

        if not campaign:
            raise HTTPError(403, reason='No such campaign found')

        self.write(as_dict(campaign.addresses))
