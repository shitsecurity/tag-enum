#!/usr/bin/env python

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class SQLite( object ): # no, think twice before you do this...
                        # if you still want to - think again

    @staticmethod
    def create(db={}):
        database = db.get('database', 'cms.db')
        engine=create_engine('sqlite:///{database}'.format(database=database))
        Base.metadata.create_all(engine)
        return sessionmaker(bind=engine)()

class MySQL( object ):

    @staticmethod
    def create(db={}):
        driver = db.get('driver', 'mysql+pymysql')
        username = db.get('username', 'root')
        password = db.get('password', 'root')
        database = db.get('database', 'enum_cms')
        host = db.get('host', 'localhost')
        creds = '{driver}://{username}:{password}@{host}/{database}' \
                '?charset=utf8' \
                .format(driver=driver,
                        username=username,
                        password=password,
                        database=database,
                        host=host)
        engine=create_engine( creds, pool_size=0xF, max_overflow=0 )
        Base.metadata.create_all(engine)
        return sessionmaker(bind=engine)()

class Session( object ):

    def __init__( self, session='default' ):
        self._session = session

    @property
    def session( self ):
        return self._session
