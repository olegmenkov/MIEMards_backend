from fastapi import HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse

import ai
from ai.generate_deck_recommendation import generate_deck_recommendation

from db.db_functions import profile, interests, decks, cards
import authentification
from db.db_class import Database
from schemas import *

from loguru import logger

from database_config import HOST, PORT, USERNAME, PASSWORD, DATABASE

db = Database(HOST, PORT, USERNAME, PASSWORD, DATABASE)


router = APIRouter()


@router.post("/register")
async def register(request_body: UserInfo):
    """
    Регистрирует в БД нового пользователя со всеми полями, указанными при регистрации
    """
    await profile.add(db, request_body.username, request_body.password, request_body.email, request_body.phone,
                      request_body.country)
    return JSONResponse(content={"message": "User registered successfully"})


@router.post("/login")
async def login(request_body: LoginModel):
    """
    Проверяет, существует ли пользователь с таким логином и паролем. Если да, возвращает токен для дальнейшего доступа
    """

    found_user = await profile.find_by_login(db, request_body.email, request_body.password)
    if not found_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = str(found_user.u_id)
    user_data = {"username": found_user.u_username,
                 "email": found_user.u_email,
                 "phone": found_user.u_phone,
                 "country": found_user.u_country}

    # Создаем токен
    access_token = authentification.create_access_token(data={"sub": str(user_id)})

    # Возвращаем токен в ответе
    return JSONResponse(content={"access_token": access_token, "token_type": "bearer",
                                 "user_id": user_id,
                                 "username": user_data["username"],
                                 "email": user_data["email"],
                                 "phone": user_data["phone"],
                                 "country": user_data["country"]})


@router.patch("")
async def edit_profile(request_body: EditProfileModel, user_id: str = Depends(authentification.get_current_user)):
    """
    Редактирует указанное поле в профиле пользователя, если такое есть
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in request_body.model_dump(exclude_unset=True).items():
        # Проверка существования поля в модели
        if field not in UserInfo.__annotations__:
            raise HTTPException(status_code=422, detail=f"Invalid field: {field}")

        if value is not None:
            await profile.edit(db, user_id, field, value)

    return JSONResponse(content={"message": "Profile edited successfully"})


@router.get("")
async def get_user_data(user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = await profile.get_data(db, user_id)

    return JSONResponse(content=user_data)


@router.delete("")
async def delete_profile(user_id: str = Depends(authentification.get_current_user)):
    """
    Удаляет профиль пользователя
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    await profile.delete(db, user_id)

    return JSONResponse(content={"message": "Profile deleted successfully"})


@router.get("/generate_deck")
async def generate_deck(word: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Генерирует колоду для данного пользователя
    """
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    new_deck = ai.generate_deck_recommendation.generate_deck_recommendation(word)
    deck_id = await decks.add(db, word, user_id, "")
    for k, v in new_deck.items():
        card_id = await cards.add(db, k, v, "", deck_id)
    return JSONResponse(content={"deck_id": deck_id})
