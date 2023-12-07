import authentification
import db
import db.db_functions
from db.db_class import Database
import pytest
from httpx import AsyncClient
from main import app

HOST = 'localhost'
PORT = 5433
DATABASE = 'miemards'
USERNAME = 'postgres'
PASSWORD = 'postgres'


@pytest.fixture
async def database():
    return Database(HOST, PORT, USERNAME, PASSWORD, DATABASE)


@pytest.mark.asyncio
async def test_register_success(database, client):
    """
    Test successful user registration
    :param client:
    :param database:
    :return:
    """
    # Регистрируемся
    user_data_input = {"username": "Petya", "password": "12345", "email": "petya@example.com",
                       "phone": "89109836725", "country": "Russia"}
    response = client.post("/profile/register", json=user_data_input)
    assert response.status_code == 200

    # Логинимся под этим новым пользователем, получаем токен, из которого будем брать ID
    access_token = client.post("/profile/login", json={"email": "petya@example.com", "password": "12345"}).json()[
        'access_token']
    assert access_token
    user_id = authentification.get_current_user(access_token)

    # Проверяем, что в БД добавилась та же информация, что мы отправили
    user_data_in_db = await db.db_functions.get_userdata_by_id(await database, user_id)
    user_data_input.pop("password")
    assert user_data_input == user_data_in_db


@pytest.mark.asyncio
async def test_login_user_not_existing(client, database):
    """
    Test non-existing user login
    :param client:
    :param database:
    :return:
    """

    # несуществующие данные
    email = "not-existing@example.com"
    password = "notexistingpasswd"

    # проверяем, что таких пользователей правда нет в БД
    assert not await db.db_functions.find_user_by_login_data(await database, email, password)

    # проверяем, что приложение вернёт ошибку при попытке залогиниться под этим пользователем
    response = client.post("/profile/login", json={"email": email, "password": email})
    assert response.status_code == 401
    assert response.json() == {'detail': "Invalid email or password"}


@pytest.mark.asyncio
async def test_profile_edited_correctly(client, database):
    # Регистрируемся
    user_data = {"username": "Luka", "password": "12345", "email": "luka@example.com",
                       "phone": "+38 910-983-6725", "country": "Yugoslavia"}
    response = client.post("/profile/register", json=user_data)
    assert response.status_code == 200

    # Логинимся под этим новым пользователем, получаем токен, из которого будем брать ID
    access_token = client.post("/profile/login", json={"email": "luka@example.com", "password": "12345"}).json()[
        'access_token']
    assert access_token
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    # Меняем некоторые поля
    user_data["country"] = "Serbia"
    user_data["phone"] = "+381 910-983-6725"
    response = client.patch("/profile", json=user_data, headers=headers)
    assert response.status_code == 200

    # Проверяем, что в БД они тоже поменялись
    user_id = authentification.get_current_user(access_token)
    user_data_in_db = await db.db_functions.get_userdata_by_id(await database, user_id)
    user_data.pop("password")
    assert user_data_in_db == user_data


@pytest.mark.asyncio
async def test_create_deck(client, database):
    # Регистрируемся и логинимся
    client.post("/profile/register", json={
        "username": "string",
        "password": "string",
        "email": "user@example.com",
        "phone": "string",
        "country": "string"
    })
    access_token = client.post("/profile/login", json={"email": "user@example.com", "password": "string"}).json()[
        'access_token']
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

    # Добавляем новую колоду
    deck_data = {
        'name': 'MyDeck',
        'description': 'Description of MyDeck',
    }
    response = client.post("/decks", json=deck_data, headers=headers)
    assert response.status_code == 200

    # Проверим, что колода добавилась в том виде, в котором мы её добавили
    deck_id = response.json()["deck_id"]
    user_id = authentification.get_current_user(access_token)
    deck_data_from_db = await db.db_functions.get_deck_by_id(await database, deck_id)
    assert deck_data == deck_data_from_db


@pytest.mark.asyncio
async def test_show_users_decks(client):
    # Регистрируемся и логинимся
    client.post("/profile/register", json={
        "username": "string",
        "password": "string",
        "email": "user@example.com",
        "phone": "string",
        "country": "string"
    })
    access_token = client.post("/profile/login", json={"email": "user@example.com", "password": "string"}).json()[
        'access_token']
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

    # Добавляем колоду
    deck_data = {'name': 'dog', 'description': 'dogDesc'}
    response = client.post("/decks", json=deck_data, headers=headers)
    assert response.status_code == 200

    deck_id = response.json()["deck_id"]

    # Смотрим колоды пользователя
    response = client.get(f"/decks/get_deck_by_id?deck_id={deck_id}", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) != 0
    assert response.json() == deck_data


