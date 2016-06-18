import pytest
from wtforms.validators import ValidationError

from leaflets.forms.auth import AddUserForm, name_email, extract_emails, check_for_url, check_emails_provided


REQUIRED_FIELD = 'This field is required.'


@pytest.mark.parametrize('missing_field',
    ('name', 'password', 'password_repeat', 'email')
)
def test_all_fields_required(missing_field):
    """Make sure that all fields are required."""
    fields = {
        'name': 'test',
        'password': 'test',
        'password_repeat': 'test',
        'email': 'test@test.rp'
    }
    del fields[missing_field]
    form = AddUserForm(**fields)
    assert not form.validate()
    assert form.errors[missing_field] == [REQUIRED_FIELD]


@pytest.mark.parametrize('password, repeat_password', (
    ('test', ''),
    ('test', None),
    ('test', 'None'),
    ('test1', 'test'),
))
def test_passwords_must_match(password, repeat_password):
    """Make sure that the passwords must match."""
    form = AddUserForm(
        name='test',
        password=password,
        password_repeat=repeat_password,
        email='test@sdf.sd'
    )
    assert not form.validate()
    assert form.password.errors == [AddUserForm.PASSWORD_MISMATCH]


@pytest.mark.parametrize('address, expected', (
    ('asd@asd.com', ('', 'asd@asd.com')),
    ('      <bla@ble.bl>', ('', 'bla@ble.bl')),
    ('Wrar wrar <bla@ble.bl>', ('Wrar wrar', 'bla@ble.bl')),
    ('Wrar wrar <bla@ble.bl>   asd  asd', ('Wrar wrar', 'bla@ble.bl')),
    ('Wrar wrar <bla@ble.bl>asd  asd', ('Wrar wrar', 'bla@ble.bl')),
    ('Wrar wrar <bla@ble.bl', ('Wrar wrar', 'bla@ble.bl')),
    ('Wrar wrar bla@ble.bl', ('Wrar wrar', 'bla@ble.bl')),
))
def test_name_email(address, expected):
    """Check whether email addresses are correctly extracted."""
    assert name_email(address) == expected


@pytest.mark.parametrize('text, emails', (
    (
        'asd@ds.com; bla; fe; asd; Bla bla <wrar@ble.com>\nwr@ffa.com;bla+bla@co.com',
        ['asd@ds.com', 'Bla bla <wrar@ble.com>', 'wr@ffa.com', 'bla+bla@co.com']
    ), (
        # these are some corner cases which aren't really handled correctly
        '    aWd ds    <   bla@rea.re     >; asd; asd;      dsf@sd.d        asd;asd',
        ['aWd ds    <   bla@rea.re', 'dsf@sd.d']
    )
))
def test_extract_emails(text, emails):
    """Check whether extracting emails works."""
    assert extract_emails(text) == emails


class MockField(object):
    def __init__(self, data):
        self.data = data


@pytest.mark.parametrize('text', ('{url}', '{url}asd', 'asd{url}', 'asd{url}asd'))
def test_check_for_url_pass(text):
    """Check that no exception is raised for valid texts."""
    check_for_url(None, MockField(text))


def test_check_for_url_no_pass():
    """Check that an exception is raised for invalid texts."""
    with pytest.raises(ValidationError):
        check_for_url(None, MockField('text'))


@pytest.mark.parametrize('text', ('dwad ads asd@ds.com asdsa', 'Bla <a@d.com>; as ed@cin.sd'))
def test_check_emails_provided_pass(text):
    """Check that no exception is raised when emails are present."""
    check_emails_provided(None, MockField(text))


@pytest.mark.parametrize('text', ('dwad ads asdds.com asdsa', '@', '@asd.com', 'Bla <ad.com>; as ed@'))
def test_check_emails_provided_no_pass(text):
    """Check that no exception is raised when no emails are present."""
    with pytest.raises(ValidationError):
        check_emails_provided(None, MockField(text))
