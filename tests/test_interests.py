def test_add_interest(client):
    access_token = client.post("/profile/login", json={"email": "vasya@example.com", "password": "12345"}).json()[
        'access_token']

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    response = client.post("/interests",
                           json={"name": "sport"}, headers=headers)
    assert response.status_code == 200
    assert 'interest_id' in response.json()


def test_get_interest(client):
    access_token = client.post("/profile/login", json={"email": "vasya@example.com", "password": "12345"}).json()[
        'access_token']

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    interest_name = "music"
    response = client.post("/interests",
                           json={"name": interest_name}, headers=headers)
    interest_id = response.json()['interest_id']

    response = client.get(f'/interests/get_interest_by_id/?interest_id={interest_id}', headers=headers)

    assert response.status_code == 200
    assert response.json()["name"] == interest_name
