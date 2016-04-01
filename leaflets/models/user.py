from hashlib import sha512

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship

from leaflets.database import Base


class User(Base):
    """A user of the platform."""

    __tablename__ = 'users'

    id = Column(Integer, nullable=False, primary_key=True)
    username = Column(String(length=255), nullable=False, unique=True, index=True)
    email = Column(String(length=255), nullable=False)
    password_hash = Column(String, nullable=False)
    admin = Column(Boolean, nullable=False, default=False)

    parent_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    parent = relationship('User', backref='children', remote_side=id)

    @staticmethod
    def hash(passwd):
        """Get a hash for the given password.

        :param str passwd: the password to be hashed
        """
        return sha512(passwd.encode('utf-8')).hexdigest()

    @property
    def parent_campaigns(self):
        """Get all direct campaigns from all parents."""
        if not self.parent:
            return []
        return self.parent.parent_campaigns + self.parent.campaigns

    @property
    def children_campaigns(self):
        """Get all children campaigns."""
        campaigns = []
        for child in self.children:
            campaigns += child.campaigns
            campaigns += child.children_campaigns
        return campaigns
