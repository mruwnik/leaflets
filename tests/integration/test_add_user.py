import pytest

from mock import Mock, patch

from leaflets.views import AddUserHandler
from leaflets.views import BaseHandler


@pytest.mark.gen_test
def test_add_user(xsrf_client, base_url, app, database):
    """Check whether users get correctly added."""
    url = app.reverse_url('add_user')

    async def add_user(password, users_count):
        """Attempt to add a new user and validate the result."""
        post_data = {
            'name': 'test',
            'password': password,
            'password_repeat': 'test',
            'email': 'test@test.vl'
        }
        request = await xsrf_client.xsrf_request(base_url + url, post_data)
        response = await xsrf_client.fetch(request)

        assert response.code == 200

        with database.cursor() as c:
            c.execute("SELECT count(*) FROM users WHERE username = %s", ('test',))
            amount, = c.fetchone()
        assert amount == users_count

        if not users_count:
            assert AddUserHandler.PASSWORD_MISMATCH in str(response.body)
            assert response.effective_url == url
        else:
            assert response.effective_url == base_url

    # try to add a user with a password mistmatch - it shouldn't pass
    add_user('bla', 0)

    # matching passwords - the user should be added
    add_user('test', 1)


@pytest.mark.gen_test
def test_admin_user(app, database):
    """Check whether users get correctly added."""

    async def add_user(is_admin):
        """Add a new user to the database."""
        with database.cursor() as c:
            c.execute('DELETE FROM users')
            c.execute("INSERT INTO users (id, name, email, password_hash, admin) VALUES "
                      "(1, 'test', 'test@asd.sd', 'test', %s)", (is_admin,))

    def check_if_admin(expected):
        """Check if the current user is an admin."""
        with patch('leaflets.views.BaseHandler.get_current_user', return_value=1):
            handler = BaseHandler(app, Mock())
            is_admin = yield handler.is_admin
            assert is_admin is expected

    # no user in the database - not admin
    check_if_admin(False)

    for is_admin in True, False:
        add_user(is_admin)
        check_if_admin(is_admin)
