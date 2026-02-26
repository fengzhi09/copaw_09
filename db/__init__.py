# -*- coding: utf-8 -*-
"""
PostgreSQL Database Module for cp9

Tables:
- agents: Agent 元数据
- short_term_memory: 短期记忆
- long_term_memory: 长期记忆
- trace_logs: 执行追踪日志
- credit_logs: Credit 消耗记录
- cost_stats: 成本统计
- conversations: 对话历史
- configs: 系统配置
"""

import os
from datetime import datetime
from typing import Optional
from contextlib import contextmanager

from pydantic import BaseModel
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    Text,
    JSON,
    Index,
    ForeignKey,
)
try:
    from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
    # VECTOR需要pgvector扩展，如果失败则跳过
    try:
        from sqlalchemy.dialects.postgresql import VECTOR
    except ImportError:
        VECTOR = None
except ImportError:
    JSONB = None
    TIMESTAMP = None
    VECTOR = None
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Database URL
DATABASE_URL = os.environ.get(
    "COPAW_DATABASE_URL",
    "postgresql://cp9:cp9@localhost:5432/cp9"
)

Base = declarative_base()

engine = None
SessionLocal = None


def get_database_url() -> str:
    """Get database URL from environment or config."""
    return os.environ.get(
        "COPAW_DATABASE_URL",
        "postgresql://cp9:cp9@localhost:5432/cp9"
    )


def init_db(database_url: Optional[str] = None) -> None:
    """Initialize database connection and create tables."""
    global engine, SessionLocal
    
    url = database_url or get_database_url()
    engine = create_engine(
        url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)


def get_session():
    """Get database session."""
    global SessionLocal
    if SessionLocal is None:
        init_db()
    return SessionLocal()


@contextmanager
def session_scope():
    """Provide a transactional scope for database operations."""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ==================== Models ====================

class Agent(Base):
    """Agent 元数据"""
    __tablename__ = "agents"
    
    id = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    short_term_memories = relationship("ShortTermMemory", back_populates="agent")
    long_term_memories = relationship("LongTermMemory", back_populates="agent")
    credit_logs = relationship("CreditLog", back_populates="agent")
    cost_stats = relationship("CostStat", back_populates="agent")
    conversations = relationship("Conversation", back_populates="agent")


class ShortTermMemory(Base):
    """短期记忆"""
    __tablename__ = "short_term_memory"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(10), ForeignKey("agents.id"))
    session_id = Column(String(50))
    content = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    agent = relationship("Agent", back_populates="short_term_memories")


class LongTermMemory(Base):
    """长期记忆"""
    __tablename__ = "long_term_memory"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(10), ForeignKey("agents.id"))
    title = Column(String(200))
    content = Column(Text)
    tags = Column(JSON, default=list)
    # embedding = Column(VECTOR(1536))  # 向量索引，需要 pgvector 扩展
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent", back_populates="long_term_memories")


class TraceLog(Base):
    """执行追踪日志"""
    __tablename__ = "trace_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    trace_id = Column(String(50))
    span_id = Column(String(50))
    parent_id = Column(String(50), nullable=True)
    agent_id = Column(String(10), ForeignKey("agents.id"))
    action = Column(String(100))
    status = Column(String(20))
    duration_ms = Column(Integer)
    tokens = Column(Integer, default=0)
    credit_used = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent")


class CreditLog(Base):
    """Credit 消耗记录"""
    __tablename__ = "credit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(10), ForeignKey("agents.id"))
    operation = Column(String(50))
    tokens = Column(Integer, default=0)
    cost = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent", back_populates="credit_logs")


class CostStat(Base):
    """成本统计"""
    __tablename__ = "cost_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(10), ForeignKey("agents.id"))
    model = Column(String(50))
    usage_amount = Column(Integer, default=0)
    cost = Column(Integer, default=0)
    period = Column(DateTime)  # 日期
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent", back_populates="cost_stats")


class Conversation(Base):
    """对话历史"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50))
    agent_id = Column(String(10), ForeignKey("agents.id"))
    channel = Column(String(20))
    user_message = Column(Text)
    agent_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent", back_populates="conversations")


class Config(Base):
    """系统配置"""
    __tablename__ = "configs"
    
    key = Column(String(100), primary_key=True)
    value = Column(JSON)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== Indexes ====================

Index("idx_short_term_agent_session", ShortTermMemory.agent_id, ShortTermMemory.session_id)
Index("idx_long_term_agent", LongTermMemory.agent_id)
Index("idx_trace_traceid", TraceLog.trace_id)
Index("idx_credit_agent_date", CreditLog.agent_id, CreditLog.created_at)
Index("idx_conversation_user", Conversation.user_id, Conversation.created_at)


# ==================== Database Commands ====================

class DatabaseCommands:
    """Database management commands."""
    
    @staticmethod
    def init(database_url: Optional[str] = None):
        """Initialize database."""
        init_db(database_url)
    
    @staticmethod
    def backup(backup_path: str):
        """Backup database."""
        import subprocess
        url = get_database_url()
        # pg_dump -Fc -f backup_path
        subprocess.run(["pg_dump", "-Fc", "-f", backup_path, url], check=True)
    
    @staticmethod
    def restore(backup_path: str):
        """Restore database."""
        import subprocess
        url = get_database_url()
        # pg_restore -d url backup_path
        subprocess.run(["pg_restore", "-d", url, backup_path], check=True)
    
    @staticmethod
    def status() -> dict:
        """Check database status."""
        try:
            with session_scope() as session:
                result = session.execute("SELECT 1").fetchone()
                return {"status": "connected", "database": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ==================== Vector Search ====================

def search_by_vector(
    embedding: list,
    limit: int = 5,
    agent_id: str = None
) -> list:
    """
    Search long-term memory by vector embedding.
    
    Args:
        embedding: Vector embedding to search
        limit: Number of results
        agent_id: Filter by agent ID
    
    Returns:
        List of matching memories
    """
    from sqlalchemy import text
    
    with session_scope() as session:
        query = """
            SELECT id, agent_id, title, content, tags, 
                   1 - (embedding <=> :embedding) as similarity
            FROM long_term_memory
            WHERE embedding IS NOT NULL
        """
        
        params = {"embedding": embedding, "limit": limit}
        
        if agent_id:
            query += " AND agent_id = :agent_id"
            params["agent_id"] = agent_id
        
        query += " ORDER BY embedding <=> :embedding LIMIT :limit"
        
        result = session.execute(text(query), params)
        return [
            {
                "id": row[0],
                "agent_id": row[1],
                "title": row[2],
                "content": row[3],
                "tags": row[4],
                "similarity": row[5]
            }
            for row in result
        ]


def add_embedding(memory_id: int, embedding: list) -> None:
    """Add vector embedding to a long-term memory."""
    from sqlalchemy import text
    
    with session_scope() as session:
        session.execute(
            text("UPDATE long_term_memory SET embedding = :embedding WHERE id = :id"),
            {"embedding": embedding, "id": memory_id}
        )
