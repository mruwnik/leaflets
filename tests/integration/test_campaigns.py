from datetime import datetime, timedelta

import pytest

from leaflets.views import AddCampaignHandler
from leaflets.models import Campaign


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
    assert campaign.user_id == admin

    # check whether all addresses were attached
    for addr in campaign.addresses:
        assert addr.id in address_ids
