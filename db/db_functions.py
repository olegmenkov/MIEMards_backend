from pydantic import EmailStr
from fastapi import HTTPException
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
    return next((user_id for user_id in users_table if
                 users_table[user_id]["email"] == email and users_table[user_id]["password"] == password), None)


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
        if cards_table[card_id]["deck"] in decks_to_delete:
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
        if cards_table[card_id]["deck"] == deck_id:
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
    decks_table[deck_id] = {"english_word": english_word, "translation": translation, "explanation": explanation,
                            "deck_id": deck_id}
    return card_id


def get_card_by_id(card_id: str, deck_id: str, user_id: str):
    check_deck_for_user(user_id, deck_id)
    check_card_for_deck(deck_id, card_id)
    return cards_table[card_id]


def check_card_for_deck(deck_id: str, card_id: str):
    if cards_table[card_id]["creator"] == deck_id:
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
    cards_table.pop(deck_id)


def get_decks_cards(user_id: str, deck_id: str):
    check_deck_for_user(user_id, deck_id)
    cards = {}
    for card_id in cards_table:
        if cards_table[card_id]["deck"] == deck_id:
            cards[card_id] = cards_table[card_id]

    return cards
