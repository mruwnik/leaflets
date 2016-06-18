import random

import pytest

from bs4 import BeautifulSoup

from leaflets.models import User
from leaflets.views import UsersListHandler, EditUserHandler


@pytest.mark.gen_test
def test_edit_user(xsrf_client, base_url, app, db_session, admin, users):
    """Check whether users get correctly added."""
    async def edit_user(user, name, email, is_admin):
        """Change the given user's parameters."""
        post_data = {
            'name': name,
            'email': email,
            'is_admin': is_admin,
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
        assert response.effective_url == base_url + UsersListHandler.url

    sample_user = User.query.filter(User.parent == admin, User.admin).first()
    child = sample_user.children[0]

    # update the child
    yield edit_user(child, 'wrar', 'bla4@ble.dfl', True)

    # update the selected user
    yield edit_user(sample_user, 'wrar2', 'bla@ble.dfl', False)
    yield edit_user(sample_user, 'wrar2', 'bla1@ble.dfl', True)
    yield edit_user(sample_user, 'wrar2', 'bla2@ble.dfl', True)


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
            'name': info.find('span', attrs={'class', 'name'}).text.strip(),
            'email': info.find('span', attrs={'class', 'email'}).text.strip()[1:-1],
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


@pytest.mark.gen_test
def test_move_user(xsrf_client, base_url, app, db_session, admin, users):
    """Check whether moving users around works."""
    async def move_user(user, target):
        post_data = {
            'user': user.id,
            'target': target.id,
        }
        request = await xsrf_client.xsrf_request(base_url + UsersListHandler.url, post_data)
        response = await xsrf_client.fetch(request)

        assert response.code == 200
        db_session.commit()
        user = User.query.get(user.id)

        assert user.parent_id == target.id
        assert response.effective_url == base_url + UsersListHandler.url
        return admin

    initial_children_amount = len(admin.children)
    last_child = admin.children[-1]
    for child in admin.children[:3]:
        yield move_user(child, last_child)

    admin = User.query.get(admin.id)
    assert len(admin.children) == initial_children_amount - 3

    for child in admin.children[-1].children[:3]:
        yield move_user(child, admin)

    admin = User.query.get(admin.id)
    assert len(admin.children) == initial_children_amount
