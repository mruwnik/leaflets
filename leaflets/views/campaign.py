from tornado import gen

from leaflets.views.base import BaseHandler


class AddCampaignHandler(BaseHandler):

    url = '/campaign/add'

    def get(self):
        self.render('add_campaign.html', name='', addresses=[])

    @gen.coroutine
    def get_user(self, form):
        """Get the user from the provided form.

        :param LoginForm form: the login form
        :returns: the user's id, or None if could be found
        """
        result = yield self.application.db.execute(
            'SELECT id FROM users WHERE username = %s AND password_hash = %s',
            (form.name.data, self.hash(form.password.data))
        )
        user_id = result.fetchone()
        raise gen.Return(user_id and user_id[0])

    @gen.coroutine
    def post(self):
        name = self.get_argument('name')
        addresses = self.get_arguments('addresses[]')

        if not name or not addresses:
            return self.render('add_campaign.html', name=name, addresses=addresses)

        self.render('add_campaign.html', name=name, addresses=addresses)

