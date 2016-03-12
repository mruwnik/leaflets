from sqlalchemy import Column, String, Boolean, Integer

from leaflets.database import Base


class User(Base):
    """A user of the platform."""

    __tablename__ = 'users'

    id = Column(Integer, nullable=False, primary_key=True)
    username = Column(String(length=255), nullable=False, unique=True, index=True)
    email = Column(String(length=255), nullable=False)
    password_hash = Column(String, nullable=False)
    admin = Column(Boolean, nullable=False, default=False)
