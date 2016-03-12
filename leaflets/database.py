from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from leaflets.etc import options


DATABASE_URL = 'postgresql://{user}{password}@{host}:{port}/{database}'.format(
    user=options.DB_USER,
    password=':' + options.DB_PASSWORD if options.DB_PASSWORD else '',
    host=options.DB_HOST,
    port=options.DB_PORT,
    database=options.DB_NAME
)
engine = create_engine(
    DATABASE_URL,
    encoding='utf-8',
    pool_recycle=600,
    pool_size=20,
    max_overflow=100
)


session = scoped_session(sessionmaker(
    autocommit=False,
    autoflush=True,
    expire_on_commit=False,
    bind=engine
))

Base = declarative_base()
Base.query = session.query_property()
