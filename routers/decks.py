from fastapi import HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse

from db.db_functions import decks, cards
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
    deck_id = await decks.add(db, deck_data.name, user_id, deck_data.description)

    return JSONResponse(content={"deck_id": deck_id})


@router.get("/get_deck_by_id")
async def get_deck(deck_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает информацию о колоде по её ID в следующем формате:
    {"creator": "userId", "name": "deckName", "description": "deckDescription"}
    """
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    deck_info = await decks.get(db, deck_id)
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
            await decks.edit(db, deck_id, field, value)

    return JSONResponse(content={"message": "Deck edited successfully"})


@router.delete("")
async def delete_deck(deck_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Удаляет колоду
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    await decks.delete(db, deck_id)

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

    users_decks = await decks.get_all(db, user_id)

    return JSONResponse(content=users_decks)


@router.get("/generate_card")
async def generate_card(deck_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Генерирует карточку для данной колоды
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    # mock
    return JSONResponse(content={'card_id': "123"})

    all_cards = await cards.get_all(db, deck_id)
    deck_words = [element['english_word'] for element in all_cards]
    eng, ru = ai.generate_card_recommendation.generate_card_recommendation(deck_words)
    card_id = await cards.add(db, eng, ru, "", deck_id)
    return JSONResponse(content={'card_id': card_id})
