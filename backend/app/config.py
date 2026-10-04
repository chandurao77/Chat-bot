from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Confluence
    confluence_url: str = "https://your-domain.atlassian.net"
    confluence_username: str = ""
    confluence_api_token: str = ""
    confluence_spaces: str = ""

    # Ollama
    ollama_base_url: str = "http://ollama:11434"
    ollama_llm_model: str = "mistral:7b"
    ollama_embed_model: str = "nomic-embed-text"

    # Qdrant
    qdrant_url: str = "http://qdrant:6333"
    qdrant_collection: str = "jarvis_docs"
    qdrant_semantic_cache_collection: str = "jarvis_cache"

    # SQLite
    sqlite_path: str = "/data/jarvis.db"

    # Auth
    api_key: str = ""

    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Rate limiting
    rate_limit_rpm: int = 30

    # Environment
    environment: str = "development"
    log_level: str = "INFO"

    # LLM settings
    llm_temperature: float = 0.1
    llm_top_p: float = 0.9
    llm_max_tokens: int = 512
    llm_max_sources: int = 15

    # Retrieval
    retrieval_top_k: int = 10
    retrieval_score_threshold: float = 0.30

    # Chunking
    chunk_size: int = 256
    chunk_overlap: int = 64

    # Semantic cache
    semantic_cache_threshold: float = 0.97
    semantic_cache_ttl: int = 1800

    # Graph RAG
    graph_hop_depth: int = 1
    graph_max_expansion: int = 4

    # Conversation
    max_history_turns: int = 6
    max_question_length: int = 2000
    conversation_prune_days: int = 90

    # Embedding
    embed_batch_size: int = 32
    embed_cache_ttl: int = 300
    upsert_batch_size: int = 100

    # Local docs
    local_docs_path: str = "/local_docs"

    # Optional integrations
    azure_openai_enabled: bool = False
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = ""
    redis_enabled: bool = False
    redis_url: str = "redis://redis:6379"

    # Words kept from each retrieved source when building the prompt
    words_per_source: int = 400

    # Aliases: the older app/core and app/ingestion modules use these names.
    # They read from the canonical settings above so there is one source of truth.
    @property
    def vector_top_k(self) -> int: return self.retrieval_top_k
    @property
    def vector_score_threshold(self) -> float: return self.retrieval_score_threshold
    @property
    def max_sources(self) -> int: return self.llm_max_sources
    @property
    def conversation_history_turns(self) -> int: return self.max_history_turns
    @property
    def chunk_size_words(self) -> int: return self.chunk_size
    @property
    def chunk_overlap_words(self) -> int: return self.chunk_overlap
    @property
    def embed_cache_ttl_seconds(self) -> int: return self.embed_cache_ttl
    @property
    def graph_rag_max_extra(self) -> int: return self.graph_max_expansion
    @property
    def llm_num_predict(self) -> int: return self.llm_max_tokens
    @property
    def semantic_cache_ttl_minutes(self) -> int: return max(1, self.semantic_cache_ttl // 60)

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
