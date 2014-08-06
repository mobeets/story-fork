import os

# http://docs.sqlalchemy.org/en/rel_0_8/orm/tutorial.html
# http://docs.sqlalchemy.org/en/rel_0_8/orm/session.html#session-faq
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

DB_NAME = os.environ.get('DATABASE_URL', 'postgresql://localhost/test')

class Engine(object):
    def __init__(self, dbname=DB_NAME, echo=True):
        self.engine = self.connect(dbname, echo)
        self.session = self.new_session()
        self.dbname = dbname

    def connect(self, dbname=DB_NAME, echo=True):
        return create_engine(dbname, echo=echo)

    def create_singleton_if_not_exists(self, table_obj, table_init):
        inspector = Inspector.from_engine(self.engine)
        if table_obj.__tablename__ not in inspector.get_table_names():
            x = table_init()
            self.create_tables()
            s = self.session()
            s.add(x)
            s.commit()

    def new_session(self):
        return sessionmaker(bind=self.engine)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def drop_tables(self):
        Base.metadata.drop_all(self.engine)
