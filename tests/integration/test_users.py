import pytest

from bs4 import BeautifulSoup

from leaflets.models import User
from leaflets.views import UsersListHandler, EditUserHandler


@pytest.mark.gen_test
def test_edit_user(xsrf_client, base_url, app, db_session, admin, users):
    """Check whether users get correctly added."""
    async def edit_user(user, name, email, is_admin, is_equal=False, parent_id=admin.id):
        """Change the given user's parameters."""
        post_data = {
            'name': name,
            'email': email,
            'is_admin': is_admin,
            'is_equal': is_equal,
            'user_id': user.id
        }
        request = await xsrf_client.xsrf_request(base_url + EditUserHandler.url, post_data)
        response = await xsrf_client.fetch(request)

        assert response.code == 200
        db_session.commit()
        user = User.query.get(user.id)

        assert user.username == name
        assert user.email == email
        assert user.admin == is_admin
        assert user.parent_id == parent_id
        assert response.effective_url == base_url + UsersListHandler.url

    sample_user = User.query.filter(User.parent == admin, User.admin).first()
    child = sample_user.children[0]

    # update the child
    yield edit_user(child, 'wrar', 'bla4@ble.dfl', True, False, sample_user.id)
    yield edit_user(child, 'wrar', 'bla6@ble.dfl', True, True, sample_user.parent_id)

    # update the selected user
    yield edit_user(sample_user, 'wrar2', 'bla@ble.dfl', False)
    yield edit_user(sample_user, 'wrar2', 'bla1@ble.dfl', True)
    yield edit_user(sample_user, 'wrar2', 'bla2@ble.dfl', True, True, None)


@pytest.mark.gen_test
def test_users_list(http_client, base_url, app, db_session, users, admin):
    """Check whether users get correctly added."""

    response = yield http_client.fetch(base_url + UsersListHandler.url)
    soup = BeautifulSoup(response.body, 'html.parser')

    def parse_children(user_div):
        """Get all children from the given div."""
        info = user_div.find(attrs={'class': 'user-info'})
        _, user_id = info.find('a').attrs['href'].split('=')

        children, children_div = {}, user_div.find(attrs={'class': 'children'})
        if children_div:
            children = dict(map(
                parse_children,
                children_div.findChildren(attrs={'class': 'user'}, recursive=False)
            ))

        return int(user_id), {
            'name': info.find('a').text.strip(),
            'email': info.find('span').text.strip()[1:-1],
            'children': children
        }

    def check_children(user, attrs):
        """Check whether all children of the given user are on the page.

        :param User user: the user to be checked
        :param dict attrs: {name, email, children} of the user
        """
        assert user.username == attrs['name']
        assert user.email == attrs['email']

        assert len(user.children) == len(attrs['children'])
        for child in user.children:
            check_children(child, attrs['children'][child.id])

    user_id, attrs = parse_children(soup.find(attrs={'class': 'user'}))

    assert user_id == admin.id
    check_children(admin, attrs)
