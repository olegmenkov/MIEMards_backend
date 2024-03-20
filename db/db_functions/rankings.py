
from sqlalchemy import text
from db.db_functions import profile

from loguru import logger


async def set_rating(db, query):
    result = await db.execute(query)

    rating = []
    for row in result:
        user_id, username, words_learned = row
        data = await profile.get_data(db, user_id)
        country = data["country"]
        rating.append(
            {'user_id': str(user_id), 'username': username, 'country': country, 'words_learned': int(words_learned)})

    return rating


async def calculate_daily(db):
    query = text("""
        SELECT g.a_user as user_id, u.u_username AS user_name, SUM(g.a_words) AS total_words
        FROM games g
        JOIN users u ON g.a_user = u.u_id
        WHERE g.a_date = CURRENT_DATE
        GROUP BY u.u_username, g.a_user
        ORDER BY total_words DESC;
    """)

    rating = await set_rating(db, query)

    return rating


async def calculate_weekly(db):
    query = text("""
        SELECT g.a_user as user_id, u.u_username AS user_name, SUM(g.a_words) AS total_words
        FROM games g
        JOIN users u ON g.a_user = u.u_id
        WHERE CURRENT_DATE - INTERVAL '7 days' <= g.a_date AND g.a_date <= CURRENT_DATE
        GROUP BY u.u_username, g.a_user
        ORDER BY total_words DESC;
    """)

    rating = await set_rating(db, query)

    return rating


async def calculate_alltime(db):
    query = text("""
        SELECT g.a_user as user_id, u.u_username AS user_name, SUM(g.a_words) AS total_words
        FROM games g
        JOIN users u ON g.a_user = u.u_id
        GROUP BY u.u_username, g.a_user
        ORDER BY total_words DESC;
    """)

    rating = await set_rating(db, query)

    return rating
