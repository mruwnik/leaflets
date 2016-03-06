
import pytest
from tornado.httpclient import HTTPRequest

from leaflets.views import AddUserHandler


@pytest.mark.gen_test
def test_add_user(xsrf_client, base_url, app_with_db, database):
    """Check whether users get correctly added."""
    url = app_with_db.reverse_url('add_user')

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

