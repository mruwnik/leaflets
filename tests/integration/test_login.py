
import pytest
from tornado.httpclient import HTTPRequest

from leaflets.views import LoginHandler


REQUIRED_FIELD = 'This field is required.'


@pytest.mark.gen_test
def test_login_page(http_client, base_url, app):
    """Check whether the login page works."""
    url = app.reverse_url('login')
    response = yield http_client.fetch(base_url + url)
    assert response.code == 200
    assert ('form action="%s" method="post">' % url) in str(response.body)


@pytest.mark.gen_test
@pytest.mark.parametrize('good_field', ('name', 'password'))
def test_login_bad_values(xsrf_client, base_url, app, good_field):
    """Check whether the login page validation works for empty fields."""
    url = base_url + app.reverse_url('login')

    post_data = {good_field: 'test'}
    request = yield xsrf_client.xsrf_request(url, post_data)
    response = yield xsrf_client.fetch(request)

    assert response.code == 200
    assert REQUIRED_FIELD in str(response.body)
    assert response.effective_url == url


@pytest.mark.gen_test
def test_login_password(xsrf_client, base_url, app, database):
    """Check whether the login page validates passwords."""
    url = app.reverse_url('login')

    async def attempt_login(will_fail):
        """Attempt to log in and validate the result."""
        post_data = {
            'name': 'test',
            'password': 'test'
        }
        request = await xsrf_client.xsrf_request(base_url + url, post_data)
        response = await xsrf_client.fetch(request)

        assert response.code == 200
        if will_fail:
            assert LoginHandler.BAD_PASSWORD in str(response.body)
            assert response.effective_url == url
        else:
            assert response.effective_url == base_url

    # no user in the database - login should fail
    attempt_login(will_fail=True)

    # The password is unhashed, so shouldn't match - login should fail
    with database.cursor() as c:
        c.execute("INSERT INTO users VALUES (12, 'test', 'test', 'test', False)")
        database.commit()

    attempt_login(will_fail=True)

    # update the user's password to be a valid hash - login should work
    with database.cursor() as c:
        c.execute('UPDATE users set password_hash=%s', (LoginHandler.hash('test'),))
        database.commit()

    attempt_login(will_fail=False)

