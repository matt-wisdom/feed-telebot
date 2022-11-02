from datetime import datetime
from sqlalchemy import Column, BigInteger, Boolean, String
from sqlalchemy import DateTime, Integer, Table
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Query
from sqlalchemy.ext.hybrid import hybrid_property


from config import DB_ENGINE


Base = declarative_base()
engine = create_engine(DB_ENGINE)
Session = sessionmaker(bind=engine)
session = Session()


users_feeds = Table(
    "users_feeds",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.user_id")),
    Column("feed_sources_id", Integer, ForeignKey("feed_sources.id")),
)


def create_all():
    Base.metadata.create_all(engine)


class BaseModel:
    @classmethod
    @hybrid_property
    def query(cls) -> Query:
        return session.query(cls)


class User(BaseModel, Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True)  # Telegram user_id
    username = Column(String)  # Username or name
    last_sent = Column(DateTime)  # Last time feed was sent
    is_admin = Column(Boolean, default=False)
    date_registered = Column(DateTime, default=datetime.utcnow())
    daily_updates = Column(Boolean, default=False)
    feeds = relationship("FeedSource", secondary=users_feeds, backref="users")

    def __repr__(self) -> str:
        return f"User: {self.user_name} - ID: {self.id}"


class FeedSource(BaseModel, Base):
    __tablename__ = "feed_sources"

    id = Column(Integer, primary_key=True)
    public = Column(Boolean, default=False)
    creator = Column(BigInteger)
    # user = relationship("User", backref=backref('feeds', order_by=id))
    url = Column(String(255))
    title = Column(String(32))
    description = Column(String(250))


class Feed(BaseModel, Base):
    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    date_checked = Column(DateTime)
    feed_title = Column(String(100))
    img_link = Column(String(255))
    author = Column(String(30))
    link = Column(String(255))
    title = Column(String(100))
    published = Column(String(30))
    summary = Column(String(1000))
    src = Column(String(32))
