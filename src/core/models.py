"""
统一数据模型定义
为所有PKM Copilot模块提供标准化的数据接口
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class ContentType(str, Enum):
    """内容类型枚举"""
    ARTICLE = "article"
    EMAIL = "email"
    RSS = "rss"
    SOCIAL = "social"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"


class ProcessingStatus(str, Enum):
    """处理状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class DataSourceType(str, Enum):
    """数据源类型枚举"""
    RSS = "rss"
    EMAIL = "email"
    CRAWLER = "crawler"
    API = "api"
    MANUAL = "manual"
    IMPORT = "import"


class EntityType(str, Enum):
    """实体类型枚举"""
    CONCEPT = "concept"
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    EVENT = "event"
    PRODUCT = "product"
    TECHNOLOGY = "technology"


class Article(BaseModel):
    """统一文章模型"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    content: str
    summary: Optional[str] = None
    source: str
    url: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    collected_at: datetime = Field(default_factory=datetime.now)
    
    # 内容分类
    content_type: ContentType = ContentType.ARTICLE
    tags: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    
    # 语义信息
    concepts: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)
    
    # 向量化信息
    embedding: Optional[List[float]] = None
    embedding_model: Optional[str] = None
    
    # 质量评分
    quality_score: Optional[float] = None
    relevance_score: Optional[float] = None
    
    # 元数据
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # 处理状态
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    processing_error: Optional[str] = None
    
    # 关联信息
    related_articles: List[str] = Field(default_factory=list)
    knowledge_graph_id: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RawContent(BaseModel):
    """原始内容模型"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    source_type: DataSourceType
    source_config: Dict[str, Any]
    raw_data: Dict[str, Any]
    collected_at: datetime = Field(default_factory=datetime.now)
    processing_status: ProcessingStatus = ProcessingStatus.PENDING


class ProcessingResult(BaseModel):
    """处理结果模型"""
    article_id: str
    status: ProcessingStatus
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    concepts_extracted: List[str] = Field(default_factory=list)
    keywords_extracted: List[str] = Field(default_factory=list)
    summary_generated: Optional[str] = None
    embedding_generated: bool = False
    processed_at: datetime = Field(default_factory=datetime.now)


class Entity(BaseModel):
    """知识图谱实体模型"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    type: EntityType
    description: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    sources: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Relationship(BaseModel):
    """知识图谱关系模型"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    source_id: str
    target_id: str
    type: str
    strength: float = Field(ge=0.0, le=1.0)
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    sources: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


class VectorData(BaseModel):
    """向量数据模型"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    article_id: str
    content: str
    embedding: List[float]
    embedding_model: str
    content_type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


class FilterConfig(BaseModel):
    """过滤配置模型"""
    min_quality_score: Optional[float] = None
    min_relevance_score: Optional[float] = None
    required_tags: List[str] = Field(default_factory=list)
    excluded_tags: List[str] = Field(default_factory=list)
    date_range: Optional[Dict[str, datetime]] = None
    source_whitelist: List[str] = Field(default_factory=list)
    source_blacklist: List[str] = Field(default_factory=list)


class SummaryConfig(BaseModel):
    """总结配置模型"""
    summary_type: str = "brief"  # brief, detailed, bullet_points
    max_length: int = 500
    include_keywords: bool = True
    include_concepts: bool = True
    output_format: str = "markdown"  # markdown, json, html
    language: str = "zh"


class Collection(BaseModel):
    """收藏模型"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: Optional[str] = None
    article_ids: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_public: bool = False
    owner_id: Optional[str] = None


class SearchQuery(BaseModel):
    """搜索查询模型"""
    query: str
    filters: Optional[FilterConfig] = None
    limit: int = 10
    offset: int = 0
    search_type: str = "semantic"  # semantic, keyword, hybrid
    sort_by: str = "relevance"
    include_vectors: bool = False


class SearchResult(BaseModel):
    """搜索结果模型"""
    article: Article
    score: float
    highlights: List[str] = Field(default_factory=list)
    matched_keywords: List[str] = Field(default_factory=list)


class ProcessingJob(BaseModel):
    """处理任务模型"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    source_config: Dict[str, Any]
    processing_config: Dict[str, Any]
    status: ProcessingStatus = ProcessingStatus.PENDING
    progress: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    results_count: int = 0


class DataSource(BaseModel):
    """数据源模型"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    type: DataSourceType
    config: Dict[str, Any]
    is_active: bool = True
    last_sync: Optional[datetime] = None
    sync_interval: Optional[int] = None  # 分钟
    created_at: datetime = Field(default_factory=datetime.now)


class SyncStatus(BaseModel):
    """同步状态模型"""
    source_id: str
    last_sync: datetime
    next_sync: Optional[datetime] = None
    articles_synced: int = 0
    errors: List[str] = Field(default_factory=list)
    is_successful: bool = True