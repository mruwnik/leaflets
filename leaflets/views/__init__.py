from leaflets.views.auth import LoginHandler, LogOutHandler
from leaflets.views.add_user import AddUserHandler
from leaflets.views.base import BaseHandler
from leaflets.views.adresses import CSVImportHandler, AddressListHandler, AddressSearchHandler, AddressImportHandler
from leaflets.views.campaign import (
    AddCampaignHandler, ListCampaignsHandler, ShowCampaignsHandler, CampaignAddressesHandler, MarkCampaignHandler
)


handlers = (
    LoginHandler, LogOutHandler, AddUserHandler, BaseHandler, MarkCampaignHandler,
    AddressSearchHandler, AddressImportHandler, AddressListHandler, CSVImportHandler,
    AddCampaignHandler, ListCampaignsHandler, ShowCampaignsHandler, CampaignAddressesHandler
)


__all__ = (
    LoginHandler, LogOutHandler, AddUserHandler, BaseHandler, MarkCampaignHandler,
    AddressSearchHandler, AddressImportHandler, AddressListHandler, CSVImportHandler,
    AddCampaignHandler, ListCampaignsHandler, ShowCampaignsHandler, CampaignAddressesHandler,
    handlers
)
