from datetime import datetime

from leaflets.forms.campaign import CampaignForm


REQUIRED_FIELD = 'This field is required.'


def assert_field(name='test', desc='test', start=datetime.utcnow(), addresses=[1, 2, 3, 4], errors=None):
    """Fill a CampaignForm with the provided fields and check if the errors match."""
    form = CampaignForm(name=name, desc=desc, start=start, addresses=addresses)
    if errors is None:
        assert form.validate()
    else:
        assert not form.validate()
        assert form.errors == errors


def test_name():
    """Make sure that the name is required."""
    assert_field(name=None, errors={'name': [REQUIRED_FIELD]})
    assert_field(name='test')


def test_addresses():
    """Check whether addresses are validated."""
    assert_field(addresses=[1, 3, 4, 5])
    assert_field(addresses=[], errors={'addresses': ['No addresses selected']})
