from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import datetime
from datetime import datetime
from datetime import timedelta
import os
from dotenv import load_dotenv
from loguru import logger


# Используем протокол авторизации OAuth 2.0
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# Загружаем секретный ключ для генерации токена из переменных среды
load_dotenv()
AUTH_KEY = os.getenv('AUTH_KEY')
ALGORITHM = "HS256"


def create_access_token(data: dict):
    """
    Создаёт токен
    :param data: информация, которую надо зашифровать в токене
    :return: токен
    """
    to_encode = data.copy()     # определяем, что кодировать (у нас это будет айди пользователя)
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})       # добавляем время, когда токен перестанет действовать
    encoded_jwt = jwt.encode(to_encode, AUTH_KEY, algorithm=ALGORITHM)    # кодируем
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Функция для получения текущего пользователя по токену
    """

    credentials_exception = HTTPException(      # ошибка
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, AUTH_KEY, algorithms=[ALGORITHM])     # раскодируем инфу
        user_id: str = payload.get("sub")   # получаем оттуда id
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError as e:
        logger.debug(e)
        raise credentials_exception
