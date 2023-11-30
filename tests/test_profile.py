def test_register_success(client):
    """
    Test successful user registration
    :param client:
    :return:
    """
    response = client.post("/profile/register",
                           json={"username": "testuser", "password": "testpassword", "email": "test@example.com",
                                 # "phone": "1234567890",
                                 "country": "Testland"})
    assert response.status_code == 200
    assert response.json()


def test_register_bad_email(client):
    """
    Test user registration with an email that does not match the template
    :param client:
    :return:
    """
    response = client.post("/profile/register",
                           json={"username": "testuser", "password": "testpassword", "email": "test",
                                 "phone": "1234567890", "country": "Testland"})
    assert response.status_code == 422


def test_register_no_required_fields(client):
    """
    Test user registration with too few fields
    :param client:
    :return:
    """
    response = client.post("/profile/register",
                           json={"username": "testuser", "email": "test@example.com",
                                 "phone": "1234567890", "country": "Testland"})
    assert response.status_code == 422


def test_login_user_not_existing(client):
    """
    Test non-existing user login
    :param client:
    :return:
    """
    response = client.post("/profile/login", json={"email": "not-existing@email.com", "password": "testpassword"})
    assert response.status_code == 401
    assert response.json() == {'detail': "Invalid email or password"}


def test_login_user_success(client):
    """
    Test user registration
    :param client:
    :return:
    """
    response = client.post("/profile/login", json={"email": "test@example.com", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_create_deck(client):
    response = client.post("/profile/login", json={"email": "test@example.com", "password": "testpassword"})
    access_token = response.json()['access_token']

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
    # Логинимся

    response = client.post("/profile/login", json={"email": "test@example.com", "password": "testpassword"})
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
