import pytest

from leaflets.forms.auth import AddUserForm


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

