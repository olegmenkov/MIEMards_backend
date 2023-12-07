import authentification
from db.db_functions import get_userdata_by_id, find_user_by_login_data
from db.db_class import Database
import asyncio
import pytest

HOST = 'localhost'
PORT = 5433
DATABASE = 'miemards'
USERNAME = 'postgres'
PASSWORD = 'postgres'


@pytest.fixture
async def database():
    return Database(HOST, PORT, USERNAME, PASSWORD, DATABASE)


@pytest.mark.asyncio
async def test_register_success(client, database):
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
    user_data_in_db = await get_userdata_by_id(await database, user_id)
    assert tuple(user_data_input.values()) == user_data_in_db


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
    assert not await find_user_by_login_data(await database, email, password)

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
    user_data_in_db = await get_userdata_by_id(await database, user_id)
    assert user_data_in_db == tuple(user_data.values())
