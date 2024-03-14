from fastapi import HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse

import db.db_functions as db_functions
from db.db_class import Database
from database_config import HOST, PORT, USERNAME, PASSWORD, DATABASE

import authentification
from schemas import *


db = Database(HOST, PORT, USERNAME, PASSWORD, DATABASE)
router = APIRouter()


@router.get("/for_today")
async def rankings_today(user_id: str = Depends(authentification.get_current_user)):
    """
    Считает и отправляет топ пользователей за сегодня
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    top_all_today = await db_functions.calculate_daily_rating(db)

    return JSONResponse(content=top_all_today)


@router.get("/for_week")
async def rankings_week(user_id: str = Depends(authentification.get_current_user)):
    """
    Считает и отправляет топ пользователей за неделю
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    top_all_week = await db_functions.calculate_weekly_rating(db)

    return JSONResponse(content=top_all_week)


@router.get("/for_alltime")
async def rankings_week(user_id: str = Depends(authentification.get_current_user)):
    """
    Считает и отправляет топ пользователей за всё время
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    top_all_total = await db_functions.calculate_alltime_rating(db)

    return JSONResponse(content=top_all_total)