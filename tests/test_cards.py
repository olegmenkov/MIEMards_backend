import authentification
import db
import db.db_functions


def test_create_card(client):
    # Регистрируемся и логинимся
    client.post("/profile/register", json={"username": "string", "password": "string", "email": "user@example.com",
                                           "phone": "string", "country": "string"})
    access_token = client.post("/profile/login", json={"email": "user@example.com", "password": "string"}).json()[
        'access_token']
    user_id = authentification.get_current_user(access_token)
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

    # Добавим колоду и карту
    deck_id = client.post("/decks", json={'name': 'Fruits',
                                          'description': 'Fruits for A1'}, headers=headers).json()["deck_id"]
    card_data = {"english_word": "apple", "translation": "яблоко", "explanation": "фрукт", "deck_id": deck_id}
    response = client.post('/cards', json=card_data, headers=headers)
    assert response.status_code == 200
    card_id = response.json()['card_id']
    assert card_id

    # Проверим, что она появилась в БД с этим айди и с этми данными
    card_data_from_db = db.db_functions.get_card_by_id(card_id, deck_id, user_id)
    assert card_data == card_data_from_db


def test_edit_card(client):
    #  логинимся
    access_token = client.post("/profile/login", json={"email": "user@example.com", "password": "string"}).json()[
        'access_token']
    user_id = authentification.get_current_user(access_token)
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

    # Добавим колоду и карту
    deck_id = client.post("/decks", json={'name': 'Animals',
                                          'description': ''}, headers=headers).json()["deck_id"]
    card_data = {"english_word": "dog", "translation": "собака", "explanation": "животное из семейства псовых",
                 "deck_id": deck_id}
    response = client.post('/cards', json=card_data, headers=headers)
    card_id = response.json()['card_id']

    # Отредактируем эту карту
    new_card_data = card_data
    new_card_data["explanation"] = "сочный плод яблони, который употребляется в пищу в свежем и запеченном виде"
    response = client.patch(f"/cards/?card_id={card_id}", json=new_card_data, headers=headers)
    assert response.status_code == 200

    # Проверим, что данные об этой карте в БД поменялись
    card_data_from_db = db.db_functions.get_card_by_id(card_id, deck_id, user_id)
    assert card_data_from_db == new_card_data


def test_get_card(client):
    #  логинимся
    access_token = client.post("/profile/login", json={"email": "user@example.com", "password": "string"}).json()[
        'access_token']
    user_id = authentification.get_current_user(access_token)
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

    # Добавим колоду и карту
    deck_id = client.post("/decks", json={'name': 'School',
                                          'description': 'Things you can use at school'}, headers=headers).json()[
        "deck_id"]
    card_data = {"english_word": "pen", "translation": "ручка", "explanation": "предмет, пишущий чернилами",
                 "deck_id": deck_id}
    response = client.post('/cards', json=card_data, headers=headers)
    card_id = response.json()['card_id']

    # Удалим карту
    response = client.delete(f'/cards/?card_id={card_id}&deck_id={deck_id}', headers=headers)

    # Проверим, что она правда удалилась
    response = client.get(f"/cards/get_card_by_id/?deck_id={deck_id}&card_id={card_id}", headers=headers)
    assert response.status_code == 404
    assert response.json() == {'detail': 'This card is not found'}
