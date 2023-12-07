'''import authentification
import db
import db.db_functions


def test_add_interest(client):
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
    interest_data_from_db = db.db_functions.get_interest(user_id, interest_id)
    assert interest_data_from_db == interest_data


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

    # Теперь проверяем, что его можно получить -- получаем его по ID и проверяем корректнуа ли информация
    response = client.get(f'/interests/get_interest_by_id/?interest_id={interest_id}', headers=headers)

    assert response.status_code == 200
    assert response.json()["name"] == interest_name


def test_edit_interest(client):
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
    interest_data_from_db = db.db_functions.get_interest(user_id, interest_id)
    assert interest_data_from_db == new_interest_data
'''