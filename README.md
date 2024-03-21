# MIEMards_backend

MIEMards - сервис по изучению английских слов по карточкам. Основная особенность нашего сервиса - это использование искуственного интеллекта, который помогает нашим пользователям более качественно изучать иностранный язык. Используя MIEMards, вы можете создавать свои собственные тематические колоды с карточками или прибегать к помощи ИИ, который умеет создавать колоды и карточки именно для вас, основываясь на ваших интересах, целях и увлечениях. Также наше приложение предлагает вам генерировать перевод и иллюстрации к каждой карточке, чтобы лучше запоминать значения слов. Создав или сгенерировав свои колоды и карточки, вы сможете учить их в игровой форме и соревноваться с другими игроками, а также отслеживать свой прогресс.  

В данном репозитории находится код для back-end (серверной) части нашего сервиса. Front-end находится по [ссылке](https://github.com/No-Name-px/miemards).

## Инструкция по установке
### Клонировать код
```
git clone https://github.com/olegmenkov/MIEMards_backend.git
```
После этого нужно перейти в созданную автоматически папку MIEMards_backend
### Добавить файл .env 
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

### Установить зависимости

```shell
pip install -r requirements.txt
```

или

```shell
pip3 install -r requirements.txt
```

**!ВАЖНО!**

**Выполнять установку нужно в консоли от имени администратора**

### Поднять базу данных
1. Поднимаете в докере базу данных
```shell
docker-compose up -d
```
или
```shell
docker compose up -d
```
2. Делаете ревизию
```alembic revision --autogenerate -m "Added new tables"```
3. Обновляете
```alembic upgrade head```

### Запустить приложение

```shell
uvicorn main:app --reload
```


### Запустить тесты

1. Установить на своё устройство утилиту ```make``` (если вы используете Windows, добавить путь к "your/path/to/GnuWin32/bin/make.exe" в переменную среды PATH)
2. Выполнить команду
```shell
make test
```

## Примеры использования

Примеры использования проекта MIEMards вы можете найти в нашей [пользовательской документации](https://docs.google.com/document/d/11Q4lg1675mnOO6pmb2SldNC3Sfv87io6q4iJpIS47mw/edit)

## Ваш вклад

При обнаружении проблем или багов с использованием нашего проекта, вы можете создать issue. Для того, чтобы это сделать, перейдите во вкладку Issues в перхней части сайта
![Issues](https://github.com/olegmenkov/MIEMards_backend/assets/93485639/61c043b5-d783-4c0c-95f6-0ff56eca1224)
Затем нажмите на кнопку ```New issue```, опишите свою проблему и отправьте её. Мы постараемся оперативно вам помочь или исправить ошибку в нашем коде.
![New issue](https://github.com/olegmenkov/MIEMards_backend/assets/93485639/a6974d2e-4c4e-4441-baba-ec96d04be054)

С прочими предложениями приглашаем вас обращаться в Telegram: [@olegmenkov](https://t.me/olegmenkov "Telegram")

## Лицензия и авторство
В списке ниже перечислены авторы данного проекта, их контакты и их сферы ответственности:
1. [Дарья](https://t.me/d_a_r_i_u_s_s "Telegram") - дизайн  
2. [Кирилл](https://t.me/fac_ele_ss "Telegram") - front-end
3. [Александр](https://t.me/sanek_lapin "Telegram") - ИИ
4. [Олег](https://t.me/olegmenkov "Telegram") - back-end

MIT License

Copyright (c) [2024] [Боброва Дарья Михайловна, Коруняк Кирилл Дмитриевич, Лапин Александр Александрович, Меньков Олег Георгиевич]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
