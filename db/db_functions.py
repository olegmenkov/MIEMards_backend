import uuid

from pydantic import EmailStr
from fastapi import HTTPException
from datetime import datetime, timedelta

from sqlalchemy import text

from db.database import *


async def add_user_to_db(db, username: str, password: str, email: EmailStr, phone: str, country: str):
    query = text("""
            INSERT INTO users (u_id, u_username, u_password, u_email, u_phone, u_country) 
            VALUES (:u_id, :u_username, :u_password, :u_email, :u_phone, :u_country)
            """)
    await db.execute(query,
                     {'u_id': uuid.uuid4(),
                      'u_username': username,
                      'u_password': password,
                      'u_email': email,
                      'u_phone': phone,
                      'u_country': country})


async def find_user_by_login_data(db, email: str, password: str):
    query = text("""SELECT * FROM users where u_email = :email and u_password = :password""")
    result = await db.execute(query,
                              {'email': email,
                               'password': password})
    res = result.fetchone() if result else None
    return res


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
        cards[card_id] = {"deck_id": deck_id, "english_word": english_word, "translation": translation, "explanation": explanation}

    return cards


async def add_interest(db, user_id, name):
    interest_id = uuid.uuid4()
    query = text("""INSERT INTO interests (i_id, i_name, i_user_id) VALUES (:id, :name, :user_id)""")
    await db.execute(query,
                     {'id': interest_id,
                      'name': name,
                      'user_id': user_id})
    return str(interest_id)


async def edit_interest(db, interest_id, field_to_change, new_value):
    query = text("""UPDATE interests SET """ + 'i_' + field_to_change + """= :new_value WHERE i_id = :interest_id""")
    await db.execute(query, {'new_value': new_value, 'interest_id': interest_id})


async def delete_interest(db, interest_id):
    query = text("""DELETE FROM interests WHERE i_id = :interest_id""")
    await db.execute(query, {'interest_id': interest_id})


async def get_interest(db, interest_id):
    query = text("""SELECT i_name FROM interests where i_id = :interest_id""")
    result = await db.execute(query, {'interest_id': interest_id})
    res = result.fetchone()
    if res:
        name = res[0]
        return {"name": name}
    else:
        raise HTTPException(status_code=404,
                            detail='This interest is not found')


async def get_interests(db, user_id):
    query = text("""SELECT i_id, i_name FROM interests WHERE i_user_id = :user_id;""")
    result = await db.execute(query, {'user_id': user_id})
    interests = {}

    for row in result:
        interest_id, name = row
        interests[interest_id] = {"name": name}

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
                'admin_id': admin_id,
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
    return groups


'''def add_bank_card(user_id, number, exp_date, cvv):
    bank_card = uuid.uuid4()
    query = text("""INSERT INTO bankcards (bc_id, g_name, g_admin_id, g_users) VALUES (:id, :name, :admin, :members)""")
    await db.execute(query,
                     {'id': group_id,
                      'name': name,
                      'admin': user_id,
                      'members': members})
    return str(group_id)'''


def edit_bank_card(user_id, bank_card_id, field, value):
    pass


def delete_bank_card(user_id, bank_card_id):
    pass


def get_bank_card(user_id, bank_card_id):
    number = '1234567890123456'
    return number[-4:]


def get_bank_cards(user_id):
    return ['3144', '7302']


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
    table_column = {"type": "SMA_type", "link": "SMA_link"}
    query = text("""UPDATE socialmediaaccounts SET """ + table_column[field] + """= :new_value WHERE sma_id = :account_id""")
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
    return accounts


def update_achievements(user_id, words_learned, decks_learned_fully, decks_learned_partly):
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    # If the user exists, update their achievements for today
    if user_id in achievements:
        user_data = achievements[user_id]
        if today in user_data:
            user_data[today]["words_learned"] += words_learned
            user_data[today]["decks_learned_fully"] += decks_learned_fully
            user_data[today]["decks_learned_partly"] += decks_learned_partly
            user_data[today]["games"] += 1
        else:
            user_data[today] = {"words_learned": words_learned,
                                "decks_learned_fully": decks_learned_fully,
                                "decks_learned_partly": decks_learned_partly,
                                "games": 1}
    else:
        # If the user does not exist, create a new entry for them
        achievements[user_id] = {today: {"words_learned": words_learned,
                                         "decks_learned_fully": decks_learned_fully,
                                         "decks_learned_partly": decks_learned_partly,
                                         "games": 1}}


def get_results_for_period(user_id, period_start, period_end):
    total_words = 0
    fully_learned_decks = 0
    partly_learned_decks = 0
    total_games = 0

    user_data = achievements.get(user_id, {})

    for date, results in user_data.items():
        if period_start <= date <= period_end:
            total_words += results["words_learned"]
            fully_learned_decks += results["decks_learned_fully"]
            partly_learned_decks += results["decks_learned_partly"]
            total_games += results["games"]

    return total_words, fully_learned_decks, partly_learned_decks, total_games


def get_results_for_today(user_id):
    try:
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        return get_results_for_period(user_id, today, today + timedelta(days=1))
    except:
        return 0, 0, 0, 0


def get_weekly_results(user_id):
    today = datetime.today()
    week_start = today - timedelta(days=today.weekday())  # Assuming Monday is the start of the week
    week_end = week_start + timedelta(days=6)

    return get_results_for_period(user_id, week_start, week_end)


def get_total_results(user_id):
    today = datetime.today()
    start_date = min(date for date in achievements.get(user_id, {})) if user_id in achievements else today

    return get_results_for_period(user_id, start_date, today)


def get_top_all(metric):
    # Create a list of tuples containing user_id and the corresponding metric
    user_metric_tuples = [(user_id, metric(user_data)) for user_id, user_data in achievements.items()]

    # Sort the list by the metric in descending order
    sorted_user_metric = sorted(user_metric_tuples, key=lambda x: x[1], reverse=True)

    # Return all users with their data
    return sorted_user_metric


def get_top_all_for_day():
    try:
        metric = lambda x: x[datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)]["words_learned"]
        return get_top_all(metric)
    except:
        return []


def get_top_all_for_week():
    metric = lambda x: sum(
        value["words_learned"] for date, value in x.items() if date >= datetime.today() - timedelta(days=7))
    return get_top_all(metric)


def get_top_all_for_total():
    metric = lambda x: sum(value["words_learned"] for value in x.values())
    return get_top_all(metric)


def get_user_rank_for_day(user_id):
    top_all_today = get_top_all_for_day()
    user_rank = [rank + 1 for rank, (rank_user_id, _) in enumerate(top_all_today) if rank_user_id == user_id]
    return user_rank[0] if user_rank else None


def get_user_rank_for_week(user_id):
    top_all_weekly = get_top_all_for_week()
    user_rank = [rank + 1 for rank, (rank_user_id, _) in enumerate(top_all_weekly) if rank_user_id == user_id]
    return user_rank[0] if user_rank else None


def get_user_rank_for_total(user_id):
    top_all_total = get_top_all_for_total()
    user_rank = [rank + 1 for rank, (rank_user_id, _) in enumerate(top_all_total) if rank_user_id == user_id]
    return user_rank[0] if user_rank else None
