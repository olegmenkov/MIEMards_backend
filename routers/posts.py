from fastapi import HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse

from db.db_functions import posts
from db.db_class import Database
from database_config import HOST, PORT, USERNAME, PASSWORD, DATABASE

import authentification
from schemas import *


db = Database(HOST, PORT, USERNAME, PASSWORD, DATABASE)
router = APIRouter()


@router.post("")
async def create_post(request_body: PostData, user_id: str = Depends(authentification.get_current_user)):
    """
    Создаёт новый пост
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    # Вызываем функцию для добавления колоды в базу данных
    post_id = await posts.add(db, user_id, request_body.text)

    return JSONResponse(content={"post_id": post_id})


@router.get("/get_post_by_id")
async def get_post(post_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает пост по айди
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    post_info = await posts.get(db, post_id)
    return JSONResponse(content=post_info)


@router.patch("")
async def edit_post(request_body: PostData, post_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Меняет пост
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in request_body.model_dump(exclude_unset=True).items():
        # Проверка существования поля в модели
        if field not in PostData.__annotations__:
            raise HTTPException(status_code=422, detail=f"Invalid field: {field}")

        if value is not None:
            await posts.edit(db, post_id, field, value)
    return JSONResponse(content={"message": "Post edited successfully"})


@router.delete("")
async def delete_post(post_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Удаляет пост
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    await posts.delete(db, post_id)

    return JSONResponse(content={"message": "post deleted successfully"})


@router.get("/show_posts_of_user")
async def get_posts(user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает все посты данного пользователя
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    users_posts = await posts.get_all(db, user_id)

    return JSONResponse(content=users_posts)
