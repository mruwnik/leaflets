from sqlalchemy.exc import IntegrityError
from tornado import gen
from tornado.web import authenticated

from leaflets.views.base import BaseHandler
from leaflets.views.campaign.handle import CampaignHandler
from leaflets.forms.campaign import CampaignForm


class ListCampaignsHandler(BaseHandler):
    """Show all campaigns for the given user."""

    url = '/campaign/list'

    @authenticated
    def get(self):
        user = self.current_user_obj
        self.render(
            'campaign/list.html',
            campaigns=[
                ('user_campaigns', user.campaigns),
                ('parent_campaigns', user.parent_campaigns),
                ('children_campaigns', user.children_campaigns),
            ],
        )


class AddCampaignHandler(BaseHandler):
    """Create new campaigns."""

    url = '/campaign/add'

    def get(self):
        self.render('campaign/add_edit.html', form=CampaignForm(), view='add_campaign')

    @authenticated
    @gen.coroutine
    def post(self):
        form = CampaignForm(self.request.arguments)
        if not form.validate():
            return self.render('campaign/add_edit.html', form=form, view='add_campaign')

        try:
            form.save(self.get_current_user())
        except IntegrityError:
            form.name.errors += ['There already is a campaign with this name']
            self.render('campaign/add_edit.html', form=form, view='add_campaign')

        self.redirect(ListCampaignsHandler.url)


class EditCampaignHandler(CampaignHandler):
    """Edit a campaign."""

    url = '/campaign/edit'

    def get(self):
        campaign = self.campaign
        form = CampaignForm(
            name=campaign.name,
            desc=campaign.desc,
            start=campaign.start,
            addresses=[address.id for address in campaign.addresses]
        )
        self.render('campaign/add_edit.html', form=form, campaign=campaign, view='edit_campaign')

    @authenticated
    @gen.coroutine
    def post(self):
        form = CampaignForm(self.request.arguments)
        if not form.validate():
            return self.render('campaign/add_edit.html', form=form)

        try:
            form.update(self.campaign)
        except IntegrityError:
            form.name.errors += ['There already is a campaign with this name']
            self.render('campaign/add_edit.html', form=form)

        self.redirect(ListCampaignsHandler.url)
