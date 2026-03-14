"""
Agno Memory V2 integration for WAIGenie.
Provides persistent user context and preferences across sessions.
"""
from __future__ import annotations
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def create_memory(db_file: str = "./waigenie_memory.db"):
    """Create an Agno Memory V2 instance with SQLite backend."""
    try:
        from agno.memory.v2.memory import Memory
        from agno.memory.v2.db.sqlite import SqliteMemoryDb
        memory_db = SqliteMemoryDb(
            table_name="user_memories",
            db_file=db_file,
        )
        return Memory(db=memory_db)
    except ImportError:
        logger.warning("agno memory not available — Memory V2 disabled")
        return None
    except Exception as e:
        logger.warning(f"Could not init Memory V2: {e}")
        return None


class MemoryManager:
    """Singleton manager for the shared Memory instance."""
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            try:
                from app.config.settings import settings
                db_file = getattr(settings, 'MEMORY_DB_FILE', './waigenie_memory.db')
                cls._instance = create_memory(db_file)
                if cls._instance:
                    logger.info("Agno Memory V2 initialized")
            except Exception as e:
                logger.warning(f"MemoryManager init failed: {e}")
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None
