import os
import re


PORT = int(os.environ.get('PORT'))
SECRET_KEY = os.environ.get('SECRET_KEY')

database_url = os.environ.get('DATABASE_URL')

database_parts = re.search(
    r'postgres://(?P<user>.*?):(?P<password>.*?)@(?P<host>.*?):(?P<port>.*?)/(?P<database>.*?)$',
    database_url
)

if database_parts:
    DB_NAME = database_parts.group('database')
    DB_USER = database_parts.group('user')
    DB_PASSWORD = database_parts.group('password')
    DB_HOST = database_parts.group('host')
    DB_PORT = int(database_parts.group('port') or 5432)

