from fastapi import HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse

import db.db_functions as db_functions
from db.db_class import Database
from database_config import HOST, PORT, USERNAME, PASSWORD, DATABASE

import authentification
from schemas import *

import ai
from ai.generate_card_recommendation import generate_card_recommendation


db = Database(HOST, PORT, USERNAME, PASSWORD, DATABASE)
router = APIRouter()


@router.post("")
async def create_deck(deck_data: DeckData, user_id: str = Depends(authentification.get_current_user)):
    """
    Создаёт новую колоду, принадлежащую данному пользователю
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    # Вызываем функцию для добавления колоды в базу данных
    deck_id = await db_functions.add_deck(db, deck_data.name, user_id, deck_data.description)

    return JSONResponse(content={"deck_id": deck_id})


@router.get("/get_deck_by_id")
async def get_deck(deck_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает информацию о колоде по её ID в следующем формате:
    {"creator": "userId", "name": "deckName", "description": "deckDescription"}
    """
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    deck_info = await db_functions.get_deck_by_id(db, deck_id)
    return JSONResponse(content=deck_info)


@router.patch("")
async def edit_deck(request_body: DeckData, deck_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Редактирует указанное поле для колоды, если такое есть
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in request_body.model_dump(exclude_unset=True).items():
        # Проверка существования поля в модели
        if field not in DeckData.__annotations__:
            raise HTTPException(status_code=422, detail=f"Invalid field: {field}")

        if value is not None:
            await db_functions.edit_deck_in_db(db, deck_id, field, value)

    return JSONResponse(content={"message": "Deck edited successfully"})


# Эндпоинт для удаления колоды
@router.delete("")
async def delete_deck(deck_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Удаляет колоду
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    await db_functions.delete_deck_from_db(db, deck_id)

    return JSONResponse(content={"message": "Deck deleted successfully"})


@router.get("/show_decks_of_user")
async def get_decks(user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает все колоды данного пользователя в таком формате
    {
        "deckId": {
            "creator": "userId", "name": "deckName", "description": "deckDescription"
        },
        "deckId2": {
            "creator": "userId", "name": "deckName2", "description": "deckDescription2"
        },
        ...
     }
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    users_decks = await db_functions.get_users_decks(db, user_id)

    return JSONResponse(content=users_decks)


@router.get("/generate_card")
async def generate_card(deck_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Генерирует карточку для данной колоды
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    ai.generate_card_recommendation.generate_card_recommendation(deck_id)

    return JSONResponse(content={'message': 'Success!'})

