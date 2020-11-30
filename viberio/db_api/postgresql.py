import asyncpg
import asyncio

from asyncpg import UniqueViolationError
from asyncpg.protocol.protocol import Record

from viberio.data import config


class Database:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.COUNT_USERS = "SELECT COUNT(*) FROM postgres.public.users"
        self.pool: asyncpg.pool.Pool = loop.run_until_complete(
            asyncpg.create_pool(
                user=config.PGUSER,
                password=config.PGPASSWORD,
                host=config.ip
            )
        )

    async def get_user_data(self, user_id: int):
        sql = "SELECT * FROM USERS WHERE id = $1"
        return await self.pool.fetchrow(sql, user_id)

    async def count_users(self):
        record: Record = await self.pool.fetchval(self.COUNT_USERS)
        return record

    # Аналитика по посылкам

    # async def get_users_count(self):
    #     sql = "SELECT COUNT(*) FROM postgres.public.users"
    #     return self.pool(sql)

    @staticmethod
    async def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters, start=1)
        ])
        return sql, tuple(parameters.values())

    # Статистика по посылкам
    async def add_parcels_created(self, id: int):
        sql = "UPDATE Users SET PARCELS_CREATED=PARCELS_CREATED+1 WHERE id=$1"

        await self.pool.execute(sql, id)

    async def add_parcels_sent(self, id: int):
        sql = "UPDATE Users SET PARCELS_SENT=PARCELS_SENT+1 WHERE id=$1"

        await self.pool.execute(sql, id)

    async def add_parcels_received(self, id: int):
        sql = "UPDATE USERS SET PARCELS_RECEIVED=PARCELS_RECEIVED+1 WHERE id=$1"

        await self.pool.fetchval(sql, id)

    # Новое
    async def add_door_not_opened(self, id: int):
        sql = "UPDATE USERS SET DOOR_NOT_OPENED=DOOR_NOT_OPENED+1 WHERE id=$1"

        await self.pool.execute(sql, id)

    async def get_users_json(self, id: int):
        sql = "SELECT data_info FROM USERS WHERE id=$1"

        return await self.pool.fetchval(sql, id)

    #     "SELECT SUM(postgres.public.users.parcels_sent) FROM users;
    # SELECT SUM(postgres.public.users.parcels_received) FROM users;
    # SELECT SUM(postgres.public.users.parcels_created) FROM users;
    # SELECT SUM(postgres.public.users.door_not_opened) FROM users;"
    # async def add_data_info(self, id: int, data:dict):
    #     sql = "UPDATE USERS SET data_info=$2 WHERE id=$1"
    async def get_parcels_sent(self):
        sql = "SELECT SUM(parcels_sent) FROM users"

        return await self.pool.fetchval(sql)

    async def get_parcels_received(self):
        sql = "SELECT SUM(parcels_received) FROM users"

        return await self.pool.fetchval(sql)

    async def get_parcels_created(self):
        sql = "SELECT SUM(parcels_created) FROM users"

        return await self.pool.fetchval(sql)

    async def get_door_not_opened(self):
        sql = "SELECT SUM(door_not_opened) FROM users"

        return await self.pool.fetchval(sql)

    async def add_poshtomat_event_info(self):
        sql = "INSERT INTO Users SUM(door_not_opened) FROM users"

        await self.pool.fetchval(sql)

    async def update_data_info(self, id: int, new_data):
        sql = "UPDATE USERS SET data_info=$2 WHERE id=$1"

        await self.pool.fetchval(sql, id, new_data)

    async def add_user(self, id: int, full_name: str, phone_number: str, time_date: str):
        sql = "INSERT INTO Users (id, full_name, phone_number, time_date) VALUES ($1, $2, $3, $4)"

        await self.pool.execute(sql, id, full_name, phone_number, time_date)

    async def add_viber_user(self, id: str, full_name: str, country: str, language: str, api_version: int):
        sql = "INSERT INTO viber_users (user_id, name,country,language,api_version) VALUES ($1, $2,$3,$4,$5)"

        await self.pool.execute(sql, id, full_name, country, language, api_version)

    async def save_user_token(self, user_id: int, token: str):
        sql = "UPDATE Users SET parcel_list_token = $2 WHERE id = $1"

        await self.pool.execute(sql, user_id, token)

    async def user_exist(self, user_id):
        sql = "SELECT id FROM Users WHERE id = user_id"

        return await self.pool.fetchrow(self, user_id)


db = Database(loop=asyncio.get_event_loop())

#
#
# async def select_user(self, **kwargs):
#     sql = "SELECT * FROM Users WHERE"
#     sql, parameters = self.format_args(sql, kwargs)
#     print(sql)
#     return await self.pool.fetchrow(sql, *parameters)
#
#
# async def count_users(self):
#     return await self.pool.fetchval("SELECT COUNT(*) FROM Users")
#
#
# async def update_user_phone(self, phone, id):
#     sql = "UPDATE Users SET phone = $1 WHERE id = $2"
#     return await self.pool.execute(sql, phone, id)
#
#
# async def delete_users(self):
#     await self.pool.execute("DELETE FROM Users WHERE True")
