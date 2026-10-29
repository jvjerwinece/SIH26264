"""PostgreSQL access for the Ekasutra API.

One pool, no ORM. Queries return dicts and the view-model is assembled in
app.py. `prepare_threshold=None` keeps psycopg from using named prepared
statements, so the same code works through Supabase's Supavisor pooler.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from psycopg import Connection, OperationalError
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

_pool: ConnectionPool | None = None


def start() -> None:
    """Open the pool if DATABASE_URL is present. Never raises: a service with
    no database still serves the static UI and reports 503 on /health."""
    global _pool
    dsn = os.environ.get("DATABASE_URL", "").strip()
    if not dsn or _pool is not None:
        return
    _pool = ConnectionPool(
        dsn,
        min_size=1,
        max_size=int(os.environ.get("DB_POOL_MAX", "5")),
        timeout=15,
        max_idle=120,
        kwargs={"row_factory": dict_row, "prepare_threshold": None},
        open=False,
        name="ekasutra",
    )
    _pool.open()


def stop() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


def configured() -> bool:
    return _pool is not None


@contextmanager
def connection() -> Iterator[Connection]:
    """Hand out a connection that is known to be alive.

    Supabase's pooler and Render both drop idle sockets. Probing with
    `select 1` before yielding means a write never starts on a dead
    connection: a broken checkout is discarded and retried once.
    """
    if _pool is None:
        raise RuntimeError("DATABASE_URL is not set")
    last: OperationalError | None = None
    for _ in range(2):
        with _pool.connection() as conn:
            try:
                conn.execute("select 1")
            except OperationalError as exc:
                last = exc
                continue
            yield conn
            return
    raise last if last else RuntimeError("no database connection")


def rows(sql: str, params: tuple | dict | None = None) -> list[dict]:
    with connection() as conn:
        return conn.execute(sql, params or ()).fetchall()


def one(sql: str, params: tuple | dict | None = None) -> dict | None:
    with connection() as conn:
        return conn.execute(sql, params or ()).fetchone()
