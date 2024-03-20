import uuid

from fastapi import HTTPException
from sqlalchemy import text

from loguru import logger


async def add(db, english_word: str, translation: str, explanation: str, deck_id: str):
    card_id = uuid.uuid4()
    query = text("""
                    INSERT INTO cards (c_id, c_english_word, c_translation, c_explanation, c_deck_id) 
                    VALUES (:id, :english_word, :translation, :explanation, :deck_id)
                    """)
    await db.execute(query,
                     {'id': card_id,
                      'english_word': english_word,
                      'translation': translation,
                      'explanation': explanation,
                      'deck_id': deck_id})
    return str(card_id)


async def get(db, card_id: str):
    query = text("""SELECT c_english_word, c_translation, c_explanation FROM cards where c_id = :card_id""")
    result = await db.execute(query, {'card_id': card_id})
    res = result.fetchone()
    if res:
        english_word, translation, explanation = res
        return {"english_word": english_word, "translation": translation, "explanation": explanation}
    else:
        raise HTTPException(status_code=404,
                            detail='This card is not found')


async def edit(db, card_id, field_to_change, new_value):
    query = text(
        """UPDATE cards SET """ + 'c_' + field_to_change + """= :new_value WHERE c_id = :card_id""")
    await db.execute(query, {'new_value': new_value, 'card_id': card_id})


async def delete(db, card_id):
    query = text("""DELETE FROM cards WHERE c_id = :card_id""")
    await db.execute(query, {'card_id': card_id})


async def get_all(db, deck_id: str):
    query = text("""SELECT c_id, c_english_word, c_translation, c_explanation FROM cards WHERE c_deck_id = :deck_id;""")
    result = await db.execute(query, {'deck_id': deck_id})
    cards = {}

    for row in result:
        card_id, english_word, translation, explanation = row
        cards[str(card_id)] = {"card_id": str(card_id), "english_word": english_word, "translation": translation,
                               "explanation": explanation}

    return cards