@pytest.mark.asyncio
async def test_delete_deck(database, client):
    # Регистрируемся и логинимся
    client.post("/profile/register", json={
        "username": "string",
        "password": "string",
        "email": "user@example.com",
        "phone": "string",
        "country": "string"
    })
    access_token = client.post("/profile/login", json={"email": "user@example.com", "password": "string"}).json()[
        'access_token']
    assert access_token
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

    # Добавляем колоду и проверяем по ID, что она добавилась
    response = client.post("/decks", json={'name': 'MyDeck', 'description': 'Description of MyDeck'}, headers=headers)
    deck_id = response.json()["deck_id"]
    deck_data_from_db = await db.db_functions.get_deck_by_id(await database, deck_id)
    assert deck_data_from_db

    # Теперь удалим и проверим, что она правда удалилась
    client.delete(f"/decks/?deck_id={deck_id}", headers=headers)
    response = client.get(f"/decks/get_deck_by_id/?deck_id={deck_id}", headers=headers)
    assert response.status_code == 404
    assert response.json() == {'detail': 'This deck is not found'}


@pytest.mark.asyncio
async def test_create_card(database, client):
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
    card_data_from_db = await db.db_functions.get_card_by_id(await database, card_id)
    card_data.pop("deck_id")
    assert card_data == card_data_from_db


@pytest.mark.asyncio
async def test_edit_card(database, client):
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
    card_data_from_db = await db.db_functions.get_card_by_id(await database, card_id)
    new_card_data.pop("deck_id")
    assert card_data_from_db == new_card_data


@pytest.mark.asyncio
async def test_delete_card(client):
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
    response = client.delete(f'/cards/?card_id={card_id}', headers=headers)

    # Проверим, что она правда удалилась
    response = client.get(f"/cards/get_card_by_id/?card_id={card_id}", headers=headers)
    assert response.status_code == 404
    assert response.json() == {'detail': 'This card is not found'}


@pytest.mark.asyncio
async def test_add_interest(database, client):
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

    # Добавляем новый интерес
    interest_data = {"name": "sport"}
    response = client.post("/interests",
                           json=interest_data, headers=headers)
    assert response.status_code == 200
    interest_id = response.json()["interest_id"]
    assert interest_id

    # Проверяем, что в БД он появился с правильными данными
    interest_data_from_db = await db.db_functions.get_interest(await database, interest_id)
    assert interest_data_from_db == interest_data


@pytest.mark.asyncio
async def test_get_interest(client):
    # Регистрируемся и логинимся
    client.post("/profile/register", json={
        "username": "string",
        "password": "string",
        "email": "user@example.com",
        "phone": "string",
        "country": "string"
    })
    access_token = client.post("/profile/login", json={"email": "user@example.com", "password": "string"}).json()[
        'access_token']
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    # Добавляем новый интерес
    interest_name = "music"
    response = client.post("/interests",
                           json={"name": interest_name}, headers=headers)
    interest_id = response.json()['interest_id']

    # Теперь проверяем, что его можно получить -- получаем его по ID и проверяем корректнуа ли информация
    response = client.get(f'/interests/get_interest_by_id/?interest_id={interest_id}', headers=headers)

    assert response.status_code == 200
    assert response.json()["name"] == interest_name


@pytest.mark.asyncio
async def test_edit_interest(database, client):
    # Регистрируемся
    user_data_input = {"username": "Petya", "password": "12345", "email": "petya@example.com",
                       "phone": "89109836725", "country": "Russia"}
    response = client.post("/profile/register", json=user_data_input)

    # Логинимся под этим новым пользователем, получаем токен, из которого будем брать ID
    access_token = client.post("/profile/login", json={"email": "petya@example.com", "password": "12345"}).json()[
        'access_token']
    assert access_token
    user_id = authentification.get_current_user(access_token)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    # Добавляем новый интерес
    old_interest_data = {"name": "chess"}
    response = client.post("/interests",
                           json=old_interest_data, headers=headers)
    interest_id = response.json()["interest_id"]

    # Отредактируем интерес и проверим, что он поменялся
    new_interest_data = old_interest_data
    new_interest_data["name"] = "rowing"
    response = client.patch(f"/interests?interest_id={interest_id}",
                            json=new_interest_data, headers=headers)
    assert response.status_code == 200
    interest_data_from_db = await db.db_functions.get_interest(await database, interest_id)
    assert interest_data_from_db == new_interest_data
