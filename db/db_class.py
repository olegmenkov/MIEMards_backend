from sqlalchemy.ext.asyncio import create_async_engine


class Database:
    """
    Класс с асинхронным подключением к базе данных.
    При инициализации принимает параметры для подключения.
    """

    def __init__(self, host, port, user, password, database):
        self._database_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
        self._engine = create_async_engine(self._database_url, echo=True)

    async def execute(self, query, *args, **kwargs):
        async with self._engine.begin() as conn:
            result = await conn.execute(query, *args, **kwargs)
            return result

    async def close(self):
        await self._engine.dispose()
