from sqlalchemy import Column, String, DateTime, BigInteger, ARRAY
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


class decks(Base):
    __tablename__ = 'decks'
    d_id = Column(UUID(as_uuid=True), primary_key=True)
    d_creator = Column(UUID(as_uuid=True))
    d_name = Column(String(128))
    d_description = Column(String(512))


class Achievements(Base):
    __tablename__ = 'achievements'
    a_id = Column(UUID(as_uuid=True), primary_key=True)
    a_user_creator = Column(UUID(as_uuid=True))
    a_date = Column(DateTime)
    a_words = Column(BigInteger)
    a_decks_full = Column(BigInteger)
    a_decks_part = Column(BigInteger)
    a_games = Column(BigInteger)


class Users(Base):
    __tablename__ = 'users'
    u_id = Column(UUID(as_uuid=True), primary_key=True)
    u_username = Column(String(128))
    u_password = Column(String(128))
    u_email = Column(String(128))
    u_phone = Column(String(128))
    u_country = Column(String(128))


class Interests(Base):
    __tablename__ = 'interests'

    i_id = Column(UUID(as_uuid=True), primary_key=True)
    i_name = Column(String(128))


class Posts(Base):
    __tablename__ = 'posts'
    p_id = Column(UUID(as_uuid=True), primary_key=True)
    p_author_id = Column(UUID(as_uuid=True))
    p_text = Column(String(512))


class Groups(Base):
    __tablename__ = 'groups'
    g_id = Column(UUID(as_uuid=True), primary_key=True)
    g_name = Column(String(128))
    g_admin_id = Column(UUID(as_uuid=True))
    g_members = Column(ARRAY(String))


class BankCards(Base):
    __tablename__ = 'bankcards'
    bc_user_id = Column(UUID(as_uuid=True), primary_key=True)
    bc_number = Column(String(128))
    bc_exp_date = DateTime()
    bc_cvv = Column(String(4))


class SocialMediaAccounts(Base):
    __tablename__ = 'socialmediaaccounts'
    sma_id = Column(UUID(as_uuid=True), primary_key=True)
    sma_user_id = Column(UUID(as_uuid=True))
    SMA_type = Column(String(128))
    SMA_link = Column(String(128))
