def test_register_user(client):
    """
    Test successful user registration
    :param client:
    :return:
    """
    response = client.post("/register",
                           json={"username": "testuser", "password": "testpassword", "email": "test@example.com",
                                 "phone": "1234567890", "country": "Testland"})
    assert response.status_code == 200
    assert response.json()


def test_login_user(client):
    """
    Test successful user registration
    :param client:
    :return:
    """
    response = client.post("/login", json={"email": "test@example.com", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_create_deck(client):
    response = client.post("/login", json={"email": "test@example.com", "password": "testpassword"})
    access_token = response.json()['access_token']

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    deck_data = {
        'name': 'MyDeck',
        'description': 'Description of MyDeck',
    }

    response = client.post("/decks/add", json=deck_data, headers=headers)

    assert response.status_code == 200
    assert "deck_id" in response.json()


def test_show_users_decks(client):
    # Логинимся

    response = client.post("/login", json={"email": "test@example.com", "password": "testpassword"})
    access_token = response.json()['access_token']

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    deck_data = {
        'name': 'MyDeck',
        'description': 'Description of MyDeck',
    }

    # Добавляем колоду

    response = client.post("/decks/add", json=deck_data, headers=headers)
    deck_id = response.json()["deck_id"]

    # Смотрим колоды пользователя

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    response = client.get("/decks/show_users_decks", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) != 0
    assert response.json()[deck_id]["name"] == 'MyDeck'
    assert response.json()[deck_id]["description"] == 'Description of MyDeck'

