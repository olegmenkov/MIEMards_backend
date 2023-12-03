def test_register_success(client):
    """
    Test successful user registration
    :param client:
    :return:
    """
    response = client.post("/profile/register",
                           json={"username": "testuser", "password": "testpassword", "email": "test@example.com",
                                 # "phone": "1234567890", # необязательные поля можно не вводить
                                 "country": "Testland"})
    assert response.status_code == 200
    assert response.json()


def test_register_no_required_fields(client):
    """
    Test user registration with too few fields
    :param client:
    :return:
    """
    response = client.post("/profile/register",
                           json={"username": "testuser", "email": "test@example.com", # нет пароля -- обязательного поля
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
