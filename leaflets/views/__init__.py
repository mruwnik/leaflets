from leaflets.views.adresses import CSVImportHandler, AddressListHandler, AddressSearchHandler, AddressImportHandler
from leaflets.views.base import BaseHandler
from leaflets.views.campaign import (
    AddCampaignHandler, ListCampaignsHandler, ShowCampaignsHandler, CampaignAddressesHandler,
    MarkCampaignHandler, EditCampaignHandler,
)
from leaflets.views.users import LoginHandler, LogOutHandler, AddUserHandler, UsersListHandler, EditUserHandler


handlers = (
    LoginHandler, LogOutHandler, AddUserHandler, BaseHandler, MarkCampaignHandler,
    AddressSearchHandler, AddressImportHandler, AddressListHandler, CSVImportHandler,
    AddCampaignHandler, ListCampaignsHandler, ShowCampaignsHandler, CampaignAddressesHandler,
    EditCampaignHandler, UsersListHandler, EditUserHandler
)


__all__ = (
    LoginHandler, LogOutHandler, AddUserHandler, BaseHandler, MarkCampaignHandler,
    AddressSearchHandler, AddressImportHandler, AddressListHandler, CSVImportHandler,
    AddCampaignHandler, ListCampaignsHandler, ShowCampaignsHandler, CampaignAddressesHandler,
    EditCampaignHandler, UsersListHandler, EditUserHandler,
    handlers
)
