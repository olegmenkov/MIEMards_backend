from fastapi import HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse

from db.db_functions import statistics, rankings
from db.db_class import Database
from database_config import HOST, PORT, USERNAME, PASSWORD, DATABASE

import authentification
from schemas import *


db = Database(HOST, PORT, USERNAME, PASSWORD, DATABASE)
router = APIRouter()


def find_rank(top, user_id):
    ranking = None
    for place_from_0 in range(len(top)):
        if top[place_from_0]['user_id'] == user_id:
            ranking = place_from_0 + 1
    return ranking


@router.post("")
async def new_game_results(request_body: GameResults, user_id: str = Depends(authentification.get_current_user)):
    """
    Принимает результаты очередной игры и обновляет таблицу достижений пользователя
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    await statistics.update(db, user_id, request_body.words_learned, request_body.decks_learned_fully,
                            request_body.decks_learned_partly)

    return JSONResponse(content={"message": "Updated user's achievements successfully"})


@router.get("/for_today")
async def statistics_for_today(user_id: str = Depends(authentification.get_current_user)):
    """
    Считает и отправляет статистику успехов пользователя за сегодня.
    Если ranking = None, то он ещё не сыграл ни одной игры сегодня
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    stats = await statistics.calculate_daily(db, user_id)
    total_words, fully_learned_decks, partly_learned_decks, games = [param if param else 0 for param in stats]

    top_today = await rankings.calculate_daily(db)
    ranking = find_rank(top_today, user_id) if top_today else None

    return JSONResponse(
        content={"total_words": int(total_words), "ranking": ranking, "fully_learned_decks": int(fully_learned_decks),
                 "partly_learned_decks": int(partly_learned_decks), "games": games})


@router.get("/for_week")
async def statistics_for_week(user_id: str = Depends(authentification.get_current_user)):
    """
    Считает и отправляет статистику успехов пользователя за неделю.
    Если ranking = None, то он ещё не сыграл ни одной игры за последнюю неделю
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    stats = await statistics.calculate_weekly(db, user_id)
    total_words, fully_learned_decks, partly_learned_decks, games = [param if param else 0 for param in stats]

    top_week = await rankings.calculate_weekly(db)
    ranking = find_rank(top_week, user_id) if top_week else None

    return JSONResponse(
        content={"total_words": int(total_words), "ranking": ranking, "fully_learned_decks": int(fully_learned_decks),
                 "partly_learned_decks": int(partly_learned_decks), "games": games})


@router.get("/for_alltime")
async def statistics_for_alltime(user_id: str = Depends(authentification.get_current_user)):
    """
    Считает и отправляет статистику успехов пользователя за всё время
    Если ranking = None, то он ещё не сыграл ни одной игры
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    stats = await statistics.calculate_alltime(db, user_id)
    total_words, fully_learned_decks, partly_learned_decks, games = [param if param else 0 for param in stats]

    top_alltime = await rankings.calculate_alltime(db)
    ranking = find_rank(top_alltime, user_id) if top_alltime else None

    return JSONResponse(
        content={"total_words": int(total_words), "ranking": ranking, "fully_learned_decks": int(fully_learned_decks),
                 "partly_learned_decks": int(partly_learned_decks), "games": games})
