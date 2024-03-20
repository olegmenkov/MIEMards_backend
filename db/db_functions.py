import uuid

from pydantic import EmailStr
from fastapi import HTTPException
from datetime import datetime, timedelta
from sqlalchemy import text, select, func

from db.database import *
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

from loguru import logger


def encrypt(string):
    load_dotenv()
    key = bytes(str(os.getenv('ENC_KEY')), 'utf-8')
    f = Fernet(key)
    password = bytes(string, 'utf-8')
    return f.encrypt(password)


def decrypt(string):
    try:
        load_dotenv()
        key = bytes(str(os.getenv('ENC_KEY')), 'utf-8')
        f = Fernet(key)
        decrypted_data = f.decrypt(string)
        return decrypted_data.decode('utf-8')
    except Exception as e:
        logger.debug(f"Error during decryption: {e}")
        return None


async def add_user_to_db(db, username: str, password: str, email: EmailStr, phone: str, country: str):
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
                      'u_password': encrypt(password),
                      'u_email': email,
                      'u_phone': phone,
                      'u_country': country})


async def find_user_by_login_data(db, email: str, password: str):
    query = text("""SELECT * FROM users where u_email = :email""")
    result = await db.execute(query,
                              {'email': email})
    res = result.fetchone()
    if not res:
        logger.debug('User does not exist')
        return None
    u_id, u_username, u_email, u_password, u_phone, u_country = res
    if decrypt(u_password) == password:
        return res
    else:
        return None


async def get_userdata_by_id(db, user_id):
    query = text("""SELECT u_username, u_email, u_phone, u_country FROM users where u_id = :user_id""")
    result = await db.execute(query,
                              {'user_id': user_id})
    res = result.fetchone()
    if res:
        username, email, phone, country = res
        return {'username': username, 'email': email, 'phone': phone, 'country': country}
    else:
        raise HTTPException(status_code=404,
                            detail='This deck is not found')


async def edit_users_profile(db, user_id, field_to_change: str, new_value: str):
    if field_to_change == 'password':
        new_value = encrypt(new_value)
    query = text("""UPDATE users SET """ + 'u_' + field_to_change + """= :new_value WHERE u_id = :user_id""")
    await db.execute(query, {'new_value': new_value, 'user_id': user_id})


async def delete_user_from_db(db, user_id):
    query = text("""DELETE FROM users WHERE u_id = :user_id""")
    await db.execute(query, {'user_id': user_id})

    query = text("""SELECT d_id FROM decks where d_creator = :user_id""")
    result = await db.execute(query, {'user_id': user_id})

    res = result.fetchone()
    if res:
        for deck_id in res:
            await delete_deck_from_db(db, deck_id)


async def add_deck(db, name: str, creator: str, description: str):
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


async def get_deck_by_id(db, deck_id: str):
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


async def edit_deck_in_db(db, deck_id, field_to_change, new_value):
    query = text("""UPDATE decks SET """ + 'd_' + field_to_change + """= :new_value WHERE d_id = :deck_id""")
    await db.execute(query, {'new_value': new_value, 'deck_id': deck_id})


async def delete_deck_from_db(db, deck_id):
    query = text("""DELETE FROM decks WHERE d_id = :deck_id""")
    await db.execute(query, {'deck_id': deck_id})

    query = text("""SELECT c_id FROM cards where c_deck_id= :deck_id""")
    result = await db.execute(query, {'deck_id': deck_id})

    res = result.fetchone()
    if res:
        for deck_id in res:
            await delete_deck_from_db(db, deck_id)


async def get_users_decks(db, user_id: str):
    query = text("""SELECT d_id, d_creator, d_name, d_description FROM decks WHERE d_creator = :user_id;""")
    result = await db.execute(query, {'user_id': user_id})
    decks = dict()

    for row in result:
        deck_id, creator, name, description = row
        decks[str(deck_id)] = {"creator": str(creator), "name": name, "description": description}

    return decks


async def add_card(db, english_word: str, translation: str, explanation: str, deck_id: str):
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


async def get_card_by_id(db, card_id: str):
    query = text("""SELECT c_english_word, c_translation, c_explanation FROM cards where c_id = :card_id""")
    result = await db.execute(query, {'card_id': card_id})
    res = result.fetchone()
    if res:
        english_word, translation, explanation = res
        return {"english_word": english_word, "translation": translation, "explanation": explanation}
    else:
        raise HTTPException(status_code=404,
                            detail='This card is not found')


