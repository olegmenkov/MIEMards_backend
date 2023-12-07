'''import authentification
import db
import db.db_functions


def test_add_group(client):
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

    # Добавим новую группу
    group_data_input = {"name": "BIV201", "users": "Darya, Kirill, Alexander, Oleg"}
    response = client.post('/groups', json=group_data_input, headers=headers)
    assert response.status_code == 200
    group_id = response.json()['group_id']
    assert group_id

    # Проверим, что она правильно добавилась
    group_data_from_db = db.db_functions.get_group(user_id, group_id)
    assert group_data_input == group_data_from_db


def test_edit_group(client):
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

    # Добавим новую группу
    old_group_data_input = {"name": "BIV201", "users": "Darya, Kirill, Alexander, Oleg"}
    group_id = client.post('/groups', json=old_group_data_input, headers=headers).json()['group_id']

    # Отредактируем её и проверим, что в БД данные изменились
    new_group_data_input = old_group_data_input
    new_group_data_input["name"] = "БИВ201 - MIEMards"
    response = client.patch(f"/groups?group_id={group_id}", json=new_group_data_input, headers=headers)
    assert response.status_code == 200

    group_data_from_db = db.db_functions.get_group(user_id, group_id)
    assert group_data_from_db == new_group_data_input


def test_delete_group(client):
    #  логинимся
    access_token = client.post("/profile/login", json={"email": "user@example.com", "password": "string"}).json()[
        'access_token']
    user_id = authentification.get_current_user(access_token)
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

    # Добавим новую группу
    old_group_data_input = {"name": "BIV201", "users": "Darya, Kirill, Alexander, Oleg"}
    group_id = client.post('/groups', json=old_group_data_input, headers=headers).json()['group_id']

    # Удалим группу
    response = client.delete(f'/groups/?group_id={group_id}', headers=headers)

    # Проверим, что она правда удалилась
    response = client.get(f"/groups/get_group_by_id/?group_id={group_id}", headers=headers)
    assert response.status_code == 404
    assert response.json() == {'detail': 'This group is not found'}

'''