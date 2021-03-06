import os

from tornado.options import define, options, parse_config_file, parse_command_line, Error


SETTINGS_DIR = os.path.abspath(os.path.split(__file__)[0])
BASE_DIR = os.path.join(SETTINGS_DIR, '..')
PROJECT_DIR = os.path.join(BASE_DIR, '..')


define('PORT', 5000, help='The port where the application listens at')

config = os.environ.get('LEAFLETS_TEST', '')
if config:
    config = os.path.join(SETTINGS_DIR, config)
define('config_file', config, help='The settings to use')

define('DEBUG', False)
define('TEMPLATES', os.path.join(BASE_DIR, 'templates'), help='The location of all HTML templates')
define('STATIC_FILES', os.path.join(BASE_DIR, 'static'), help='The location of all static files')
define('SECRET_KEY', '123456', help='A secret key used e.g. for secure cookies')
define('LOCALE_DIR', os.path.join(BASE_DIR, 'locale'), help='Where locale files are kept')

define('EMAIL_ADDR', None, help='The address from which to send emails')
define('EMAIL_PASSWD', None, help='The password for the email address')
define('ACTIVATION_TIMEOUT', 30, help='The amount of days after which activation links are deemed stale')

# test params

define('POSTGRES_LOCATION', '/usr/lib/postgresql/', help='Where postgres is installed')


DATABASE_PARAMS = {
    'DB_NAME': 'leaflets',
    'DB_USER': 'leaflets',
    'DB_PASSWORD': 'leaflets',
    'DB_HOST': 'localhost',
    'DB_PORT': 5432
}
for param, val in DATABASE_PARAMS.items():
    define(param, val)


def import_settings(settings_file):
    """Import the given settings file if it exists."""
    try:
        parse_config_file(settings_file)
        print(' * Imported %s' % settings_file)
    except FileNotFoundError:
        pass

# Parse the command line to see if any config file was provided
try:
    parse_command_line()
except Error as e:
    print(e)

# Import the various settings files
for settings_file in os.path.join(SETTINGS_DIR, 'local.py'), options.config_file:
    import_settings(settings_file)

# The command line options should be more important than those in the settings,
# so import them once again - otherwise they might have been overwritten
# while importing from the files.
try:
    parse_command_line()
except Error as e:
    print(e)