async def edit_card_in_db(db, card_id, field_to_change, new_value):
    query = text(
        """UPDATE cards SET """ + 'c_' + field_to_change + """= :new_value WHERE c_id = :card_id""")
    await db.execute(query, {'new_value': new_value, 'card_id': card_id})


async def delete_card_from_db(db, card_id):
    query = text("""DELETE FROM cards WHERE c_id = :card_id""")
    await db.execute(query, {'card_id': card_id})


async def get_decks_cards(db, deck_id: str):
    query = text("""SELECT c_id, c_english_word, c_translation, c_explanation FROM cards WHERE c_deck_id = :deck_id;""")
    result = await db.execute(query, {'deck_id': deck_id})
    cards = {}

    for row in result:
        card_id, english_word, translation, explanation = row
        cards[str(card_id)] = {"deck_id": str(deck_id), "english_word": english_word, "translation": translation,
                               "explanation": explanation}

    return cards


async def add_interest(db, user_id, name, description):
    interest_id = uuid.uuid4()
    query = text(
        """INSERT INTO interests (i_id, i_name, i_user_id, i_description) VALUES (:id, :name, :user_id, :description)""")
    await db.execute(query,
                     {'id': interest_id,
                      'name': name,
                      'user_id': user_id,
                      'description': description})
    return str(interest_id)


async def edit_interest(db, interest_id, field_to_change, new_value):
    query = text("""UPDATE interests SET """ + 'i_' + field_to_change + """= :new_value WHERE i_id = :interest_id""")
    await db.execute(query, {'new_value': new_value, 'interest_id': interest_id})


async def delete_interest(db, interest_id):
    query = text("""DELETE FROM interests WHERE i_id = :interest_id""")
    await db.execute(query, {'interest_id': interest_id})


async def get_interest(db, interest_id):
    query = text("""SELECT i_name, i_description FROM interests where i_id = :interest_id""")
    result = await db.execute(query, {'interest_id': interest_id})
    res = result.fetchone()
    if res:
        name, description = res
        return {"name": name, 'description': description}
    else:
        raise HTTPException(status_code=404,
                            detail='This interest is not found')


async def get_interests(db, user_id):
    query = text("""SELECT i_id, i_name, i_description FROM interests WHERE i_user_id = :user_id;""")
    result = await db.execute(query, {'user_id': user_id})
    interests = {}

    for row in result:
        interest_id, name, description = row
        interests[str(interest_id)] = {"name": name, 'description': description}

    return interests


async def add_post(db, user_id, text_):
    post_id = uuid.uuid4()
    query = text("""INSERT INTO posts (p_id, p_author_id, p_text) VALUES (:id, :author, :text)""")
    await db.execute(query,
                     {'id': post_id,
                      'author': user_id,
                      'text': text_})
    return str(post_id)


async def edit_post(db, post_id, field_to_change, new_value):
    query = text("""UPDATE posts SET """ + 'p_' + field_to_change + """= :new_value WHERE p_id = :post_id""")
    await db.execute(query, {'new_value': new_value, 'post_id': post_id})


async def delete_post(db, post_id):
    query = text("""DELETE FROM posts WHERE p_id = :post_id""")
    await db.execute(query, {'post_id': post_id})


async def get_post(db, post_id):
    query = text("""SELECT p_text FROM posts where p_id = :post_id""")
    result = await db.execute(query, {'post_id': post_id})
    res = result.fetchone()
    if res:
        text_ = res[0]
        return {"text": text_}
    else:
        raise HTTPException(status_code=404,
                            detail='This post is not found')


async def get_posts(db, user_id):
    query = text("""SELECT p_id, p_text FROM posts WHERE p_author_id = :user_id;""")
    result = await db.execute(query, {'user_id': user_id})
    posts = {}

    for row in result:
        post_id, text_ = row
        posts[str(post_id)] = {"text": text_}

    return posts


