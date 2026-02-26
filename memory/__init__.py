# -*- coding: utf-8 -*-
"""
Memory System for cp9 Agents

Manages:
- Short-term memory: Current task context (session-based)
- Long-term memory: Persistent knowledge and experience
"""

import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

# Try to import database, fallback to file-based storage
try:
    from db import session_scope, ShortTermMemory, LongTermMemory
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False


class MemoryStore:
    """File-based memory storage (fallback when DB is not available)"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or "~/.cp9/memory")
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_short_term_path(self, agent_id: str, session_id: str) -> Path:
        path = self.base_path / agent_id / "short_term" / f"{session_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    
    def _get_long_term_path(self, agent_id: str) -> Path:
        path = self.base_path / agent_id / "long_term"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    # Short-term memory
    def save_short_term(self, agent_id: str, session_id: str, content: Dict[str, Any]) -> None:
        path = self._get_short_term_path(agent_id, session_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
    
    def load_short_term(self, agent_id: str, session_id: str) -> Optional[Dict[str, Any]]:
        path = self._get_short_term_path(agent_id, session_id)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
    
    def clear_short_term(self, agent_id: str, session_id: str) -> None:
        path = self._get_short_term_path(agent_id, session_id)
        if path.exists():
            path.unlink()
    
    # Long-term memory
    def save_long_term(
        self, 
        agent_id: str, 
        title: str, 
        content: str, 
        tags: List[str] = None
    ) -> str:
        path = self._get_long_term_path(agent_id)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{title[:50]}.md"
        
        # Create markdown file
        file_path = path / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            if tags:
                f.write(f"**Tags**: {', '.join(tags)}\n\n")
            f.write(f"**Created**: {datetime.now().isoformat()}\n\n")
            f.write("---\n\n")
            f.write(content)
        
        # Save metadata
        meta = {
            "title": title,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "file": filename
        }
        meta_path = path / f"{filename}.meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False)
        
        return filename
    
    def list_long_term(self, agent_id: str) -> List[Dict[str, Any]]:
        path = self._get_long_term_path(agent_id)
        if not path.exists():
            return []
        
        results = []
        for meta_file in path.glob("*.meta.json"):
            with open(meta_file, "r", encoding="utf-8") as f:
                results.append(json.load(f))
        
        return sorted(results, key=lambda x: x.get("created_at", ""), reverse=True)
    
    def get_long_term(self, agent_id: str, filename: str) -> Optional[str]:
        path = self._get_long_term_path(agent_id) / filename
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return None


class MemorySystem:
    """
    Unified memory system for agents.
    Uses database if available, falls back to file storage.
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        
        if DB_AVAILABLE:
            self.use_db = True
        else:
            self.use_db = False
            self.file_store = MemoryStore()
    
    # ==================== Short-term Memory ====================
    
    def save_short_term(
        self, 
        session_id: str, 
        content: Dict[str, Any],
        expires_hours: int = 24
    ) -> None:
        """Save short-term memory (current task context)."""
        
        if self.use_db:
            with session_scope() as session:
                expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
                memory = ShortTermMemory(
                    agent_id=self.agent_id,
                    session_id=session_id,
                    content=content,
                    expires_at=expires_at
                )
                session.merge(memory)
        else:
            self.file_store.save_short_term(self.agent_id, session_id, content)
    
    def load_short_term(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load short-term memory."""
        
        if self.use_db:
            with session_scope() as session:
                memory = session.query(ShortTermMemory).filter(
                    ShortTermMemory.agent_id == self.agent_id,
                    ShortTermMemory.session_id == session_id
                ).first()
                
                if memory:
                    # Check if expired
                    if memory.expires_at and memory.expires_at < datetime.utcnow():
                        session.delete(memory)
                        return None
                    return memory.content
                return None
        else:
            return self.file_store.load_short_term(self.agent_id, session_id)
    
    def clear_short_term(self, session_id: str) -> None:
        """Clear short-term memory."""
        
        if self.use_db:
            with session_scope() as session:
                session.query(ShortTermMemory).filter(
                    ShortTermMemory.agent_id == self.agent_id,
                    ShortTermMemory.session_id == session_id
                ).delete()
        else:
            self.file_store.clear_short_term(self.agent_id, session_id)
    
    # ==================== Long-term Memory ====================
    
    def save_long_term(
        self, 
        title: str, 
        content: str, 
        tags: List[str] = None
    ) -> str:
        """Save long-term memory (knowledge, experience)."""
        
        if self.use_db:
            with session_scope() as session:
                memory = LongTermMemory(
                    agent_id=self.agent_id,
                    title=title,
                    content=content,
                    tags=tags or []
                )
                session.add(memory)
                session.flush()
                return str(memory.id)
        else:
            return self.file_store.save_long_term(self.agent_id, title, content, tags)
    
    def list_long_term(
        self, 
        tag: str = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List long-term memories."""
        
        if self.use_db:
            with session_scope() as session:
                query = session.query(LongTermMemory).filter(
                    LongTermMemory.agent_id == self.agent_id
                )
                
                if tag:
                    query = query.filter(LongTermMemory.tags.contains(tag))
                
                memories = query.order_by(
                    LongTermMemory.created_at.desc()
                ).limit(limit).all()
                
                return [
                    {
                        "id": m.id,
                        "title": m.title,
                        "content": m.content,
                        "tags": m.tags,
                        "created_at": m.created_at.isoformat()
                    }
                    for m in memories
                ]
        else:
            results = self.file_store.list_long_term(self.agent_id)
            if tag:
                results = [r for r in results if tag in r.get("tags", [])]
            return results[:limit]
    
    def search_long_term(self, keyword: str) -> List[Dict[str, Any]]:
        """Search long-term memory by keyword."""
        
        if self.use_db:
            with session_scope() as session:
                memories = session.query(LongTermMemory).filter(
                    LongTermMemory.agent_id == self.agent_id,
                    LongTermMemory.content.ilike(f"%{keyword}%")
                ).all()
                
                return [
                    {
                        "id": m.id,
                        "title": m.title,
                        "content": m.content[:200] + "...",
                        "tags": m.tags,
                        "created_at": m.created_at.isoformat()
                    }
                    for m in memories
                ]
        else:
            results = []
            for mem in self.file_store.list_long_term(self.agent_id):
                content = self.file_store.get_long_term(
                    self.agent_id, 
                    mem["file"]
                )
                if content and keyword.lower() in content.lower():
                    results.append({
                        **mem,
                        "content": content[:200] + "..."
                    })
            return results


# ==================== Exports ====================

__all__ = [
    "MemorySystem",
    "MemoryStore",
]
