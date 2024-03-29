from sqlalchemy import Column, String, DateTime, BigInteger, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Cards(Base):
    __tablename__ = 'cards'

    c_id = Column(UUID(as_uuid=True), primary_key=True)
    c_deck_id = Column(UUID(as_uuid=True))
    c_english_word = Column(String(128))
    c_translation = Column(String(128))
    c_explanation = Column(String(128))
    c_image = Column(String(1024))


class Decks(Base):
    __tablename__ = 'decks'
    d_id = Column(UUID(as_uuid=True), primary_key=True)
    d_creator = Column(UUID(as_uuid=True))
    d_name = Column(String(128))
    d_description = Column(String(512))


class Games(Base):
    __tablename__ = 'games'
    a_id = Column(UUID(as_uuid=True), primary_key=True)
    a_user = Column(UUID(as_uuid=True))
    a_date = Column(DateTime)
    a_words = Column(BigInteger)
    a_decks_full = Column(BigInteger)
    a_decks_part = Column(BigInteger)


class Users(Base):
    __tablename__ = 'users'
    u_id = Column(UUID(as_uuid=True), primary_key=True)
    u_username = Column(String(128))
    u_email = Column(String(128))
    u_password = Column(LargeBinary)
    u_phone = Column(String(128))
    u_country = Column(String(128))


class Interests(Base):
    __tablename__ = 'interests'

    i_id = Column(UUID(as_uuid=True), primary_key=True)
    i_name = Column(String(128))
    i_user_id = Column(UUID(as_uuid=True))
    i_description = Column(String(512))


class Posts(Base):
    __tablename__ = 'posts'
    p_id = Column(UUID(as_uuid=True), primary_key=True)
    p_author_id = Column(UUID(as_uuid=True))
    p_text = Column(String(512))
    p_date = Column(DateTime)


class BankCards(Base):
    __tablename__ = 'bankcards'

    bc_id = Column(UUID(as_uuid=True), primary_key=True)
    bc_user_id = Column(UUID(as_uuid=True))
    bc_number = Column(LargeBinary)
    bc_exp_date = Column(LargeBinary)
    bc_cvv = Column(LargeBinary)
