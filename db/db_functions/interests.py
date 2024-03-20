import uuid

from fastapi import HTTPException
from sqlalchemy import text

from loguru import logger


async def add(db, user_id, name, description):
    interest_id = uuid.uuid4()
    query = text(
        """INSERT INTO interests (i_id, i_name, i_user_id, i_description) VALUES (:id, :name, :user_id, :description)""")
    await db.execute(query,
                     {'id': interest_id,
                      'name': name,
                      'user_id': user_id,
                      'description': description})
    return str(interest_id)


async def edit(db, interest_id, field_to_change, new_value):
    query = text("""UPDATE interests SET """ + 'i_' + field_to_change + """= :new_value WHERE i_id = :interest_id""")
    await db.execute(query, {'new_value': new_value, 'interest_id': interest_id})


async def delete(db, interest_id):
    query = text("""DELETE FROM interests WHERE i_id = :interest_id""")
    await db.execute(query, {'interest_id': interest_id})


async def get(db, interest_id):
    query = text("""SELECT i_name, i_description FROM interests where i_id = :interest_id""")
    result = await db.execute(query, {'interest_id': interest_id})
    res = result.fetchone()
    if res:
        name, description = res
        return {"name": name, 'description': description}
    else:
        raise HTTPException(status_code=404,
                            detail='This interest is not found')


async def get_all(db, user_id):
    query = text("""SELECT i_id, i_name, i_description FROM interests WHERE i_user_id = :user_id;""")
    result = await db.execute(query, {'user_id': user_id})
    interests = {}

    for row in result:
        interest_id, name, description = row
        interests[str(interest_id)] = {"name": name, 'description': description}

    return interests
