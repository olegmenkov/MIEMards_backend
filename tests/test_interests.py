def test_add_interest(client):
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
    response = client.post("/interests",
                           json={"name": "sport"}, headers=headers)
    assert response.status_code == 200
    assert 'interest_id' in response.json()


def test_get_interest(client):
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

    # Теперь проверяем, что он появился -- получаем его по ID
    response = client.get(f'/interests/get_interest_by_id/?interest_id={interest_id}', headers=headers)

    assert response.status_code == 200
    assert response.json()["name"] == interest_name
