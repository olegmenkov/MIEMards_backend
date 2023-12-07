import authentification
import db
import db.db_functions


def test_add_bank_card(client):
    # Регистрируемся
    user_data_input = {"username": "Petya", "password": "12345", "email": "petya@example.com",
                       "phone": "89109836725", "country": "Russia"}
    response = client.post("/profile/register", json=user_data_input)

    # Логинимся под этим новым пользователем, получаем токен, из которого будем брать ID
    access_token = client.post("/profile/login", json={"email": "petya@example.com", "password": "12345"}).json()[
        'access_token']
    user_id = authentification.get_current_user(access_token)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    # Добавим банковскую карту
    bank_card_data = {"number": "1234567890123456",
                      "exp_date": "09/25",
                      "cvv": "736"}
    response = client.post("/bank_cards", json=bank_card_data, headers=headers)
    assert response.status_code == 200
    bank_card_id = response.json()["bank_card_id"]

    # Проверим, что она появилась в БД с этим айди и с этми данными
    bank_card_data_from_db = db.db_functions.get_bank_card(user_id, bank_card_id)
    assert bank_card_data == bank_card_data_from_db


def test_edit_bank_card(client):
    # Регистрируемся
    user_data_input = {"username": "Petya", "password": "12345", "email": "petya@example.com",
                       "phone": "89109836725", "country": "Russia"}
    response = client.post("/profile/register", json=user_data_input)

    # Логинимся под этим новым пользователем, получаем токен, из которого будем брать ID
    access_token = client.post("/profile/login", json={"email": "petya@example.com", "password": "12345"}).json()[
        'access_token']
    user_id = authentification.get_current_user(access_token)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    # Добавим банковскую карту
    bank_card_data = {"number": "1234567890123456", "exp_date": "09/25", "cvv": "736"}
    bank_card_id = client.post("/bank_cards", json=bank_card_data, headers=headers).json()["bank_card_id"]

    # Отредактируем и проверим, что изменения добавились
    new_exp_date = "09/28"
    db.db_functions.edit_bank_card(user_id, bank_card_id, "exp_date", new_exp_date)
    bank_card_data_from_db = db.db_functions.get_bank_card(user_id, bank_card_id)
    assert bank_card_data_from_db["exp_date"] == new_exp_date


def test_delete_bank_card(client):
    # Регистрируемся
    user_data_input = {"username": "Petya", "password": "12345", "email": "petya@example.com",
                       "phone": "89109836725", "country": "Russia"}
    response = client.post("/profile/register", json=user_data_input)

    # Логинимся под этим новым пользователем, получаем токен, из которого будем брать ID
    access_token = client.post("/profile/login", json={"email": "petya@example.com", "password": "12345"}).json()[
        'access_token']
    user_id = authentification.get_current_user(access_token)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    # Добавим банковскую карту
    bank_card_data = {"number": "1234567890123456", "exp_date": "09/25", "cvv": "736"}
    bank_card_id = client.post("/bank_cards", json=bank_card_data, headers=headers).json()["bank_card_id"]

    # Удалим её и проверим, что она удалена
    db.db_functions.delete_bank_card(user_id, bank_card_id)
    response = client.get(f"/bank_cards/get_bank_card_by_id/?bank_card_id={bank_card_id}, headers=headers")
    assert response.status_code == 404
    assert response.json() == {'detail': 'This card is not found'}


def test_get_bank_cards(client):
    # Регистрируемся
    user_data_input = {"username": "Petya", "password": "12345", "email": "petya@example.com",
                       "phone": "89109836725", "country": "Russia"}
    response = client.post("/profile/register", json=user_data_input)

    # Логинимся под этим новым пользователем, получаем токен, из которого будем брать ID
    access_token = client.post("/profile/login", json={"email": "petya@example.com", "password": "12345"}).json()[
        'access_token']
    user_id = authentification.get_current_user(access_token)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    # Добавим банковскую карту
    number = "1234567890123456"
    bank_card_data = {"number": number, "exp_date": "09/25", "cvv": "736"}
    client.post("/bank_cards", json=bank_card_data, headers=headers).json()["bank_card_id"]

    # Проверим карты этого пользователя
    bank_card_data_from_db = db.db_functions.get_bank_cards(user_id)
    assert len(bank_card_data_from_db) == 1
    assert bank_card_data_from_db[0] == number
