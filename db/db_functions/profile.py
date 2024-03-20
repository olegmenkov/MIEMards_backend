import uuid

from pydantic import EmailStr
from fastapi import HTTPException
from sqlalchemy import text

import db.encryption as encryption
from db.db_functions import decks

from loguru import logger


async def add(db, username: str, password: str, email: EmailStr, phone: str, country: str):
    query = text("""SELECT u_email FROM users where u_email = :email""")
    result = await db.execute(query,
                              {'email': email})
    res = result.fetchone()
    if res:
        raise HTTPException(status_code=409, detail="Email already registered")

    query = text("""
            INSERT INTO users (u_id, u_username, u_password, u_email, u_phone, u_country) 
            VALUES (:u_id, :u_username, :u_password, :u_email, :u_phone, :u_country)
            """)
    await db.execute(query,
                     {'u_id': uuid.uuid4(),
                      'u_username': username,
                      'u_password': encryption.encrypt(password),
                      'u_email': email,
                      'u_phone': phone,
                      'u_country': country})


async def find_by_login(db, email: str, password: str):
    query = text("""SELECT * FROM users where u_email = :email""")
    result = await db.execute(query,
                              {'email': email})
    res = result.fetchone()
    if not res:
        logger.debug('User does not exist')
        return None
    u_id, u_username, u_email, u_password, u_phone, u_country = res
    if encryption.decrypt(u_password) == password:
        return res
    else:
        return None


async def get_data(db, user_id):
    query = text("""SELECT u_username, u_email, u_phone, u_country FROM users where u_id = :user_id""")
    result = await db.execute(query,
                              {'user_id': user_id})
    res = result.fetchone()
    if res:
        username, email, phone, country = res
        return {'username': username, 'email': email, 'phone': phone, 'country': country}
    else:
        raise HTTPException(status_code=404,
                            detail='This user is not found')


async def edit(db, user_id, field_to_change: str, new_value: str):
    if field_to_change == 'password':
        new_value = encryption.encrypt(new_value)
    query = text("""UPDATE users SET """ + 'u_' + field_to_change + """= :new_value WHERE u_id = :user_id""")
    await db.execute(query, {'new_value': new_value, 'user_id': user_id})


async def delete(db, user_id):
    query = text("""DELETE FROM users WHERE u_id = :user_id""")
    await db.execute(query, {'user_id': user_id})

    query = text("""SELECT d_id FROM decks where d_creator = :user_id""")
    result = await db.execute(query, {'user_id': user_id})

    res = result.fetchone()
    if res:
        for deck_id in res:
            await decks.delete(db, deck_id)
