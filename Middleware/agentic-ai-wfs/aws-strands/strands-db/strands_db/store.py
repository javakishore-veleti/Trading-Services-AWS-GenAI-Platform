import json
import os
import re
import uuid
from enum import Enum
from typing import Any

import psycopg
from psycopg.types.json import Json
from strands.memory import MemoryManager
from strands.memory.types import MemoryEntry, SearchOptions
from strands.session.repository_session_manager import RepositorySessionManager
from strands.session.session_repository import SessionRepository
from strands.types.exceptions import SessionException
from strands.types.session import Session, SessionAgent, SessionMessage

SCHEMA = "strands"


def _connect() -> psycopg.Connection:
    return psycopg.connect(
        host=os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
        dbname=os.environ.get("POSTGRES_DB", "postgres"),
        autocommit=True,
    )


def _dump(value: Any) -> Json:
    return Json(json.loads(json.dumps(value, default=lambda item: item.value if isinstance(item, Enum) else str(item))))


def ensure_schema() -> None:
    with _connect() as connection:
        connection.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {SCHEMA}.sessions (
                session_id text PRIMARY KEY,
                body jsonb NOT NULL
            )
            """
        )
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {SCHEMA}.agents (
                session_id text NOT NULL,
                agent_id text NOT NULL,
                body jsonb NOT NULL,
                PRIMARY KEY (session_id, agent_id)
            )
            """
        )
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {SCHEMA}.messages (
                session_id text NOT NULL,
                agent_id text NOT NULL,
                message_id integer NOT NULL,
                body jsonb NOT NULL,
                PRIMARY KEY (session_id, agent_id, message_id)
            )
            """
        )
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {SCHEMA}.memories (
                id text PRIMARY KEY,
                content text NOT NULL,
                metadata jsonb NOT NULL DEFAULT '{{}}'::jsonb,
                created_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )


class PostgresSessionRepository(SessionRepository):
    """Short-term memory. One row per message in the current conversation."""

    def create_session(self, session: Session, **kwargs: Any) -> Session:
        with _connect() as connection:
            connection.execute(
                f"""
                INSERT INTO {SCHEMA}.sessions (session_id, body)
                VALUES (%s, %s)
                ON CONFLICT (session_id) DO UPDATE SET body = EXCLUDED.body
                """,
                (session.session_id, _dump(session.to_dict())),
            )
        return session

    def read_session(self, session_id: str, **kwargs: Any) -> Session | None:
        with _connect() as connection:
            row = connection.execute(
                f"SELECT body FROM {SCHEMA}.sessions WHERE session_id = %s",
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        return Session.from_dict(row[0])

    def create_agent(self, session_id: str, session_agent: SessionAgent, **kwargs: Any) -> None:
        with _connect() as connection:
            connection.execute(
                f"""
                INSERT INTO {SCHEMA}.agents (session_id, agent_id, body)
                VALUES (%s, %s, %s)
                ON CONFLICT (session_id, agent_id) DO UPDATE SET body = EXCLUDED.body
                """,
                (session_id, session_agent.agent_id, _dump(session_agent.to_dict())),
            )

    def read_agent(self, session_id: str, agent_id: str, **kwargs: Any) -> SessionAgent | None:
        with _connect() as connection:
            row = connection.execute(
                f"SELECT body FROM {SCHEMA}.agents WHERE session_id = %s AND agent_id = %s",
                (session_id, agent_id),
            ).fetchone()
        if row is None:
            return None
        return SessionAgent.from_dict(row[0])

    def update_agent(self, session_id: str, session_agent: SessionAgent, **kwargs: Any) -> None:
        previous = self.read_agent(session_id, session_agent.agent_id)
        if previous is None:
            raise SessionException(f"Agent {session_agent.agent_id} in session {session_id} does not exist")
        session_agent.created_at = previous.created_at
        self.create_agent(session_id, session_agent)

    def create_message(self, session_id: str, agent_id: str, session_message: SessionMessage, **kwargs: Any) -> None:
        with _connect() as connection:
            connection.execute(
                f"""
                INSERT INTO {SCHEMA}.messages (session_id, agent_id, message_id, body)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (session_id, agent_id, message_id) DO UPDATE SET body = EXCLUDED.body
                """,
                (session_id, agent_id, session_message.message_id, _dump(session_message.to_dict())),
            )

    def read_message(self, session_id: str, agent_id: str, message_id: int, **kwargs: Any) -> SessionMessage | None:
        with _connect() as connection:
            row = connection.execute(
                f"""
                SELECT body FROM {SCHEMA}.messages
                WHERE session_id = %s AND agent_id = %s AND message_id = %s
                """,
                (session_id, agent_id, message_id),
            ).fetchone()
        if row is None:
            return None
        return SessionMessage.from_dict(row[0])

    def update_message(self, session_id: str, agent_id: str, session_message: SessionMessage, **kwargs: Any) -> None:
        previous = self.read_message(session_id, agent_id, session_message.message_id)
        if previous is None:
            raise SessionException(f"Message {session_message.message_id} does not exist")
        session_message.created_at = previous.created_at
        self.create_message(session_id, agent_id, session_message)

    def list_messages(
        self, session_id: str, agent_id: str, limit: int | None = None, offset: int = 0, **kwargs: Any
    ) -> list[SessionMessage]:
        sql = f"""
            SELECT body FROM {SCHEMA}.messages
            WHERE session_id = %s AND agent_id = %s
            ORDER BY message_id
            OFFSET %s
        """
        params: list[Any] = [session_id, agent_id, offset]
        if limit is not None:
            sql += " LIMIT %s"
            params.append(limit)
        with _connect() as connection:
            rows = connection.execute(sql, params).fetchall()
        return [SessionMessage.from_dict(row[0]) for row in rows]


def _tokens(text: str) -> set[str]:
    return {token for token in re.split(r"\W+", text.lower()) if token}


class PostgresMemoryStore:
    """Long-term memory. Facts survive after a conversation ends."""

    def __init__(self) -> None:
        self.name = "facts"
        self.description = "Facts saved from earlier conversations."
        self.max_search_results = 5
        self.writable = True
        self.extraction = False

    async def add(self, content: str, metadata: dict[str, Any] | None = None) -> dict[str, str]:
        memory_id = str(uuid.uuid4())
        with _connect() as connection:
            connection.execute(
                f"INSERT INTO {SCHEMA}.memories (id, content, metadata) VALUES (%s, %s, %s)",
                (memory_id, content, _dump(metadata or {})),
            )
        return {"id": memory_id}

    async def search(self, query: str, options: SearchOptions | None = None) -> list[MemoryEntry]:
        limit = self.max_search_results
        if options and options.get("max_search_results"):
            limit = int(options["max_search_results"])
        with _connect() as connection:
            rows = connection.execute(
                f"SELECT content, metadata FROM {SCHEMA}.memories ORDER BY created_at DESC LIMIT 500"
            ).fetchall()
        query_tokens = _tokens(query)
        ranked = []
        for content, metadata in rows:
            score = len(query_tokens & _tokens(content)) if query_tokens else 0
            if query_tokens and score == 0:
                continue
            ranked.append((score, MemoryEntry(content=content, metadata=metadata)))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [entry for _score, entry in ranked[:limit]]


def memory_manager() -> MemoryManager:
    return MemoryManager(stores=[PostgresMemoryStore()], add_tool_config=True)


def session_manager(session_id: str) -> RepositorySessionManager:
    return RepositorySessionManager(session_id=session_id, session_repository=PostgresSessionRepository())
