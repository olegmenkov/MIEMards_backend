import requests

# Логинимся под этим новым пользователем, получаем токен, из которого будем брать ID
response = requests.post("http://127.0.0.1:8000/profile/login", json={"email": "vasya@example.com", "password": "12345"})
access_token = response.json()['access_token']
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json',
}

response = requests.get("http://127.0.0.1:8000/posts/show_posts_of_user", headers=headers)
print(response.status_code)
print(response.json())