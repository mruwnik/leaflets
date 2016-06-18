import time
from uuid import uuid4
from hashlib import sha512

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship

from leaflets.database import Base


class User(Base):
    """A user of the platform."""

    __tablename__ = 'users'

    id = Column(Integer, nullable=False, primary_key=True)
    username = Column(String(length=255), nullable=False)
    email = Column(String(length=255), nullable=False, unique=True, index=True)
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
    def activation_hash(self):
        """Get an activation hash for this user."""
        return '%d-%s' % (time.time() / (60 * 60 * 24), uuid4().hex)

    def reset_passwd(self, passwd=None):
        """Reset the password.

        Set the password to the provided value if not None. In that case
        set the password hash to an activation link hash to mark that it
        needs to be set. This should be quite safe, as the activation hash
        will contain characters that will never appear in a normal hash.
        """
        if passwd is not None:
            self.password_hash = self.hash(passwd)
            return self.password_hash
        else:
            hash = self.activation_hash
            self.password_hash = 'reset-' + hash
            return hash

    @property
    def ancestors(self):
        """Get all ancestors of this user."""
        if not self.parent:
            return []
        return [self.parent] + self.parent.ancestors

    @property
    def descendants(self):
        """Get all descendants of this user."""
        children = self.children[:]
        for child in self.children:
            children += child.descendants
        return children

    @property
    def parent_campaigns(self):
        """Get all direct campaigns from all parents."""
        return [campaign for parent in self.ancestors for campaign in parent.campaigns]

    @property
    def children_campaigns(self):
        """Get all children campaigns."""
        return [campaign for child in self.descendants for campaign in child.campaigns]
