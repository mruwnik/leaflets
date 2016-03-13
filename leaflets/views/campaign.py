from sqlalchemy.exc import IntegrityError
from tornado import gen
from tornado.web import authenticated

from leaflets.views.base import BaseHandler
from leaflets.forms.campaign import CampaignForm
from leaflets.models import Campaign


class AddCampaignHandler(BaseHandler):
    """Create new campaigns."""

    url = '/campaign/add'

    def get(self):
        self.render('campaign/add_campaign.html', form=CampaignForm())

    @authenticated
    @gen.coroutine
    def post(self):
        form = CampaignForm(self.request.arguments)
        if not form.validate():
            return self.render('add_campaign.html', form=form)

        try:
            form.save(self.get_current_user())
        except IntegrityError:
            form.name.errors += ['There already is a campaign with this name']
            self.render('add_campaign.html', form=form)

        self.redirect(self.reverse_url('list_campaigns'))


class ListCampaignsHandler(BaseHandler):
    """Show all campaigns for the given user."""

    url = '/campaign/list'

    @authenticated
    def get(self):
        self.render(
            'campaign/list_campaigns.html',
            campaigns=Campaign.query.filter(Campaign.user_id == self.get_current_user()).all()
        )
