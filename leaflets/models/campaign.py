from datetime import datetime
from sqlalchemy import Column, String, Enum, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from leaflets.database import Base


class AddressStates(Enum):
    selected = 'selected'
    marked = 'marked'
    removed = 'removed'


class CampaignAddress(Base):
    """A many to many mapper between the campaign and addresses tables."""

    __tablename__ = 'campaign_address'

    campaign_id = Column(Integer, ForeignKey('campaigns.id'), primary_key=True)
    address_id = Column(Integer, ForeignKey('addresses.id'), primary_key=True)
    modified = Column(DateTime, nullable=False, default=datetime.utcnow)
    state = Column(AddressStates(name='address_states'), default=AddressStates.selected)
    campaign = relationship('Campaign', backref='campaign_addresses')
    address = relationship('Address', backref='campaign_addresses')


class Campaign(Base):
    """A leaflets campaign."""

    __tablename__ = 'campaigns'

    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String, nullable=False)
    desc = Column(Text, nullable=True)
    start = Column(DateTime, nullable=False, default=datetime.utcnow)
    created = Column(DateTime, nullable=False, default=datetime.utcnow)

    addresses = relationship(
        'Address',
        secondary=CampaignAddress.__table__,
        backref='campaigns'
    )