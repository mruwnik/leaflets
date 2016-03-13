from tornado import gen
from tornado.web import authenticated

from leaflets.views.base import BaseHandler
from leaflets.forms.campaign import CampaignForm


class AddCampaignHandler(BaseHandler):
    """Create new campaigns."""

    url = '/campaign/add'

    def get(self):
        self.render('add_campaign.html', form=CampaignForm())

    @authenticated
    @gen.coroutine
    def post(self):
        form = CampaignForm(self.request.arguments)
        if not form.validate():
            return self.render('add_campaign.html', form=form)

        form.save(self.get_current_user())
        self.render('add_campaign.html', form=form)
