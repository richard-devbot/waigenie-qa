"""
LanceDB Knowledge Base for WAIGenie.
Stores verified selectors, UI patterns, and test strategies learned from runs.
"""
from __future__ import annotations
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class QAKnowledgeBase:
    """
    Vector knowledge base for QA automation patterns.
    Stores: verified selectors, UI patterns, gherkin templates, test strategies.
    """

    def __init__(self, uri: str = "./waigenie_knowledge", table_name: str = "qa_knowledge"):
        self.uri = uri
        self.table_name = table_name
        self.vector_db = None
        self.knowledge = None
        self._initialized = False
        self._try_init()

    def _try_init(self):
        try:
            from agno.vectordb.lancedb import LanceDb
            self.vector_db = LanceDb(table_name=self.table_name, uri=self.uri)
            self._initialized = True
            logger.info(f"LanceDB Knowledge Base initialized at {self.uri}")
        except ImportError:
            logger.warning("lancedb not available — Knowledge Base disabled")
        except Exception as e:
            logger.warning(f"KB init failed: {e}")

    @property
    def is_ready(self) -> bool:
        return self._initialized and self.vector_db is not None

    def add_text(self, content: str, metadata: dict[str, Any] | None = None) -> bool:
        """Add a text entry to the knowledge base."""
        if not self.is_ready:
            return False
        try:
            from agno.document import Document
            doc = Document(content=content, meta_data=metadata or {})
            self.vector_db.upsert([doc])
            return True
        except Exception as e:
            logger.error(f"KB add_text failed: {e}")
            return False

    def search(self, query: str, num_results: int = 5) -> list[dict]:
        """Semantic search in the knowledge base."""
        if not self.is_ready:
            return []
        try:
            results = self.vector_db.search(query=query, limit=num_results)
            return [{"content": r.content, "metadata": r.meta_data} for r in results] if results else []
        except Exception as e:
            logger.error(f"KB search failed: {e}")
            return []

    def add_selector(self, url: str, element_details: dict[str, Any]) -> bool:
        """Store a verified element selector."""
        selectors = element_details.get("selectors", {})
        if not selectors:
            return False
        content = f"URL: {url}\nElement: {element_details.get('tag_name','')}\nText: {element_details.get('meaningful_text','')}\nSelectors: {selectors}"
        return self.add_text(content, metadata={"type": "selector", "url": url})

    def add_gherkin_pattern(self, scenario: str, url: str) -> bool:
        """Store a successful Gherkin scenario pattern."""
        content = f"Gherkin Pattern for {url}:\n{scenario}"
        return self.add_text(content, metadata={"type": "gherkin", "url": url})


class KnowledgeBaseManager:
    """Singleton manager for the shared QA Knowledge Base."""
    _instance: Optional[QAKnowledgeBase] = None

    @classmethod
    def get_instance(cls) -> QAKnowledgeBase:
        if cls._instance is None:
            try:
                from app.config.settings import settings
                uri = getattr(settings, 'LANCEDB_URI', './waigenie_knowledge')
                cls._instance = QAKnowledgeBase(uri=uri)
            except Exception as e:
                logger.warning(f"KBManager init failed: {e}")
                cls._instance = QAKnowledgeBase()
        return cls._instance