'''
async def add_group(db, user_id, name, members):
    group_id = uuid.uuid4()
    query = text("""INSERT INTO groups (g_id, g_name, g_admin_id, g_users) VALUES (:id, :name, :admin, :members)""")
    await db.execute(query,
                     {'id': group_id,
                      'name': name,
                      'admin': user_id,
                      'members': members})
    return str(group_id)


async def edit_group(db, group_id, field, value):
    query = text("""UPDATE groups SET """ + 'g_' + field + """= :new_value WHERE g_id = :group_id""")
    await db.execute(query, {'new_value': value, 'group_id': group_id})


async def delete_group(db, group_id):
    query = text("""DELETE FROM groups WHERE g_id = :group_id""")
    await db.execute(query, {'group_id': group_id})


async def get_group(db, group_id):
    query = text("""SELECT * FROM groups where g_id = :group_id""")
    result = await db.execute(query, {'group_id': group_id})
    res = result.fetchone()
    if res:
        group_id, name, admin_id, members = res
        return {'name': name,
                'admin_id': str(admin_id),
                'users': members}
    else:
        raise HTTPException(status_code=404,
                            detail='This group is not found')


async def get_groups(db, user_id):
    query = text("""SELECT * FROM groups WHERE g_admin_id = :user_id;""")
    result = await db.execute(query, {'user_id': user_id})
    groups = {}

    for row in result:
        group_id, name, admin, members = row
        groups[str(group_id)] = {'name': name,
                                 'admin_id': admin,
                                 'users': members}
    return groups'''


async def add_bank_card(db, user_id, number, exp_date, cvv):
    bank_card_id = uuid.uuid4()
    query = text(
        """INSERT INTO bankcards (bc_id, bc_user_id, bc_number, bc_exp_date, bc_cvv) VALUES (:id, :user_id, :number, :exp_date, :cvv)""")
    await db.execute(query,
                     {'id': bank_card_id,
                      'user_id': user_id,
                      'number': encrypt(number),
                      'exp_date': encrypt(exp_date),
                      'cvv': encrypt(cvv)})
    return str(bank_card_id)


async def edit_bank_card(db, bank_card_id, field, value):
    if field in ['number', 'cvv', 'exp_date']:
        value = encrypt(value)
    query = text("""UPDATE bankcards SET """ + 'bc_' + field + """= :new_value WHERE bc_id = :bc_id""")
    await db.execute(query, {'new_value': value, 'bc_id': bank_card_id})


async def delete_bank_card(db, bank_card_id):
    query = text("""DELETE FROM bankcards WHERE bc_id = :bank_card_id""")
    await db.execute(query, {'bank_card_id': bank_card_id})


async def get_bank_card(db, bank_card_id):
    query = text("""SELECT bc_number, bc_exp_date, bc_cvv FROM bankcards where bc_id = :bank_card_id""")
    result = await db.execute(query, {'bank_card_id': bank_card_id})
    res = result.fetchone()
    if res:
        bc_number, bc_exp_date, bc_cvv = res
        number = decrypt(bc_number)
        return {'number': str(number)[-4:]}
    else:
        raise HTTPException(status_code=404,
                            detail='This card is not found')


async def get_bank_cards(db, user_id):
    query = text("""SELECT * FROM bankcards WHERE bc_user_id = :user_id;""")
    result = await db.execute(query, {'user_id': user_id})
    cards = {}

    for row in result:
        bc_id, bc_user_id, bc_number, bc_exp_date, bc_cvv = row
        cards[str(bc_id)] = {'number': str(decrypt(bc_number))[-4:]}
    return cards


'''
async def add_account(db, user_id, type_, link):
    acc_id = uuid.uuid4()
    query = text("""INSERT INTO socialmediaaccounts VALUES (:id, :user_id, :type, :link)""")
    await db.execute(query,
                     {'id': acc_id,
                      'user_id': user_id,
                      'type': type_,
                      'link': link})
    return str(acc_id)


async def edit_account(db, account_id, field, value):
    table_column = {'type': "sma_type", 'link': "sma_link"}

    if field == "type":
        query = text(
            """UPDATE socialmediaaccounts SET ababa = :new_value WHERE sma_id = :account_id""")

    if field == "link":
        query = text(
            """UPDATE socialmediaaccounts SET obobo = :new_value WHERE sma_id = :account_id""")

    await db.execute(query, {'new_value': value, 'account_id': account_id})


async def delete_account(db, account_id):
    query = text("""DELETE FROM socialmediaaccounts WHERE sma_id = :account_id""")
    await db.execute(query, {'account_id': account_id})


async def get_account(db, account_id):
    query = text("""SELECT * FROM socialmediaaccounts where sma_id = :account_id""")
    result = await db.execute(query, {'account_id': account_id})
    res = result.fetchone()
    if res:
        id_, user_id, type_, link = res
        return {'type': type_,
                'link': link}
    else:
        raise HTTPException(status_code=404,
                            detail='This account is not found')


async def get_accounts(db, user_id):
    query = text("""SELECT * FROM socialmediaaccounts WHERE sma_user_id = :user_id;""")
    result = await db.execute(query, {'user_id': user_id})
    accounts = {}

    for row in result:
        acc_id, user_id, type_, link = row
        accounts[str(acc_id)] = {'type': type_,
                                 'link': link}
    return accounts'''


