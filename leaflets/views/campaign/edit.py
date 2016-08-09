from collections import defaultdict
from sqlalchemy.exc import IntegrityError
from tornado import gen
from tornado.web import authenticated, HTTPError, MissingArgumentError

from leaflets.views.base import BaseHandler
from leaflets.views.campaign.handle import CampaignHandler, CampaignAddressesHandler
from leaflets.views.adresses.parse import BoundingBox
from leaflets.forms.campaign import CampaignForm
from leaflets.models import CampaignAddress, Address
from leaflets import database


class ListCampaignsHandler(BaseHandler):
    """Show all campaigns for the given user."""

    url = '/campaign/list'

    @authenticated
    def get(self):
        user = self.current_user_obj

        if not user.admin and len(user.campaigns + user.parent_campaigns) == 1:
            self.redirect('/campaign/%d' % user.first_campaign.id)
        else:
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

    url = '/campaign/edit/(\d+)'
    name = 'edit_campaign'

    def get(self, campaign_id):
        campaign = self.get_campaign(campaign_id)
        form = CampaignForm(
            name=campaign.name,
            desc=campaign.desc,
            start=campaign.start,
            addresses=[address.id for address in campaign.addresses]
        )
        self.render('campaign/add_edit.html', form=form, campaign=campaign, view='edit_campaign')

    @authenticated
    @gen.coroutine
    def post(self, campaign_id):
        form = CampaignForm(self.request.arguments)
        if not form.validate():
            return self.render('campaign/add_edit.html', form=form)

        try:
            form.update(self.campaign)
        except IntegrityError:
            form.name.errors += ['There already is a campaign with this name']
            self.render('campaign/add_edit.html', form=form)

        self.redirect(ListCampaignsHandler.url)


class AssignCampaignHandler(CampaignHandler):
    """Assign users to Addresses."""

    url = '/campaign/assign/(map|list)'
    name = 'assign_campaign'

    def get(self, view_type):
        self.render(
            'campaign/assign-%s.html' % view_type, campaign=self.campaign)


class UserAssignCampaignHandler(CampaignAddressesHandler, BoundingBox):

    url = '/campaign/assign_user'

    def mark_address(self, user_id, address_id):
        """
        Mark the given address as being assigned to the given user.

        :param int user_id: the id of the user
        :param int address_id: the id of the address
        """
        address = CampaignAddress.query.filter(
            CampaignAddress.campaign == self.campaign,
            CampaignAddress.address_id == int(self.get_argument('address'))
        ).scalar()

        if not address:
            raise HTTPError(403, reason=self.locale.translate('No such address found'))

        address.user_id = user_id
        database.session.commit()

        self.write({'result': 'ok'})

    def bulk_mark_addresses(self, user_id, bounds):
        """Mark all addresses within the provided bounds as assigned to the given user.

        :param int user_id: the id of the user. If not an int, all addresses will be unassigned
        :param tuple bounds: (south, west, north, east)
        """
        south, west, north, east = bounds

        addresses = database.session.query(CampaignAddress).join(Address).filter(
            CampaignAddress.campaign == self.campaign,
            Address.lat >= south,
            Address.lat <= north,
            Address.lon >= west,
            Address.lon <= east,
        )

        try:
            user_id = int(user_id)
        except ValueError:
            user_id = None

        for address in addresses:
            address.user_id = user_id
        database.session.commit()

        self.write({addr.address_id: addr.serialised_address() for addr in addresses})

    @authenticated
    @gen.coroutine
    def post(self):
        """Mark or unmark an address in the given campaign."""
        try:
            user_id = self.get_argument('userId')
        except MissingArgumentError:
            raise HTTPError(403, reason=self.locale.translate('No user id provided'))

        address_id = self.get_argument('address', None)
        if address_id:
            self.mark_address(user_id, address_id)
        elif self.get_argument('south', None) is not None:
            self.bulk_mark_addresses(user_id, self.get_bounds())
