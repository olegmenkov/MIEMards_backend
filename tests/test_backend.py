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
