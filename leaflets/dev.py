import sys
from subprocess import check_output
from datetime import datetime, timedelta
from random import randint, choice, sample

from IPython import embed
from path import Path
from alembic.config import Config
from alembic import command as alembic_command

from leaflets import database
from leaflets.models import Address, User
from leaflets.views import AddressImportHandler
from leaflets.views.adresses.address_utils import find_addresses
from leaflets.forms import CampaignForm


DEFAULT_USER = 'user'
DEFAULT_USER_PASSWORD = 'password'
LORUM_IPSUM = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas accumsan imperdiet risus. Ut tristique volutpat
 pretium. Phasellus urna sem, dignissim sit amet tellus ac, venenatis venenatis nulla. Cras bibendum risus quis egestas
 aliquam. Mauris faucibus lobortis nibh ac convallis. Fusce vitae posuere tellus. In tempor semper tincidunt.
 Cras pharetra augue sed arcu pulvinar molestie. Integer turpis leo, commodo sit amet consectetur at, consectetur non
 quam. Morbi at elementum est, in egestas metus. Suspendisse rhoncus ex a velit dignissim tempus. Morbi nulla mauris,
 aliquet eget justo quis, malesuada maximus nisl. Praesent porta egestas libero imperdiet varius. Morbi bibendum vitae
 velit in eleifend. Cras ligula purus, pretium sed urna vel, dapibus ullamcorper odio. Nunc pretium, dui ac mattis
 tempus, erat orci tempus quam, vel tincidunt risus diam in nulla. Etiam malesuada velit porttitor elit rhoncus
 suscipit non non neque. Aenean pharetra dui a sapien tempor varius. Suspendisse non neque ex. Nulla gravida metus et
 lorem scelerisque interdum. Vestibulum sit amet viverra orci, ac vestibulum turpis.
 Praesent sit amet lectus aliquam, ultrices sapien vitae, facilisis diam. Fusce volutpat tincidunt felis, eget varius
 libero efficitur ut. Cras ultricies sem a ligula congue, ut consectetur orci aliquet. Nam feugiat, velit id lacinia
 lacinia, tellus nunc placerat metus, id sollicitudin orci nibh non lectus. Cras venenatis, lectus ac tempus faucibus,
 mauris metus venenatis sapien, eu dictum magna lorem vel nisi. Sed id tristique dolor. Sed consequat sem vitae mi
 lobortis, at placerat metus rhoncus. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac
 turpis egestas. Suspendisse potenti. Vivamus luctus consectetur porta.
"""


def create_user(user_name, parent=None):
    """Create a new user."""
    return User(
        username=user_name,
        email=user_name.replace(' ', '_') + '@bla.bl',
        password_hash=User.hash(DEFAULT_USER_PASSWORD),
        admin=choice([True, False]),
        parent_id=parent,
    )


def add_default_user():
    """Add the default user."""
    print('* adding default user')
    default_user = User(
        username=DEFAULT_USER,
        email=DEFAULT_USER + '@bla.bl',
        password_hash=User.hash(DEFAULT_USER_PASSWORD),
        admin=True,
        parent_id=None,
    )

    database.session.add(default_user)
    database.session.commit()
    return default_user


def add_users(default_user):
    """Add a load of fake users."""
    print('* adding users')

    # Create 10 top level users
    print('  - top level users')
    database.session.add_all([create_user('equal user %d' % i) for i in range(10)])

    for i in range(10):
        username = 'child %d' % i
        print('  -', username)
        user = create_user(username, default_user.id)
        database.session.add(user)
        database.session.commit()

        if user.admin:
            database.session.add_all(
                [create_user('admin %d\'s child %d' % (user.id, j), user.id) for j in range(randint(1, 10))])


def add_addressess():
    """Add all addresses from Giszowiec."""
    print('* searching for addresses')
    addresses = list(find_addresses((50.213267971591954, 19.055913791656494, 50.23326797159195, 19.085913791656495)))
    print('* adding %d addresses' % len(addresses))
    AddressImportHandler.import_addresses(None, addresses)


def random_campaign(addresses):
    """Generate a random campaign."""
    words = LORUM_IPSUM.split()
    return CampaignForm(
        name=' '.join(sample(words, 3)).capitalize(),
        desc=' '.join(sample(words, randint(0, 100))),
        start=datetime.utcnow() + timedelta(minutes=randint(0, 10000) - 5000),
        addresses=sample(addresses, randint(20, len(addresses))),
    )


def add_campaigns():
    """Add fake campaigns."""
    addresses = [addr.id for addr in database.session.query(Address)]

    print('* adding campaigns for default user')
    for i in range(5):
        CampaignForm(
            name='Cąþąiŋń ńó %d' % i,
            desc='The description for campaign %d, along with some unicode for fun: 継続は力なり' % i,
            start=datetime.utcnow() + timedelta(minutes=randint(0, 10000) - 5000),
            addresses=sample(addresses, randint(20, len(addresses))),
        ).save(user_id=1)

    print('* adding random campaigns')
    admins = User.query.filter(User.admin == True).all()
    for i in range(randint(10, 30)):
        random_campaign(addresses).save(choice(admins).id)


def db_drop():
    """Delete all data from the database."""
    table_names = str(', '.join(database.engine.table_names()))

    drop_tables_query = (
        "DROP TABLE {0};".format(table_names) +
        "DROP TYPE address_states;"
    )

    if table_names:  # table_names not empty -> there is a table to drop
        database.engine.execute(drop_tables_query)


def db_init():
    """Set up the database."""
    base_path = Path(__file__).parent
    alembic_ini = 'alembic.ini'
    alembic_cfg = Config(alembic_ini)

    with base_path:
        alembic_command.upgrade(alembic_cfg, "head")


def db_generate():
    """Generate fake data and insert it into the database."""
    add_users(add_default_user())
    add_addressess()
    add_campaigns()

    database.session.commit()


def db_shell():
    """Run IPython within a Flask-SQLAlchemy session."""
    # By default embed uses the calling function's scope as global scope, which prevents interactively defining and
    # using a global and a function accessing it: https://github.com/ipython/ipython/issues/62. Using a separate
    # namespace for interactive commands fixes this.
    from leaflets import database
    from leaflets import models
    user_ns = {name: getattr(database, name) for name in dir(database)}
    user_ns.update({name: getattr(models, name) for name in dir(models)})

    # Banner with available namespace to be displayed on the IPython start:
    banner = 'User namespace: %s' % sorted(obj for obj in user_ns.keys() if not obj.startswith('__'))
    embed(user_ns=user_ns, banner2=banner)


def compile_locales():
    """Compile all messages.pot files."""
    base_path = Path(__file__).parent / 'locale'
    for locale in base_path.dirs():
        with (locale / 'LC_MESSAGES'):
            print('* translating', locale)
            check_output(['msgfmt', 'messages.pot'])


if __name__ == "__main__":
    if not sys.argv[1:]:
        print('either select "translate", "shell" or "recreate"')
    else:
        if sys.argv[1] == 'shell':
            db_shell()
        elif sys.argv[1] == 'translate':
            compile_locales()
        elif sys.argv[1] == 'recreate':
            db_drop()
            db_init()
            db_generate()
        else:
            print('"%s" is not a valid command' % sys.argv[1])
