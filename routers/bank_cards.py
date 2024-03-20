from fastapi import HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse

from db.db_functions import bank_cards
from db.db_class import Database
from database_config import HOST, PORT, USERNAME, PASSWORD, DATABASE

import authentification
from schemas import *


db = Database(HOST, PORT, USERNAME, PASSWORD, DATABASE)
router = APIRouter()


@router.post("")
async def create_bank_card(request_body: BankCardData, user_id: str = Depends(authentification.get_current_user)):
    """
    Создаёт новую карту
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    # Вызываем функцию для добавления колоды в базу данных
    bank_card_id = await bank_cards.add(db, user_id, request_body.number, request_body.exp_date, request_body.cvv)
    return JSONResponse(content={"bank_card_id": bank_card_id})


@router.get("/get_bank_card_by_id")
async def get_bank_card(bank_card_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает карту по айди. Из соображений безопасности -- только последние 4 цифры номера
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    bank_card_info = await bank_cards.get(db, bank_card_id)
    return JSONResponse(content=bank_card_info)


@router.patch("")
async def edit_bank_card(request_body: BankCardData, bank_card_id: str,
                         user_id: str = Depends(authentification.get_current_user)):
    """
    Редактирует карту
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in request_body.model_dump(exclude_unset=True).items():
        # Проверка существования поля в модели
        if field not in BankCardData.__annotations__:
            raise HTTPException(status_code=422, detail=f"Invalid field: {field}")

        if value is not None:
            await bank_cards.edit(db, bank_card_id, field, value)
    return JSONResponse(content={"message": "bank card edited successfully"})


@router.delete("")
async def delete_bank_card(bank_card_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Удаляет карту
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    await bank_cards.delete(db, bank_card_id)

    return JSONResponse(content={"message": "bank_card deleted successfully"})


@router.get("/show_bank_cards_of_user")
async def get_bank_cards(user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает все карты данного пользователя. Из соображений безопасности -- только последние 4 цифры номера
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    users_bank_cards = await bank_cards.get_all(db, user_id)

    return JSONResponse(content=users_bank_cards)
