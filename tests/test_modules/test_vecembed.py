"""
VecEmbed模块测试
"""

import pytest
import asyncio
import numpy as np
from src.modules.vecembed.core import VecEmbedCore, SentenceTransformerVectorizer
from src.core.models import VectorData


class TestVecEmbedCore:
    """VecEmbed核心测试"""
    
    @pytest.fixture
    def vecembed_core(self):
        return VecEmbedCore()
    
    def test_initialization(self, vecembed_core):
        """测试初始化"""
        assert vecembed_core is not None
        assert vecembed_core.config is not None
    
    def test_get_vector_size(self, vecembed_core):
        """测试获取向量维度"""
        # 测试默认模型
        size = vecembed_core.get_vector_size()
        assert isinstance(size, int)
        assert size > 0
        
        # 测试OpenAI模型
        openai_size = vecembed_core.get_vector_size("text-embedding-3-small")
        assert openai_size == 1536
        
        openai_large_size = vecembed_core.get_vector_size("text-embedding-3-large")
        assert openai_large_size == 3072
    
    def test_get_available_models(self, vecembed_core):
        """测试获取可用模型"""
        models = vecembed_core.get_available_models()
        assert isinstance(models, dict)
        assert len(models) > 0
        assert "sentence_transformers" in models
    
    @pytest.mark.asyncio
    async def test_vectorize_text(self, vecembed_core):
        """测试文本向量化"""
        text = "这是一个测试文本"
        embedding = await vecembed_core.vectorize_text(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, (int, float)) for x in embedding)
    
    @pytest.mark.asyncio
    async def test_vectorize_empty_text(self, vecembed_core):
        """测试空文本向量化"""
        embedding = await vecembed_core.vectorize_text("")
        assert isinstance(embedding, list)
        assert len(embedding) == 0
    
    @pytest.mark.asyncio
    async def test_vectorize_batch(self, vecembed_core):
        """测试批量向量化"""
        texts = ["文本1", "文本2", "文本3"]
        embeddings = await vecembed_core.vectorize_batch(texts)
        
        assert isinstance(embeddings, list)
        assert len(embeddings) == 3
        assert all(isinstance(emb, list) for emb in embeddings)
        assert all(len(emb) > 0 for emb in embeddings)
    
    @pytest.mark.asyncio
    async def test_vectorize_batch_with_empty(self, vecembed_core):
        """测试包含空文本的批量向量化"""
        texts = ["文本1", "", "文本3"]
        embeddings = await vecembed_core.vectorize_batch(texts)
        
        assert isinstance(embeddings, list)
        assert len(embeddings) == 3
        assert len(embeddings[0]) > 0  # 非空文本
        assert len(embeddings[1]) == 0  # 空文本
        assert len(embeddings[2]) > 0  # 非空文本
    
    @pytest.mark.asyncio
    async def test_create_collection(self, vecembed_core):
        """测试创建向量集合"""
        # 注意：实际测试可能需要跳过，因为需要向量数据库
        if vecembed_core.vector_store is None:
            pytest.skip("向量存储未初始化")
        
        success = await vecembed_core.create_collection(384)
        assert isinstance(success, bool)
    
    @pytest.mark.asyncio
    async def test_search_similar(self, vecembed_core):
        """测试相似搜索"""
        # 注意：实际测试可能需要跳过，因为需要向量数据库
        if vecembed_core.vector_store is None:
            pytest.skip("向量存储未初始化")
        
        results = await vecembed_core.search_similar("测试查询")
        assert isinstance(results, list)


class TestSentenceTransformerVectorizer:
    """Sentence Transformers向量化器测试"""
    
    @pytest.fixture
    def vectorizer(self):
        return SentenceTransformerVectorizer("all-MiniLM-L6-v2")
    
    @pytest.mark.asyncio
    async def test_vectorize_text(self, vectorizer):
        """测试文本向量化"""
        text = "这是一个测试文本"
        embedding = await vectorizer.vectorize_text(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == 384  # all-MiniLM-L6-v2的维度
        assert all(isinstance(x, float) for x in embedding)
    
    @pytest.mark.asyncio
    async def test_vectorize_batch(self, vectorizer):
        """测试批量向量化"""
        texts = ["文本1", "文本2", "文本3"]
        embeddings = await vectorizer.vectorize_batch(texts)
        
        assert isinstance(embeddings, list)
        assert len(embeddings) == 3
        assert all(len(emb) == 384 for emb in embeddings)
    
    @pytest.mark.asyncio
    async def test_vector_similarity(self, vectorizer):
        """测试向量相似性"""
        text1 = "机器学习"
        text2 = "深度学习"
        text3 = "苹果派"
        
        emb1 = await vectorizer.vectorize_text(text1)
        emb2 = await vectorizer.vectorize_text(text2)
        emb3 = await vectorizer.vectorize_text(text3)
        
        # 计算余弦相似度
        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
        sim12 = cosine_similarity(emb1, emb2)
        sim13 = cosine_similarity(emb1, emb3)
        
        # 相关文本应该有更高的相似度
        assert sim12 > sim13


class TestVectorData:
    """向量数据测试"""
    
    def test_vector_data_creation(self):
        """测试向量数据创建"""
        vector_data = VectorData(
            article_id="test-article-1",
            content="测试内容",
            embedding=[0.1, 0.2, 0.3],
            embedding_model="test-model",
            content_type="text"
        )
        
        assert vector_data.article_id == "test-article-1"
        assert vector_data.content == "测试内容"
        assert vector_data.embedding == [0.1, 0.2, 0.3]
        assert vector_data.embedding_model == "test-model"
        assert vector_data.content_type == "text"
        assert vector_data.created_at is not None


class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_embedding_workflow(self):
        """测试完整向量化工作流"""
        core = VecEmbedCore()
        
        # 测试文本
        texts = [
            "人工智能是计算机科学的一个分支",
            "机器学习是AI的重要技术",
            "深度学习使用神经网络进行学习"
        ]
        
        # 向量化
        embeddings = await core.vectorize_batch(texts)
        
        assert len(embeddings) == 3
        assert all(len(emb) > 0 for emb in embeddings)
        
        # 测试相似度计算
        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
        sim = cosine_similarity(embeddings[0], embeddings[1])
        assert 0 <= sim <= 1