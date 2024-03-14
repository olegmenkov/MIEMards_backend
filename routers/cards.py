from fastapi import HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse

import db.db_functions as db_functions
from db.db_class import Database
from database_config import HOST, PORT, USERNAME, PASSWORD, DATABASE

import authentification
from schemas import *

import ai
from ai.generate_image import generate_image
from ai.generate_translation import generate_translation


db = Database(HOST, PORT, USERNAME, PASSWORD, DATABASE)
router = APIRouter()


@router.post("")
async def create_card(card_data: CardData, user_id: str = Depends(authentification.get_current_user)):
    """
    Создаёт новую карту в колоде пользователя
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    # Вызываем функцию для добавления карты в базу данных
    card_id = await db_functions.add_card(db, card_data.english_word, card_data.translation, card_data.explanation,
                                          card_data.deck_id)
    return JSONResponse(content={"card_id": card_id})


@router.get("/get_card_by_id")
async def get_card(card_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает информацию по карточке по её ID в следующем формате
    {"english_word": "englishWord", "translation": "translation", "explanation": "explanation",
                            "deck_id": "deckId"}
    """
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    deck_info = await db_functions.get_card_by_id(db, card_id)
    return JSONResponse(content=deck_info)


@router.patch("")
async def edit_card(card_id: str, request_body: CardData, user_id: str = Depends(authentification.get_current_user)):
    """
    Редактирует поле для карточки в колоде, если такое поле есть
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in request_body.model_dump(exclude_unset=True).items():
        # Проверка существования поля в модели
        if field not in CardData.__annotations__ and field != "deck_id":
            raise HTTPException(status_code=422, detail=f"Invalid field: {field}")

        if value is not None:
            await db_functions.edit_card_in_db(db, card_id, field, value)

    return JSONResponse(content={"message": "Card edited successfully"})


@router.delete("")
async def delete_card(card_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Удаляет карточку из колоды пользователя
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    await db_functions.delete_card_from_db(db, card_id)
    return JSONResponse(content={"message": "Card deleted successfully"})


@router.get("/show_cards_from_deck")
async def get_cards(deck_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает все карты в заданной колоде в формате
    {
        "cardId": {
            "deck": "deckId", "english_word": "englishWord", "translation": "translation", "explanation": "explanation"
        },
        "cardId2": {
            "deck": "deckId2", "english_word": "englishWord2", "translation": "translation2", "explanation": "explanation2"
        },
        ...
    }
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    cards = await db_functions.get_decks_cards(db, deck_id)
    return JSONResponse(content=cards)


@router.get("/generate_image")
async def generate_image(card_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Генерирует изображение для данной карточки
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    ai.generate_image.generate_image(card_id)

    return JSONResponse(content={'message': 'Success!'})


@router.get("/generate_translation")
async def generate_translation(card_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Генерирует перевод для данной карточки
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    ai.generate_translation.generate_translation(card_id)

    return JSONResponse(content={'message': 'Success!'})
