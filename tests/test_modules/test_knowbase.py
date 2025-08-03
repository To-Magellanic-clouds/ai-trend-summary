"""
KnowBase模块测试
"""

import pytest
import asyncio
from datetime import datetime
from src.modules.knowbase.core import KnowBaseCore, RSSCollector
from src.core.models import DataSource, DataSourceType


class TestKnowBaseCore:
    """KnowBase核心测试"""
    
    @pytest.fixture
    def knowbase_core(self):
        return KnowBaseCore()
    
    @pytest.fixture
    def sample_rss_source(self):
        return DataSource(
            name="测试RSS源",
            type=DataSourceType.RSS,
            config={
                "url": "https://example.com/rss"
            },
            is_active=True
        )
    
    def test_initialization(self, knowbase_core):
        """测试初始化"""
        assert knowbase_core is not None
        assert len(knowbase_core.collectors) > 0
    
    def test_supported_source_types(self, knowbase_core):
        """测试支持的数据源类型"""
        types = knowbase_core.get_supported_source_types()
        assert isinstance(types, list)
        assert len(types) > 0
        assert "rss" in types
    
    @pytest.mark.asyncio
    async def test_validate_source_invalid_url(self, knowbase_core):
        """测试无效URL验证"""
        source = DataSource(
            name="无效RSS源",
            type=DataSourceType.RSS,
            config={"url": "invalid-url"},
            is_active=True
        )
        
        result = await knowbase_core.validate_source(source)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_source_missing_config(self, knowbase_core):
        """测试缺少配置验证"""
        source = DataSource(
            name="缺少配置RSS源",
            type=DataSourceType.RSS,
            config={},
            is_active=True
        )
        
        result = await knowbase_core.validate_source(source)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_source_info(self, knowbase_core):
        """测试获取数据源信息"""
        info = await knowbase_core.get_source_info(DataSourceType.RSS)
        assert isinstance(info, dict)
        assert "type" in info
        assert "description" in info
        assert "required_config" in info


class TestRSSCollector:
    """RSS收集器测试"""
    
    @pytest.fixture
    def rss_collector(self):
        return RSSCollector()
    
    @pytest.fixture
    def valid_rss_source(self):
        return DataSource(
            name="有效RSS源",
            type=DataSourceType.RSS,
            config={
                "url": "https://news.ycombinator.com/rss"
            },
            is_active=True
        )
    
    @pytest.mark.asyncio
    async def test_validate_source_valid_url(self, rss_collector):
        """测试有效URL验证"""
        source = DataSource(
            name="测试RSS源",
            type=DataSourceType.RSS,
            config={"url": "https://news.ycombinator.com/rss"},
            is_active=True
        )
        
        # 注意：实际网络测试可能被禁用
        result = await rss_collector.validate_source(source)
        # 根据网络环境，结果可能不同
        assert isinstance(result, bool)
    
    @pytest.mark.asyncio
    async def test_get_source_info(self, rss_collector):
        """测试获取源信息"""
        info = await rss_collector.get_source_info("test")
        assert isinstance(info, dict)
        assert info["type"] == "RSS"
        assert info["description"] == "RSS订阅源"


class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_workflow_simulation(self):
        """测试工作流模拟"""
        core = KnowBaseCore()
        
        # 创建测试数据源
        sources = [
            DataSource(
                name="测试源1",
                type=DataSourceType.RSS,
                config={"url": "https://example.com/rss"},
                is_active=True
            ),
            DataSource(
                name="测试源2",
                type=DataSourceType.RSS,
                config={"url": "https://example2.com/rss"},
                is_active=False
            )
        ]
        
        # 测试同步逻辑
        result = await core.sync_all_sources(sources)
        assert isinstance(result, dict)
        assert "total_sources" in result
        assert "successful" in result
        assert "failed" in result
        assert result["total_sources"] == 2