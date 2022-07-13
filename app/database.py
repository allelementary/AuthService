import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional, Tuple, List, Any, Dict, cast
import logging
import re
from functools import lru_cache
import asyncpg
from orjson import loads, dumps

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@' \
                          f'{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

SQL_URL = f'postgresql://{settings.database_username}:{settings.database_password}@' \
                          f'{settings.database_hostname}:{settings.database_port}/'


_pool: Optional[asyncpg.pool.Pool] = None
_ph_catcher = re.compile('\\{(\\w+)\\}')

AUTH_SCHEMA = 'auth_service'

# region sqla settings
meta_data = MetaData(schema=AUTH_SCHEMA)
# Base = declarative_base(metadata=meta_data)
__db_session = None

engine = create_engine(SQLALCHEMY_DATABASE_URL)
#
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
Base = declarative_base()


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# def get_session():
#     # from config.conf import config
#     global __db_session
#
#     if not __db_session:
#         print('created app connection to db with dsn ', SQLALCHEMY_DATABASE_URL)
#         engine = create_engine(SQLALCHEMY_DATABASE_URL)
#         __db_session = sessionmaker(bind=engine)()
#
#     return __db_session


# endregion

def get_schema_table(cls):
    return f"{cls.__table__.schema}.{cls.__tablename__}"


Base.get_schema_table = classmethod(
    lru_cache(maxsize=None)(get_schema_table))


async def _connection_init(conn: asyncpg.Connection):
    # hstore <-> dict
    await conn.set_builtin_type_codec('hstore', codec_name='pg_contrib.hstore')
    # json <-> dict
    await conn.set_type_codec('json', encoder=dumps, decoder=loads, schema='pg_catalog')
    await conn.set_type_codec('jsonb', encoder=dumps, decoder=loads, schema='pg_catalog')


async def connect(loop: asyncio.AbstractEventLoop = None, db_dsn: str = None) -> Optional[asyncpg.pool.Pool]:
    """Get DB connection pool. Intended for manual use:
        ```
        conn = await connect()
        ...
        await close()
        ```
    """
    # from config.conf import config
    global _pool

    if not _pool:
        params = dict(
            dsn=db_dsn,
            timeout=settings.DB_TIMEOUT, command_timeout=2 * settings.DB_TIMEOUT,
            min_size=settings.POOL_MIN_SIZE, max_size=settings.POOL_MAX_SIZE,
            max_queries=settings.POOL_QUERIES,
            max_inactive_connection_lifetime=settings.POOL_LIFETIME
        )
        logging.debug('Creating DB pool with params: %s', params)
        _pool = await asyncpg.create_pool(
            init=_connection_init, loop=loop,
            **params)

    return _pool


async def close():
    """Close connection pool"""
    global _pool

    if not _pool:
        return

    await _pool.close()
    _pool = None


@asynccontextmanager
async def get_connection(loop: asyncio.AbstractEventLoop = None) \
        -> AsyncIterator[asyncpg.Connection]:
    """Get DB connection using context manager. For use in `with` statements:
        ```
        async with get_connection() as conn:
            ...
        ```
    """
    conn: Optional[asyncpg.Connection] = None

    try:
        _pool = await connect(loop=loop, db_dsn=SQLALCHEMY_DATABASE_URL)
        conn = await _pool.acquire()
        yield cast(asyncpg.Connection, conn)
    finally:
        if conn:
            await _pool.release(conn)


def translate_placeholders(query: str, params: Dict[str, Any]) -> Tuple[str, List[Any]]:
    """
    This is a simple translator designed to allow usage of queries like
    `SELECT a, b, c FROM table WHERE d = {d} AND e = {e}` with parameters in
    form of `{'d': 1, 'e': 2}`.

    It converts query to native PostgreSQL placeholder syntax
    `SELECT a, b, c FROM table WHERE d = $1 AND e = $2` and parameters to `[1, 2]`
    preserving arguments order and filtering out unused parameter values.

    :param query: str query
    :param params: dict params

    :return: tuple (translated query, [id])
    """
    mapping = {}
    values = []
    used_keys = list(m.group(1) for m in _ph_catcher.finditer(query))

    logging.log(logging.DEBUG - 5, 'Translating query: %s', query)
    logging.log(logging.DEBUG - 5, 'With params: %r', params)

    for k in params:
        if k not in used_keys:
            continue
        values.append(params[k])
        mapping[k] = f'${len(values)}'

    logging.log(logging.DEBUG - 5, 'Built mapping: %s', mapping)

    query = query.format_map(mapping)
    logging.debug('Query translated: %s', query)
    logging.debug('Query params translated: %r', values)

    return query, values


# def get_model(model_name):
#     """
#     :param model_name: String case sensitive model name
#     :return :class of registered models or None
#     """
#     import cms.models.all  # pylint: disable=unused-import
#     from cms.models.tags import Base as TagBase
#
#     return (
#             Base._decl_class_registry.get(model_name)
#             or TagBase._decl_class_registry.get(model_name)
#     )


def drop_db(root_pg_dsn: str, db_name: str):
    _engine = create_engine(root_pg_dsn, isolation_level='AUTOCOMMIT')
    _session = sessionmaker(bind=_engine)()

    # text = f'''
    #     SELECT pg_terminate_backend(pg_stat_activity.pid)
    #     FROM pg_stat_activity
    #     WHERE pg_stat_activity.datname = '{db_name}'
    #     AND pid <> pg_backend_pid();
    #     '''
    # _session.execute(text)

    _session.execute(f'DROP DATABASE IF EXISTS {db_name}')
    result = _session.execute(f'''
        SELECT datname 
        FROM pg_catalog.pg_database 
        WHERE lower(datname) = lower('{db_name}');
    ''')

    if result.fetchone():
        raise ValueError('Database was not properly deleted')

    _engine.dispose()
    print(f'Database {db_name} dropped')


def create_db(root_pg_dsn: str, db_name: str):
    _engine = create_engine(root_pg_dsn, isolation_level='AUTOCOMMIT')
    _session = sessionmaker(bind=_engine)()

    _session.execute(f'CREATE DATABASE {db_name} ;')
    result = _session.execute(f'''
        SELECT datname 
        FROM pg_catalog.pg_database 
        WHERE lower(datname) = lower('{db_name}');
    ''')
    if not result.fetchone():
        raise ValueError('Database was not properly created')

    _engine.dispose()


def finish_database_preparation(pg_dsn: str):
    _engine = create_engine(pg_dsn, isolation_level='AUTOCOMMIT')
    _session = sessionmaker(bind=_engine)()

    _session.execute('CREATE SCHEMA IF NOT EXISTS auth_service')

    print(f'Database {pg_dsn} created')