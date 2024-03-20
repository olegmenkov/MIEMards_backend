import uuid

from fastapi import HTTPException
from sqlalchemy import text

from db import encryption

from loguru import logger


async def add(db, user_id, number, exp_date, cvv):
    bank_card_id = uuid.uuid4()
    query = text(
        """INSERT INTO bankcards (bc_id, bc_user_id, bc_number, bc_exp_date, bc_cvv) VALUES (:id, :user_id, :number, :exp_date, :cvv)""")
    await db.execute(query,
                     {'id': bank_card_id,
                      'user_id': user_id,
                      'number': encryption.encrypt(number),
                      'exp_date': encryption.encrypt(exp_date),
                      'cvv': encryption.encrypt(cvv)})
    return str(bank_card_id)


async def edit(db, bank_card_id, field, value):
    if field in ['number', 'cvv', 'exp_date']:
        value = encryption.encrypt(value)
    query = text("""UPDATE bankcards SET """ + 'bc_' + field + """= :new_value WHERE bc_id = :bc_id""")
    await db.execute(query, {'new_value': value, 'bc_id': bank_card_id})


async def delete(db, bank_card_id):
    query = text("""DELETE FROM bankcards WHERE bc_id = :bank_card_id""")
    await db.execute(query, {'bank_card_id': bank_card_id})


async def get(db, bank_card_id):
    query = text("""SELECT bc_number, bc_exp_date, bc_cvv FROM bankcards where bc_id = :bank_card_id""")
    result = await db.execute(query, {'bank_card_id': bank_card_id})
    res = result.fetchone()
    if res:
        bc_number, bc_exp_date, bc_cvv = res
        number = encryption.decrypt(bc_number)
        return {'number': str(number)[-4:]}
    else:
        raise HTTPException(status_code=404,
                            detail='This card is not found')


async def get_all(db, user_id):
    query = text("""SELECT * FROM bankcards WHERE bc_user_id = :user_id;""")
    result = await db.execute(query, {'user_id': user_id})
    cards = {}

    for row in result:
        bc_id, bc_user_id, bc_number, bc_exp_date, bc_cvv = row
        cards[str(bc_id)] = {'number': str(encryption.decrypt(bc_number))[-4:]}
    return cards
