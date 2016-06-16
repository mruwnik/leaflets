import json
from collections import defaultdict

from tornado import gen
from tornado.web import authenticated, HTTPError
from tornado.websocket import WebSocketHandler, WebSocketClosedError
from sqlalchemy import or_

from leaflets.views.base import BaseHandler
from leaflets.models import Campaign, CampaignAddress, Address
from leaflets import database


class CampaignHandler(BaseHandler):
    """The base class for campaign handlers."""

    @property
    def campaign(self):
        """Get the campaign to be shown."""
        user = self.current_user_obj
        campaign = Campaign.query.get(self.get_argument('campaign'))

        if not campaign or campaign not in user.campaigns + user.parent_campaigns + user.children_campaigns:
            raise HTTPError(403, reason=self.locale.translate('No such campaign found'))
        return campaign

    @property
    def addrs(self):
        """Get all addresses for the given campaign."""
        user = self.current_user_obj
        return CampaignAddress.query.filter(
            CampaignAddress.campaign == self.campaign,
            or_(
                CampaignAddress.user_id.in_(
                    [user.id] + [u.id for u in user.descendants + user.ancestors]),
                CampaignAddress.user_id == None
            )
        )

    @authenticated
    @gen.coroutine
    def post(self):
        """Mark or unmark an address in the given campaign."""
        state = self.get_argument('state')
        if state is None:
            raise HTTPError(403, reason=self.locale.translate('No selection provided'))

        campaign = self.campaign

        address = CampaignAddress.query.filter(
            CampaignAddress.campaign == campaign,
            CampaignAddress.address_id == int(self.get_argument('address'))
        ).scalar()

        if not address:
            raise HTTPError(403, reason=self.locale.translate('No such address found'))

        address.state = state
        database.session.commit()

        MarkCampaignHandler.broadcast(json.dumps(address.serialised_address()))

        self.write({'result': 'ok'})


class ShowCampaignHandler(CampaignHandler):
    """Show a given campaign."""

    url = '/campaign'
    name = 'show_campaign'

    @authenticated
    def get(self):
        addrs_tree = defaultdict(lambda: defaultdict(lambda: defaultdict(CampaignAddress)))
        for address in self.addrs:
            addr = address.address
            addrs_tree[addr.town][addr.street][addr.house] = address

        self.render(
            'campaign/show-list.html',
            campaign=self.campaign,
            addrs_tree=addrs_tree,
        )


class ShowCampaignMapHandler(CampaignHandler):
    """Show a given campaign."""

    url = '/campaign_map'
    name = 'show_campaign_map'

    @authenticated
    def get(self):
        self.render('campaign/show-map.html', campaign=self.campaign)


class CampaignAddressesHandler(WebSocketHandler, CampaignHandler):
    """Get a campaign's addresses."""

    url = '/campaign/addresses'

    @authenticated
    def get(self):
        """Get all addresses for this campaign that the user can see."""
        self.write({addr.address_id: addr.serialised_address() for addr in self.addrs})


class MarkCampaignHandler(WebSocketHandler, CampaignHandler):

    url = '/campaign/mark'
    handlers = []

    @authenticated
    def open(self):
        """Add the handler to the list of active handlers."""
        MarkCampaignHandler.handlers.append(self)

    def write_error(self, error_msg):
        """Send an error message as a json object.

        :param str error_msg: the message to be sent
        """
        self.write_message(json.dumps({'error': self.locale.translate(error_msg)}))

    @classmethod
    def broadcast(cls, message):
        """Send the provided message to all handlers.

        :param str message: the message to be send
        """
        for handler in cls.handlers:
            try:
                handler.write_message(message)
            except WebSocketClosedError as e:
                cls.remove_handler(handler)

    @authenticated
    @gen.coroutine
    def on_message(self, message):
        """Handle an address being selected.

        :param str message: the json encoded parameters of the address
        """
        try:
            message = json.loads(message)
            state = message.get('state')
            address_id = message.get('address')
            campaign_id = message.get('campaign')
        except (json.decoder.JSONDecodeError, AttributeError):
            return self.write_error('invalid_json')

        if state is None:
            return self.write_error('No selection provided')

        address = CampaignAddress.query.filter(
            CampaignAddress.campaign_id == campaign_id,
            CampaignAddress.address_id == address_id
        ).scalar()

        if not address:
            return self.write_error('No such address found')

        address.state = state
        database.session.commit()

        self.broadcast(json.dumps(address.serialised_address()))

    @classmethod
    def remove_handler(cls, handler):
        """Remove the provided handler from the list of handlers.

        :param WebSocketHandler handler: the handler to be removed.
        """
        try:
            index = cls.handlers.index(handler)
            cls.handlers = cls.handlers[:index] + cls.handlers[index + 1:]
        except ValueError:
            pass

    def on_close(self):
        """Remove this handler."""
        self.remove_handler(self)
