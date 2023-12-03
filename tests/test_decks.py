
def test_create_deck(client):
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

    deck_data = {
        'name': 'MyDeck',
        'description': 'Description of MyDeck',
    }

    response = client.post("/decks", json=deck_data, headers=headers)

    assert response.status_code == 200
    assert "deck_id" in response.json()


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
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    deck_data = {
        'name': 'MyDeck',
        'description': 'Description of MyDeck',
    }

    # Добавляем колоду

    response = client.post("/decks", json=deck_data, headers=headers)
    deck_id = response.json()["deck_id"]

    # Смотрим колоды пользователя

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    response = client.get("/decks/show_decks_of_user", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) != 0
    assert response.json()[deck_id]["name"] == 'MyDeck'
    assert response.json()[deck_id]["description"] == 'Description of MyDeck'


def test_get_deck(client):

    response = client.post("/profile/login", json={"password": "54321", "email": "masha@example.com"})
    access_token = response.json()['access_token']

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    response = client.get("/decks/get_deck_by_id/?deck_id=0", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"creator": "1", "name": "A1", "description": "vocabulary for beginners"}