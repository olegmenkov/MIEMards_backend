import authentification
import db
import db.db_functions


def test_add_acc(client):
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

    # Добавим новый аккаунт
    acc_data_input = {"type": "VK", "link": "vk.com/id37364638"}
    response = client.post('/social_accounts', json=acc_data_input, headers=headers)
    assert response.status_code == 200
    account_id = response.json()['account_id']
    assert account_id

    # Проверим, что он правильно добавился
    account_data_from_db = db.db_functions.get_account(user_id, account_id)
    assert account_data_from_db == acc_data_input


def test_delete_acc(client):
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

    # Добавим новый аккаунт
    acc_data_input = {"type": "VK", "link": "vk.com/id37364638"}
    account_id = client.post('/social_accounts', json=acc_data_input, headers=headers).json()['account_id']

    # Удалим аккаунт
    response = client.delete(f'/groups/?account_id={account_id}', headers=headers)
    assert response.status_code == 200

    # Проверим, что он правда удалился
    response = client.get(f"/groups/get_account_by_id/?account_id={account_id}", headers=headers)
    assert response.status_code == 404
    assert response.json() == {'detail': 'This account is not found'}


def test_edit_acc(client):
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

    # Добавим новый аккаунт
    old_acc_data = {"type": "VK", "link": "vk.com/id37364638"}
    account_id = client.post('/social_accounts', json=acc_data_input, headers=headers).json()['account_id']

    # Отредактируем аккаунт и проверим, что он поменялся
    new_acc_data = old_acc_data
    new_acc_data["link"] = "vk.com/miemards"
    response = client.patch(f"/?account_id={account_id}",
                            json=new_acc_data, headers=headers)
    assert response.status_code == 200
    account_data_from_db = db.db_functions.get_account(user_id, account_id)
    assert account_data_from_db == new_acc_data