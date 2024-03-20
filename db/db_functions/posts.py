import uuid

from fastapi import HTTPException
from sqlalchemy import text

from loguru import logger


async def add(db, user_id, text_):
    post_id = uuid.uuid4()
    query = text("""INSERT INTO posts (p_id, p_author_id, p_text) VALUES (:id, :author, :text)""")
    await db.execute(query,
                     {'id': post_id,
                      'author': user_id,
                      'text': text_})
    return str(post_id)


async def edit(db, post_id, field_to_change, new_value):
    query = text("""UPDATE posts SET """ + 'p_' + field_to_change + """= :new_value WHERE p_id = :post_id""")
    await db.execute(query, {'new_value': new_value, 'post_id': post_id})


async def delete(db, post_id):
    query = text("""DELETE FROM posts WHERE p_id = :post_id""")
    await db.execute(query, {'post_id': post_id})


async def get(db, post_id):
    query = text("""SELECT p_text FROM posts where p_id = :post_id""")
    result = await db.execute(query, {'post_id': post_id})
    res = result.fetchone()
    if res:
        text_ = res[0]
        return {"text": text_}
    else:
        raise HTTPException(status_code=404,
                            detail='This post is not found')


async def get_all(db, user_id):
    query = text("""SELECT p_id, p_text FROM posts WHERE p_author_id = :user_id;""")
    result = await db.execute(query, {'user_id': user_id})
    posts = {}

    for row in result:
        post_id, text_ = row
        posts[str(post_id)] = {"text": text_}

    return posts
