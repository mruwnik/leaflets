import json
from datetime import datetime, timedelta
from random import choice

import pytest
from tornado.websocket import websocket_connect

from leaflets.views import (
    AddCampaignHandler, CampaignAddressesHandler, MarkCampaignHandler, EditCampaignHandler, AssignCampaignHandler
)
from leaflets.models import Campaign, AddressStates, Address


@pytest.mark.gen_test
def test_add_campaign(xsrf_client, base_url, db_session, addresses, admin):
    """Check whether campaigns are correctly created."""
    url = base_url + AddCampaignHandler.url
    now = datetime.utcnow().replace(microsecond=0)
    start = now + timedelta(days=2)
    address_ids = [addr.id for addr in addresses]

    # send a create campaign request
    post_data = {
        'name': 'test',
        'desc': 'description',
        'start': start.strftime("%Y-%m-%d %H:%M:%S"),
        'addresses[]': address_ids,
    }
    request = yield xsrf_client.xsrf_request(url, post_data)
    response = yield xsrf_client.fetch(request)

    assert response.code == 200

    # refresh the session
    db_session.commit()

    # check whether the campaign was created
    campaign = Campaign.query.one()
    assert campaign.name == 'test'
    assert campaign.desc == 'description'
    assert campaign.start == start
    assert now <= campaign.created <= datetime.utcnow()
    assert campaign.user.id == admin.id

    # check whether all addresses were attached
    for addr in campaign.addresses:
        assert addr.id in address_ids


@pytest.mark.gen_test
def test_edit_campaign(xsrf_client, base_url, db_session, addresses, campaign, admin):
    """Check whether campaigns are correctly edited."""
    url = base_url + EditCampaignHandler.url
    start = campaign.start + timedelta(days=2)

    # add an extra address to see if it will be added to the campaign
    added_address = Address(lat=1, lon=2, town='bla', postcode='23432', street='few', house='23')
    db_session.add(added_address)
    db_session.commit()

    # change what addresses are attached to the campaign
    new_addresses = addresses[::2] + [added_address]
    address_ids = [addr.id for addr in new_addresses]

    # send an edit campaign request
    post_data = {
        'name': 'new test',
        'desc': 'new description',
        'start': start.strftime("%Y-%m-%d %H:%M:%S"),
        'addresses[]': address_ids,
        'campaign': campaign.id,
    }
    request = yield xsrf_client.xsrf_request(url, post_data)
    response = yield xsrf_client.fetch(request)

    assert response.code == 200

    # refresh the session
    db_session.commit()
    campaign = Campaign.query.get(campaign.id)
    # check whether the campaign was updated
    assert campaign.name == 'new test'
    assert campaign.desc == 'new description'
    assert campaign.start == start.replace(microsecond=0)
    assert campaign.user.id == admin.id

    # check whether all addresses were attached
    assert set(address_ids) == {addr.id for addr in campaign.addresses}


@pytest.mark.gen_test
def test_get_campaign_addresses(http_client, base_url, db_session, campaign, admin):
    """Check whether fetching all addresses for a given campaign works."""
    url = base_url + CampaignAddressesHandler.url

    response = yield http_client.fetch(url + '?campaign=%d' % campaign.id)
    assert response.code == 200

    addresses = json.loads(response.body.decode('utf8'))
    assert addresses
    assert {str(c.address_id): c.serialised_address() for c in campaign.campaign_addresses} == addresses


@pytest.mark.gen_test
def test_post_campaign_addresses_state(xsrf_client, base_url, db_session, campaign, admin):
    """Check whether setting an address' state works."""
    url = base_url + CampaignAddressesHandler.url

    def check_address_state(address, state):
        """Update the given address with the given state."""
        post_data = {
            'campaign': campaign.id,
            'address': address.id,
            'state': state,
        }
        request = yield xsrf_client.xsrf_request(url, post_data)
        response = yield xsrf_client.fetch(request)

        assert response.code == 200
        db_session.commit()

        assert address.state == state

    states = [AddressStates.selected, AddressStates.marked, AddressStates.removed]
    # go through all addresses and set all states
    for state in states:
        for addr in campaign.addresses:
            addr.state = choice(states)
            db_session.commit()
            check_address_state(addr, state)


@pytest.mark.gen_test
def test_websocket_campaign_addresses_state(xsrf_client, base_url, db_session, campaign, admin):
    """Check whether setting a state via websockets works."""
    conn = yield websocket_connect(base_url.replace('http', 'ws') + MarkCampaignHandler.url)

    def check_change_state(addr, state):
        conn.write_message(json.dumps({
            'campaign': campaign.id,
            'address': addr.address_id,
            'state': state
        }))
        msg = yield conn.read_message()
        assert json.loads(msg) == addr.serialised_address()

    states = [AddressStates.selected, AddressStates.marked, AddressStates.removed]
    for state in states:
        for addr in campaign.campaign_addresses:
            addr.state = choice(states)
            db_session.commit()
            check_change_state(addr, state)


@pytest.mark.gen_test
def test_websocket_campaign_addresses_broadcast(xsrf_client, base_url, db_session, campaign, admin):
    """Check whether all handlers receive broadcasts."""
    conns = []
    for conn in range(10):
        conn = yield websocket_connect(base_url.replace('http', 'ws') + MarkCampaignHandler.url)
        conns.append(conn)

    addr = campaign.campaign_addresses[0]
    conn.write_message(json.dumps({
        'campaign': campaign.id,
        'address': addr.address_id,
        'state': AddressStates.selected
    }))

    for conn in conns:
        msg = yield conn.read_message()
        assert json.loads(msg) == addr.serialised_address()


@pytest.mark.gen_test
def test_assign_campaign_address(xsrf_client, base_url, db_session, campaign, admin, users):
    """Check whether setting an address' user works."""
    url = base_url + AssignCampaignHandler.url

    def check_address_assigned(address, user):
        """Update the given address with the given state."""
        post_data = {
            'campaign': campaign.id,
            'address': address.id,
            'userId': user.id,
        }
        request = yield xsrf_client.xsrf_request(url, post_data)
        response = yield xsrf_client.fetch(request)

        assert response.code == 200
        db_session.commit()

        assert address.userId == user.id

    address = campaign.campaign_addresses[0]

    for user in users:
        check_address_assigned(address, user)


@pytest.mark.gen_test
def test_assign_campaign_addresses(xsrf_client, base_url, db_session, campaign, admin, users):
    """Check whether setting an address' user works."""
    url = base_url + AssignCampaignHandler.url

    def check_addresses_assigned(user_id):
        """Update the given address with the given state."""
        post_data = {
            'campaign': campaign.id,
            'userId': user_id,
            'north': max([addr.lat for addr in campaign.addresses]),
            'south': min([addr.lat for addr in campaign.addresses]),
            'east': max([addr.lon for addr in campaign.addresses]),
            'west': min([addr.lon for addr in campaign.addresses]),
        }
        request = yield xsrf_client.xsrf_request(url, post_data)
        response = yield xsrf_client.fetch(request)

        assert response.code == 200
        db_session.commit()

        assert {addr.user_id for addr in campaign.campaign_addresses} == {user_id}

    # assign the same user to all addresses
    for user in users:
        check_addresses_assigned(user)

    # remove the user from all addresses
    check_addresses_assigned(None)
