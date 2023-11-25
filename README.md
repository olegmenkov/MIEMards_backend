# MIEMards_backend

Все команды выполняются в папке MIEMards_backend

## Добавить файл .env 
При локальном запуске нужно создать в корневой директории MIEMards_backend файл ".env" и вписать в него следующее:
```
SECRET_KEY=your-secret-key
```
без пробелов и кавычек. Замените ```your-secret-key``` на секретный ключ для шифрования

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

1. Установить на своё устройство утилиту ```make```
2. Выполнить команду
```shell
make test
```

## Запустить линтер

```shell
make lint
```
