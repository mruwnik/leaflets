from tornado.web import Application, url
from tornado import ioloop, httpserver

from leaflets.etc import options
from leaflets.views import (
    LoginHandler, BaseHandler, AddUserHandler, LogOutHandler, CSVImportHandler, AddressListHandler,
    AddCampaignHandler, AddressSearchHandler, AddressImportHandler, ListCampaignsHandler, ShowCampaignsHandler,
    CampaignAddressesHandler, uimodules
)


def setup_app():
    """Set the application up.

    :returns: the application instance
    """
    app = Application(
        [
            url(r"/", BaseHandler),
            url(LoginHandler.url, LoginHandler, name='login'),
            url(LogOutHandler.url, LogOutHandler, name='logout'),
            url(AddUserHandler.url, AddUserHandler, name='add_user'),

            url(AddressImportHandler.url, AddressImportHandler, name='import_addresses'),
            url(CSVImportHandler.url, CSVImportHandler, name='csv_addresses'),
            url(AddressListHandler.url, AddressListHandler, name='list_addresses'),
            url(AddressSearchHandler.url, AddressSearchHandler, name='search_addresses'),

            url(AddCampaignHandler.url, AddCampaignHandler, name='add_campaign'),
            url(ListCampaignsHandler.url, ListCampaignsHandler, name='list_campaigns'),
            url(ShowCampaignsHandler.url, ShowCampaignsHandler, name='show_campaign'),
            url(CampaignAddressesHandler.url, CampaignAddressesHandler, name='campaign_addresses'),
        ],
        debug=options.DEBUG,
        template_path=options.TEMPLATES,
        cookie_secret=options.SECRET_KEY,
        static_path=options.STATIC_FILES,
        xsrf_cookies=True,
        ui_methods=uimodules,
        login_url=LoginHandler.url,
    )
    return app


if __name__ == "__main__":
    import logging
    logging.basicConfig()

    app = setup_app()

    io_instance = ioloop.IOLoop.instance()

    http_server = httpserver.HTTPServer(app)
    http_server.listen(options.PORT)
    print('Starting application on port %d' % options.PORT)
    ioloop.IOLoop.current().start()

