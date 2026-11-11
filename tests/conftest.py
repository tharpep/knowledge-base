"""Shared fakes: no database, no network. Tests patch get_pool and the Voyage/gateway calls."""

import importlib
import os
from typing import ClassVar

for _var in ("API_KEY", "DATABASE_URL", "VOYAGE_API_KEY", "SENTRY_DSN", "API_GATEWAY_KEY"):
    os.environ[_var] = ""

import pytest

from core.config import get_config


class FakeConn:
    """Records every query as (method, sql, args) in `calls`.

    Queue return values per method in `responses`, e.g. conn.responses["fetch"].append([row]).
    Unqueued calls return: fetch [], fetchrow None, fetchval None, execute "OK 0", executemany None.
    """

    _defaults: ClassVar[dict] = {"fetchrow": None, "fetchval": None, "execute": "OK 0", "executemany": None}

    def __init__(self):
        self.calls: list[tuple[str, str, tuple]] = []
        self.responses: dict[str, list] = {m: [] for m in ("fetch", *self._defaults)}

    async def _call(self, method, sql, args):
        self.calls.append((method, sql, args))
        queued = self.responses[method]
        if queued:
            return queued.pop(0)
        return [] if method == "fetch" else self._defaults[method]

    async def fetch(self, sql, *args):
        return await self._call("fetch", sql, args)

    async def fetchrow(self, sql, *args):
        return await self._call("fetchrow", sql, args)

    async def fetchval(self, sql, *args):
        return await self._call("fetchval", sql, args)

    async def execute(self, sql, *args):
        return await self._call("execute", sql, args)

    async def executemany(self, sql, rows):
        return await self._call("executemany", sql, (rows,))

    def transaction(self):
        return _Ctx(None)

    def sql(self, method: str | None = None) -> list[str]:
        return [s for m, s, _ in self.calls if method is None or m == method]


class FakePool:
    """One shared FakeConn behind acquire(); pool-level fetch/execute go to the same conn."""

    def __init__(self):
        self.conn = FakeConn()

    def acquire(self):
        return _Ctx(self.conn)

    async def fetch(self, sql, *args):
        return await self.conn.fetch(sql, *args)

    async def fetchrow(self, sql, *args):
        return await self.conn.fetchrow(sql, *args)

    async def execute(self, sql, *args):
        return await self.conn.execute(sql, *args)


class _Ctx:
    def __init__(self, value):
        self.value = value

    async def __aenter__(self):
        return self.value

    async def __aexit__(self, *exc):
        return False


_POOL_USERS = ("rag.retriever", "rag.pipeline", "app.routes.query", "app.routes.ingest")


@pytest.fixture
def fake_pool(monkeypatch):
    """A FakePool returned by get_pool() in every module that imported it."""
    pool = FakePool()
    for name in _POOL_USERS:
        monkeypatch.setattr(importlib.import_module(name), "get_pool", lambda: pool)
    return pool


@pytest.fixture
def config():
    """The live AppConfig; set fields with monkeypatch.setattr(config, "field", value)."""
    yield get_config()
    get_config.cache_clear()
