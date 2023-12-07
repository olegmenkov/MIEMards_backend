import authentification
import db
import db.db_functions


def test_add_post(client):
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

    # Добавим новый пост
    post_data_input = {
        "text": "Hi everyone! I am new to MIEMards. Here I am gonna post some useful tips for language learning."}
    response = client.post("/posts", json=post_data_input, headers=headers)
    assert response.status_code == 200
    post_id = response.json()["post_id"]
    assert post_id
    post_data_from_db = db.db_functions.get_post(user_id, post_id)
    assert post_data_from_db == post_data_input


def test_delete_post(client):
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

    # Добавим новый пост
    post_data_input = {
        "text": "Hi everyone! I am new to MIEMards. Here I am gonna post some useful tips for language learning."}
    post_id = client.post("/posts", json=post_data_input, headers=headers).json()["post_id"]

    # Удалим его из БД и проверим, что его там правда больше нет
    db.db_functions.delete_post(user_id, post_id)
    response = client.get(f"/cards/get_post_by_id/?post_id={post_id}", headers=headers)
    assert response.status_code == 404
    assert response.json() == {'detail': 'This post is not found'}


def test_get_users_posts(client):
    # Регистрируемся
    user_data_input = {"username": "Petya", "password": "12345", "email": "petya@example.com",
                       "phone": "89109836725", "country": "Russia"}
    response = client.post("/profile/register", json=user_data_input)

    # Логинимся под этим новым пользователем, получаем токен, из которого будем брать ID
    access_token = client.post("/profile/login", json={"email": "petya@example.com", "password": "12345"}).json()[
        'access_token']
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    # Добавим ему посты
    post_data_input1 = {
        "text": "Hi everyone! I am new to MIEMards. Here I am gonna post some useful tips for language learning."}
    client.post("/posts", json=post_data_input1, headers=headers)
    post_data_input2 = {
        "text": "The first tip: always learn new words by their images. Don't translate it to your native language."}
    client.post("/posts", json=post_data_input2, headers=headers)

    # Посмотрим список постов этого пользователя
    data = client.get("/posts/show_posts_of_user", headers=headers).json()
    assert post_data_input1["text"] in data
    assert post_data_input2["text"] in data
