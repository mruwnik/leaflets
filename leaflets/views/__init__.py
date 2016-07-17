from leaflets.views.adresses import CSVImportHandler, AddressListHandler, AddressSearchHandler, AddressImportHandler
from leaflets.views.base import BaseHandler
from leaflets.views.campaign import (
    AddCampaignHandler, ListCampaignsHandler, ShowCampaignHandler, CampaignAddressesHandler,
    MarkCampaignHandler, EditCampaignHandler, UserAssignCampaignHandler, AssignCampaignHandler,
    ShowCampaignMapHandler,
)
from leaflets.views.users import (
    LoginHandler, LogOutHandler, AddUserHandler, UsersListHandler, EditUserHandler,
    InviteHandler, UpdateUserHandler, UsersFolderHandler
)


handlers = (
    LoginHandler, LogOutHandler, AddUserHandler, BaseHandler, MarkCampaignHandler,
    AddressSearchHandler, AddressImportHandler, AddressListHandler, CSVImportHandler,
    AddCampaignHandler, ListCampaignsHandler, ShowCampaignHandler, CampaignAddressesHandler,
    EditCampaignHandler, UsersListHandler, EditUserHandler, UserAssignCampaignHandler,
    AssignCampaignHandler, ShowCampaignMapHandler, InviteHandler, UpdateUserHandler,
    UsersFolderHandler,
)


__all__ = (
    LoginHandler, LogOutHandler, AddUserHandler, BaseHandler, MarkCampaignHandler,
    AddressSearchHandler, AddressImportHandler, AddressListHandler, CSVImportHandler,
    AddCampaignHandler, ListCampaignsHandler, ShowCampaignHandler, CampaignAddressesHandler,
    EditCampaignHandler, UsersListHandler, EditUserHandler, UserAssignCampaignHandler,
    AssignCampaignHandler, ShowCampaignMapHandler, InviteHandler, UpdateUserHandler,
    UsersFolderHandler, handlers
)
