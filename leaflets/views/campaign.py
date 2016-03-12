from tornado import gen

from leaflets.views.base import BaseHandler
from leaflets.forms.campaign import CampaignForm


class AddCampaignHandler(BaseHandler):

    url = '/campaign/add'

    def get(self):
        self.render('add_campaign.html', form=CampaignForm())

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
        form = CampaignForm(self.request.arguments)
        if not form.validate():
            return self.render('add_campaign.html', form=form)

        self.render('add_campaign.html', form=form)

