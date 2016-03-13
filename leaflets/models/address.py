from sqlalchemy import Column, String, Float, Integer, UniqueConstraint, Index

from leaflets.database import Base, session


class Address(Base):
    """An address."""

    __tablename__ = 'addresses'
    __table_args__ = (
        UniqueConstraint('house', 'street', 'town', 'postcode', 'country', name='unique_address'),
        Index('coords_index', 'lat', 'lon'),
    )

    id = Column(Integer, nullable=False, primary_key=True)
    house = Column(String(length=1024), nullable=True)
    street = Column(String(length=1024), nullable=True)
    town = Column(String(length=1024), nullable=True)
    postcode = Column(String(length=1024), nullable=True)
    country = Column(String(length=1024), nullable=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)

    @property
    def is_unique(self):
        return session.query(Address.id).filter(
            Address.town == self.town,
            Address.postcode == self.postcode,
            Address.street == self.street,
            Address.house == self.house,
            Address.country == self.country
        ).scalar() is None

    def serialise(self):
        """Return this address as a dict."""
        return {
            key: getattr(self, key) for key in ['id', 'lat', 'lon', 'country', 'town', 'postcode', 'street', 'house']
        }
