# MIEMards_backend

Все команды выполняются в папке MIEMards_backend

## Настроить проект
Для того, чтобы все функции импортировались правильно, необходимо отметить корневую директорию MIEMards_backend как "Sources Root". В среде PyCharm это можно сделать, кликнув правой кнопкой мыши по папке и нажав "Mark Directory as > Sources Root" 

## Добавить файл .env 
При локальном запуске нужно создать в корневой директории MIEMards_backend файл ```.env``` и вписать в него следующее:
```
AUTH_KEY=any-key
ENC_KEY=generated-fernet-key
```
без пробелов и кавычек. 
Замените ```any-key``` и ```generated-ferner-key``` на секретные ключи для шифрования. 
Вы можете придумать или сгенерировать ```any-key``` любым удобным способом, а для получения ```generated-fernet-key``` выполните следующий скрипт и вставьте то, что он вывел, без кавычек и символа 'b'
```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key)
```
Пример файла:
```
AUTH_KEY=my-very-secret-key
ENC_KEY=SeaEe_J_TOrbkRnkoqRq3aPfE8cioZuntSx679oShxU=
```

## Установить зависимости

```shell
pip install -r requirements.txt
```

или

```shell
pip3 install -r requirements.txt
```

**!ВАЖНО!**

**Выполнять установку нужно в консоли от имени администратора**

## Запустить приложение

```shell
uvicorn main:app --reload
```


## Запустить тесты

1. Установить на своё устройство утилиту ```make``` (если вы используете Windows, добавить путь к "your/path/to/GnuWin32/bin/make.exe" в переменную среды PATH)
2. Выполнить команду
```shell
make test
```

## Запустить линтер
1. Установить на своё устройство утилиту ```make``` (если вы используете Windows, добавить путь к "your/path/to/GnuWin32/bin/make.exe" в переменную среды PATH)
2. Выполнить команду
```shell
make lint
```

# Поднять базу данных
1. Поднимаете в докере базу данных
```shell
docker-compose up -d
```
или
```shell
docker compose up -d
```
2. ревизия
```alembic revision --autogenerate -m "Added new tables"```
3. обновление
```alembic upgrade head```