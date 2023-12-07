'''import authentification
import db
import db.db_functions
from db.db_class import Database
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
async def test_create_deck(client, database):
    async with database.pool.acquire() as conn:
        async with conn.transaction():
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
            deck_data_from_db = await db.db_functions.get_deck_by_id(await database, deck_id, user_id)
            assert tuple(deck_data.values()) == deck_data_from_db



def test_show_users_decks(client):
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
    deck_data = {'name': 'MyDeck', 'description': 'Description of MyDeck'}
    response = client.post("/decks", json=deck_data, headers=headers)
    deck_id = response.json()["deck_id"]

    # Смотрим колоды пользователя
    response = client.get("/decks/show_decks_of_user", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) != 0
    assert response.json() == deck_data


@pytest.mark.asyncio
async def test_delete_deck(db, client):
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
    deck_data_from_db = await db.db_functions.get_deck_by_id(deck_id, authentification.get_current_user(access_token))
    assert deck_data_from_db

    # Теперь удалим и проверим, что она правда удалилась
    client.delete(f"/decks/?deck_id={deck_id}", headers=headers)
    response = client.get(f"/decks/get_deck_by_id/?deck_id={deck_id}", headers=headers)
    assert response.status_code == 404
    assert response.json() == {'detail': 'This deck is not found'}
'''