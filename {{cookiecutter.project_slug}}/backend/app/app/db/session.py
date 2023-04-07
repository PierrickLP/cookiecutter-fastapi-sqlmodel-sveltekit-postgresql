import logging
import time
from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncIterator, Iterator, Mapping

from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import Session as _Session
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncSession as _AsyncSession

from app.core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI), pool_pre_ping=True)


@contextmanager
def Session() -> Iterator[_Session]:
    session = _Session(engine, autoflush=False)
    try:
        yield session
    finally:
        session.close()


engine_async = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI_ASYNC), pool_pre_ping=True
)


@asynccontextmanager
async def AsyncSession() -> AsyncIterator[_AsyncSession]:
    session = _AsyncSession(engine_async, autoflush=False, expire_on_commit=False)
    try:
        yield session
    finally:
        await session.close()


if settings.PROFILE_QUERY_MODE:
    logging.basicConfig()
    logger = logging.getLogger("myapp.sqltime")
    logger.setLevel(logging.DEBUG)

    def before_cursor_execute(
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Mapping[Any, Any] | None,
        context: Any | None,
        executemany: bool,
    ) -> None:
        conn.info.setdefault("query_start_time", []).append(time.time())
        logger.debug("Start Query: %s" % statement)

    def after_cursor_execute(
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Mapping[Any, Any] | None,
        context: Any | None,
        executemany: bool,
    ) -> None:
        total = time.time() - conn.info["query_start_time"].pop(-1)
        logger.debug("Query Complete!")
        logger.debug("Total Time: %f" % total)

    event.listen(
        engine_async.sync_engine, "before_cursor_execute", before_cursor_execute
    )
    event.listen(engine_async.sync_engine, "after_cursor_execute", after_cursor_execute)
