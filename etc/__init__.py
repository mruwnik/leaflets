from tornado.options import define, options, parse_config_file, parse_command_line


define('PORT', 5000, help='The port where the application listens at')
define('config_file', '', help='The settings to use')

define('DEBUG', False)
define('TEMPLATES', 'templates', help='The location of all HTML templates')

def import_settings(settings_file):
    """Import the given settings file if it exists."""
    try:
        parse_config_file(settings_file)
        print(' * Imported %s' % settings_file)
    except FileNotFoundError:
        pass

# Parse the command line to see if any config file was provided
parse_command_line()

# Import the various settings files
for settings_file in 'etc/local.py', options.config_file:
    import_settings(settings_file)

# The command line options should be more important than those in the settings,
# so import them once again - otherwise they might have been overwritten
# while importing from the files.
parse_command_line()