async def update_achievements(db, user_id, words_learned, decks_learned_fully, decks_learned_partly):
    game_id = uuid.uuid4()
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    query = text("""INSERT INTO games (a_id, a_user, a_date, a_words, a_decks_full, a_decks_part) 
    VALUES (:game_id, :user_id, :today, :words, :decks_full, :decks_part);""")

    await db.execute(query,
                     {'game_id': game_id, 'user_id': user_id, 'today': today, 'words': words_learned,
                      'decks_full': decks_learned_fully,
                      'decks_part': decks_learned_partly})


async def calculate_daily_stats(db, user_id):
    query = text("""
        SELECT 
            SUM(a_words) AS total_words_day,
            SUM(a_decks_full) AS total_decks_full_day,
            SUM(a_decks_part) AS total_decks_part_day,
            COUNT(*) AS total_games_day
        FROM games
        WHERE a_date = CURRENT_DATE AND a_user = :user_id;
    """)
    result = await db.execute(query, {'user_id': user_id})
    return list(result.fetchone())


async def calculate_weekly_stats(db, user_id):
    query = text("""
        SELECT 
            SUM(a_words) AS total_words_day,
            SUM(a_decks_full) AS total_decks_full_day,
            SUM(a_decks_part) AS total_decks_part_day,
            COUNT(*) AS total_games_day
        FROM games
        WHERE CURRENT_DATE - INTERVAL '7 days' <= a_date AND a_date <= CURRENT_DATE AND a_user = :user_id;
    """)
    result = await db.execute(query, {'user_id': user_id})
    return list(result.fetchone())


async def calculate_alltime_stats(db, user_id):
    query = text("""
        SELECT 
            SUM(a_words) AS total_words_day,
            SUM(a_decks_full) AS total_decks_full_day,
            SUM(a_decks_part) AS total_decks_part_day,
            COUNT(*) AS total_games_day
        FROM games
        WHERE a_user = :user_id;
    """)
    result = await db.execute(query, {'user_id': user_id})
    return list(result.fetchone())


async def calculate_daily_rating(db):
    query = text("""
        SELECT g.a_user as user_id, u.u_username AS user_name, SUM(g.a_words) AS total_words
        FROM games g
        JOIN users u ON g.a_user = u.u_id
        WHERE g.a_date = CURRENT_DATE
        GROUP BY u.u_username, g.a_user
        ORDER BY total_words DESC;
    """)
    result = await db.execute(query)

    rating = []
    for row in result:
        user_id, username, words_learned = row
        rating.append({'user_id': str(user_id), 'username': username, 'words_learned': int(words_learned)})

    return rating


async def calculate_weekly_rating(db):
    query = text("""
        SELECT g.a_user as user_id, u.u_username AS user_name, SUM(g.a_words) AS total_words
        FROM games g
        JOIN users u ON g.a_user = u.u_id
        WHERE CURRENT_DATE - INTERVAL '7 days' <= g.a_date AND g.a_date <= CURRENT_DATE
        GROUP BY u.u_username, g.a_user
        ORDER BY total_words DESC;
    """)
    result = await db.execute(query)

    rating = []
    for row in result:
        user_id, username, words_learned = row
        rating.append({'user_id': str(user_id), 'username': username, 'words_learned': int(words_learned)})

    return rating


async def calculate_alltime_rating(db):
    query = text("""
        SELECT g.a_user as user_id, u.u_username AS user_name, SUM(g.a_words) AS total_words
        FROM games g
        JOIN users u ON g.a_user = u.u_id
        GROUP BY u.u_username, g.a_user
        ORDER BY total_words DESC;
    """)
    result = await db.execute(query)

    rating = []
    for row in result:
        user_id, username, words_learned = row
        rating.append({'user_id': str(user_id), 'username': username, 'words_learned': int(words_learned)})

    return rating
