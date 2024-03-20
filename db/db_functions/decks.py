import uuid

from db.db_functions import cards
from fastapi import HTTPException
from sqlalchemy import text

from loguru import logger


async def add(db, name: str, creator: str, description: str):
    deck_id = uuid.uuid4()
    query = text("""
                INSERT INTO decks (d_id, d_name, d_creator, d_description) 
                VALUES (:id, :name, :creator, :description)
                """)
    await db.execute(query,
                     {'id': deck_id,
                      'name': name,
                      'creator': creator,
                      'description': description})
    return str(deck_id)


async def get(db, deck_id: str):
    query = text("""SELECT d_name, d_description FROM decks where d_id = :deck_id""")
    result = await db.execute(query,
                              {'deck_id': deck_id})
    res = result.fetchone()
    if res:
        name, description = res
        return {"name": name, "description": description}
    else:
        raise HTTPException(status_code=404,
                            detail='This deck is not found')


async def edit(db, deck_id, field_to_change, new_value):
    query = text("""UPDATE decks SET """ + 'd_' + field_to_change + """= :new_value WHERE d_id = :deck_id""")
    await db.execute(query, {'new_value': new_value, 'deck_id': deck_id})


async def delete(db, deck_id):
    query = text("""DELETE FROM decks WHERE d_id = :deck_id""")
    await db.execute(query, {'deck_id': deck_id})

    query = text("""SELECT c_id FROM cards where c_deck_id= :deck_id""")
    result = await db.execute(query, {'deck_id': deck_id})

    res = result.fetchone()
    if res:
        for card_id in res:
            await cards.delete(db, card_id)


async def get_all(db, user_id: str):
    query = text("""SELECT d_id, d_creator, d_name, d_description FROM decks WHERE d_creator = :user_id;""")
    result = await db.execute(query, {'user_id': user_id})
    decks = dict()

    for row in result:
        deck_id, creator, name, description = row
        decks[str(deck_id)] = {"creator": str(creator), "name": name, "description": description}

    return decks
