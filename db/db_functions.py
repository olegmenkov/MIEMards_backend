from pydantic import EmailStr
from fastapi import HTTPException
from datetime import datetime, timedelta
from db.database import *


def add_user_to_db(username: str, password: str, email: EmailStr, phone: str, country: str):
    for user_id in users_table:
        if users_table[user_id]["email"] == email or users_table[user_id]["phone"] == phone:
            raise HTTPException(status_code=409, detail="Email or phone number already in use")

    user_id = str(len(users_table))
    users_table[user_id] = {"username": username,
                            "password": password,
                            "email": email,
                            "phone": phone,
                            "country": country}


def find_user_by_login_data(email: str, password: str):
    return next(([user_id, users_table[user_id]] for user_id in users_table if
                 users_table[user_id]["email"] == email and users_table[user_id]["password"] == password), None)


def get_userdata_by_id(user_id):
    return users_table[user_id]


def edit_users_profile(user_id, field_to_change: str, new_value: str):
    users_table[user_id][field_to_change] = new_value


def delete_user_from_db(user_id):
    users_table.pop(user_id)

    decks_to_delete = []
    for deck_id in decks_table:
        if decks_table[deck_id]["creator"] == user_id:
            decks_to_delete.append(deck_id)
    for deck_id in decks_to_delete:
        decks_table.pop(deck_id)

    cards_to_delete = []
    for card_id in cards_table:
        if cards_table[card_id]["deck_id"] in decks_to_delete:
            cards_to_delete.append(card_id)
    for card_id in cards_to_delete:
        cards_table.pop(card_id)


def add_deck(name: str, creator: str, description: str):
    deck_id = str(len(decks_table))
    decks_table[deck_id] = {"name": name, "creator": creator, "description": description}
    return deck_id


def get_deck_by_id(deck_id: str, user_id: str):
    check_deck_for_user(user_id, deck_id)
    return decks_table[deck_id]


def check_deck_for_user(user_id: str, deck_id: str):
    if deck_id not in decks_table:
        raise HTTPException(status_code=404,
                            detail='This deck is not found')
    if decks_table[deck_id]["creator"] == user_id:
        return
    else:
        raise HTTPException(status_code=404,
                            detail='This deck does not belong to this user')


def edit_deck_in_db(user_id, deck_id, field_to_change, new_value):
    check_deck_for_user(user_id, deck_id)
    decks_table[deck_id][field_to_change] = new_value


def delete_deck_from_db(user_id, deck_id):
    check_deck_for_user(user_id, deck_id)
    decks_table.pop(deck_id)

    cards_to_delete = []
    for card_id in cards_table:
        if cards_table[card_id]["deck_id"] == deck_id:
            cards_to_delete.append(card_id)
    for card_id in cards_to_delete:
        cards_table.pop(card_id)


def get_users_decks(user_id: str):
    users_decks = {}
    for deck_id in decks_table:
        if decks_table[deck_id]["creator"] == user_id:
            users_decks[deck_id] = decks_table[deck_id]

    return users_decks


def add_card(english_word: str, translation: str, explanation: str, deck_id: str, user_id: str):
    check_deck_for_user(user_id, deck_id)
    card_id = str(len(cards_table))
    cards_table[card_id] = {"english_word": english_word, "translation": translation, "explanation": explanation,
                            "deck_id": deck_id}
    return card_id


def get_card_by_id(card_id: str, deck_id: str, user_id: str):
    check_deck_for_user(user_id, deck_id)
    check_card_for_deck(deck_id, card_id)
    return cards_table[card_id]


def check_card_for_deck(deck_id: str, card_id: str):
    if card_id not in cards_table:
        raise HTTPException(status_code=404,
                            detail='This card is not found')
    if cards_table[card_id]["deck_id"] == deck_id:
        return
    else:
        raise HTTPException(status_code=404,
                            detail='This deck does not contain such card')


def edit_card_in_db(user_id, deck_id, card_id, field_to_change, new_value):
    check_deck_for_user(user_id, deck_id)
    check_card_for_deck(deck_id, card_id)
    cards_table[card_id][field_to_change] = new_value


def delete_card_from_db(user_id, deck_id, card_id):
    check_deck_for_user(user_id, deck_id)
    check_card_for_deck(deck_id, card_id)
    cards_table.pop(card_id)


def get_decks_cards(user_id: str, deck_id: str):
    check_deck_for_user(user_id, deck_id)
    cards = {}
    for card_id in cards_table:
        if cards_table[card_id]["deck_id"] == deck_id:
            cards[card_id] = cards_table[card_id]

    return cards


def add_interest(user_id, text):
    interest_id = 20
    return interest_id


def edit_interest(user_id, interest_id):
    pass


def delete_interest(user_id, interest_id):
    pass


def get_interest(user_id, interest_id):
    return {"name": "music"}


def get_interests(user_id):
    return ["music", "sport", "reading"]


def add_post(user_id, text):
    post_id = 20
    return post_id


def edit_post(user_id, post_id):
    pass


def delete_post(user_id, post_id):
    pass


def get_post(user_id, post_id):
    return "It's more efficient to learn languages by cards!"


def get_posts(user_id):
    return ["It's more efficient to learn languages by cards!", "It is beneficial to talk to native speakers"]


def add_group(user_id, name, members):
    group_id = 20
    return group_id


def edit_group(user_id, group_id, field, value):
    pass


def delete_group(user_id, group_id):
    pass


def get_group(user_id, group_id):
    return {'name': 'BIV201', 'members': ['Daria, Kirill, Alexander, Oleg']}


def get_groups(user_id):
    return ["BIV201", "BIV202", "BIV203"]


def add_bank_card(user_id, number, exp_date, cvv):
    bank_card_id = 20
    return bank_card_id


def edit_bank_card(user_id, bank_card_id, field, value):
    pass


def delete_bank_card(user_id, bank_card_id):
    pass


def get_bank_card(user_id, bank_card_id):
    number = '1234567890123456'
    return {'type': 'MIR', 'number': number[-4:]}


def get_bank_cards(user_id):
    return [{'type': 'MIR', 'number': '3144'}, {'type': 'Visa', 'number': '7302'}]


def add_account(user_id, type, link):
    account_id = 20
    return account_id


def edit_account(user_id, account_id, field, value):
    pass


def delete_account(user_id, account_id):
    pass


def get_account(user_id, account_id):
    return {'type': 'Telegram', 'link': 't.me/someusername'}


def get_accounts(user_id):
    return [{'type': 'Telegram', 'link': 't.me/someusername'}, {'type': 'VK', 'link': 'vk.com/someuserprofile'}]


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
