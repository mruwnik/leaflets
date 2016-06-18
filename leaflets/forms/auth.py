import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sqlalchemy.exc import IntegrityError
from wtforms import StringField, PasswordField, BooleanField, HiddenField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Email, ValidationError
from wtforms_tornado import Form

from leaflets import database
from leaflets.models import User
from leaflets.etc import options

import logging
logger = logging.getLogger()


class LoginForm(Form):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class EditUserForm(Form):
    name = StringField('user_name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    is_admin = BooleanField('is_admin')
    user_id = HiddenField('user_id')

    def update(self, user):
        """Update the given user."""
        user.username = self.name.data
        user.email = self.email.data
        user.admin = self.is_admin.data

        database.session.commit()
        return user


class UpdateUserForm(Form):
    PASSWORD_MISMATCH = 'The passwords do not match'

    name = StringField('user_name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    password_repeat = PasswordField('repeat_password', validators=[DataRequired()])

    def validate_password(self, field):
        if field.data and field.data != self.password_repeat.data:
            raise ValidationError(self.PASSWORD_MISMATCH)

    def update(self, user):
        user.username=self.name.data,
        user.email=self.email.data,
        user.password_hash=User.hash(self.password.data),

        database.session.commit()


class AddUserForm(UpdateUserForm):

    is_admin = BooleanField('is_admin')
    parent = HiddenField('parent')

    def save(self, current_user_id):
        """Create a new user."""
        user = User(
            username=self.name.data,
            email=self.email.data,
            password_hash=User.hash(self.password.data),
            admin=self.is_admin.data,
            parent_id=self.parent.data or User.query.get(current_user_id).parent_id
        )

        database.session.add(user)
        database.session.commit()


def name_email(email):
    """Extract the name and address parts from the provided email address.

    Given an email like "Mr Blobby <example@site.net>" it will return ('Mr Blobby', 'example@site.net')
    """
    try:
        name, address = re.match('(.*?)\s*<?([^\s@<>]+@[^\s@<>]+)\s*', email).groups()
    except AttributeError:
        return '', email
    else:
        return name.strip(), address


def extract_emails(text):
    """Extract all emails from the provided text.

    :param str text: a text containing email addresses
    :return a list of (name, address) tuples
    """
    return re.findall('\s*([^;\n]+?@[^;\n\s]+)', text)


def check_for_url(form, field):
    """Check if the url macro is in the given field."""
    if '{url}' not in field.data:
        raise ValidationError('url_macro_missing')


def check_emails_provided(form, field):
    """Make sure that at least one email is provided."""
    if not extract_emails(field.data):
        raise ValidationError('emails_missing')


class InviteUsersForm(Form):
    """Handle email invitations."""

    parent = HiddenField('parent')
    subject = StringField('subject', validators=[DataRequired()])
    emails = StringField('emails', widget=TextArea(), validators=[DataRequired(), check_emails_provided])
    invitation = StringField('invitation', widget=TextArea(), validators=[DataRequired(), check_for_url])

    def _send_email(self, subject, address, contents):
        """Send an email to the given address."""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = options.EMAIL_ADDR
        msg['To'] = address
        msg.attach(MIMEText(contents, 'html'))

        try:
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.ehlo()
            server.starttls()
            server.login(options.EMAIL_ADDR, options.EMAIL_PASSWD)
            server.sendmail(options.EMAIL_ADDR, [address], msg.as_string())
            server.quit()
            logger.info('INVITE: sent activation url to %s', address)
        except smtplib.SMTPException:
            logger.error("Error: unable to send email")


    def send(self, base_url):
        """Send activation links to all provided email addresses.

        Links will only be sent to nonexistent users, after they get created.
        """
        for name, address in map(name_email, extract_emails(self.emails.data)):
            user = User(
                username=name,
                email=address,
                password_hash='',
                parent_id=self.parent.data
            )
            activation_url = base_url + user.reset_passwd()
            try:
                database.session.add(user)
                database.session.commit()
            except IntegrityError as e:
                logger.info("INVITE: skipping %s, as it already exists", address)
                continue

            self._send_email(
                self.subject.data, address,
                self.invitation.data.format(
                    name=name,
                    email=address,
                    url='<a href="{0}">{0}</a>'.format(activation_url)
                )
            )
