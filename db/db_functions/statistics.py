import uuid
from sqlalchemy import text

from db.database import *

from loguru import logger


async def update(db, user_id, words_learned, decks_learned_fully, decks_learned_partly):
    game_id = uuid.uuid4()
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    query = text("""INSERT INTO games (a_id, a_user, a_date, a_words, a_decks_full, a_decks_part) 
    VALUES (:game_id, :user_id, :today, :words, :decks_full, :decks_part);""")

    await db.execute(query,
                     {'game_id': game_id, 'user_id': user_id, 'today': today, 'words': words_learned,
                      'decks_full': decks_learned_fully,
                      'decks_part': decks_learned_partly})


async def calculate_daily(db, user_id):
    query = text("""
        SELECT 
            SUM(a_words) AS total_words_day,
            SUM(a_decks_full) AS total_decks_full_day,
            SUM(a_decks_part) AS total_decks_part_day,
            COUNT(*) AS total_games_day
        FROM games
        WHERE a_date = CURRENT_DATE AND a_user = :user_id;
    """)
    result = await db.execute(query, {'user_id': user_id})
    return list(result.fetchone())


async def calculate_weekly(db, user_id):
    query = text("""
        SELECT 
            SUM(a_words) AS total_words_day,
            SUM(a_decks_full) AS total_decks_full_day,
            SUM(a_decks_part) AS total_decks_part_day,
            COUNT(*) AS total_games_day
        FROM games
        WHERE CURRENT_DATE - INTERVAL '7 days' <= a_date AND a_date <= CURRENT_DATE AND a_user = :user_id;
    """)
    result = await db.execute(query, {'user_id': user_id})
    return list(result.fetchone())


async def calculate_alltime(db, user_id):
    query = text("""
        SELECT 
            SUM(a_words) AS total_words_day,
            SUM(a_decks_full) AS total_decks_full_day,
            SUM(a_decks_part) AS total_decks_part_day,
            COUNT(*) AS total_games_day
        FROM games
        WHERE a_user = :user_id;
    """)
    result = await db.execute(query, {'user_id': user_id})
    return list(result.fetchone())
