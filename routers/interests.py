from fastapi import HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse

from db.db_functions import interests
from db.db_class import Database
from database_config import HOST, PORT, USERNAME, PASSWORD, DATABASE

import authentification
from schemas import *


db = Database(HOST, PORT, USERNAME, PASSWORD, DATABASE)
router = APIRouter()


@router.post("")
async def create_interest(request_body: InterestData, user_id: str = Depends(authentification.get_current_user)):
    """
    Создаёт новый интерес
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    # Вызываем функцию для добавления колоды в базу данных
    interest_id = await interests.add(db, user_id, request_body.name, request_body.description)

    return JSONResponse(content={"interest_id": interest_id})


@router.get("/get_interest_by_id")
async def get_interest(interest_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает интерес по айди
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    interest_info = await interests.get(db, interest_id)
    return JSONResponse(content=interest_info)


@router.patch("")
async def edit_interest(request_body: InterestData, interest_id: str,
                        user_id: str = Depends(authentification.get_current_user)):
    """
    Меняет интерес
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in request_body.model_dump(exclude_unset=True).items():
        # Проверка существования поля в модели
        if field not in InterestData.__annotations__:
            raise HTTPException(status_code=422, detail=f"Invalid field: {field}")

        if value is not None:
            await interests.edit(db, interest_id, field, value)
    return JSONResponse(content={"message": "Interest edited successfully"})


@router.delete("")
async def delete_interest(interest_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Удаляет интерес
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    await interests.delete(db, interest_id)

    return JSONResponse(content={"message": "Interest deleted successfully"})


@router.get("/show_interests_of_user")
async def get_interests(user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает все интересы данного пользователя
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    users_interests = await interests.get_all(db, user_id)

    return JSONResponse(content=users_interests)
