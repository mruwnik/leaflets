import pytest

from leaflets.forms import LoginForm
from leaflets.models import User


REQUIRED_FIELD = 'This field is required.'


def test_no_name_given():
    """Check that the name is required."""
    form = LoginForm(password='asd')
    assert not form.validate()
    assert form.errors == {'name': [REQUIRED_FIELD]}


def test_no_password_given():
    """Check that the password is required."""
    form = LoginForm(name='asd')
    assert not form.validate()
    assert form.errors == {'password': [REQUIRED_FIELD]}


def test_full_form():
    form = LoginForm(name='asd', password='asd')
    assert form.validate()
    assert not form.errors


@pytest.mark.parametrize('value, hash', (
    ('', 'cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e'),  # noqa
    ('123', '3c9909afec25354d551dae21590bb26e38d53f2173b8d3dc3eee4c047e7ab1c1eb8b85103e3be7ba613b31bb5c9c36214dc9f14a42fd7a2fdb84856bca5c44c2'),  # noqa
    (';lk;sdkg;sdlfgk;lk;lk', '51243e117ec656ff3eb9577c418e7bfc2a3ede9b6f20bdb2959186a359c933952a292b1476157151a7e0c9348488fd8f288391d4b3b0691d70530fc485e4d294'),  # noqa
    ('password', 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'),  # noqa
))
def test_get_hash(value, hash):
    """Make sure that hashes are correctly calculated."""
    assert User.hash(value) == hash

