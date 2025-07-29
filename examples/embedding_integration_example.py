"""
项目集成示例
演示如何在AI趋势总结项目中集成向量化SDK
"""

import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime

# 导入向量化SDK
from src.infrastructure.embedding import (
    create_embedding_manager,
    DocumentInput,
    EmbeddingSystemConfig
)

logger = logging.getLogger(__name__)


class AITrendVectorizer:
    """AI趋势向量化器 - 项目特定的向量化封装"""
    
    def __init__(self, config: EmbeddingSystemConfig = None):
        self.config = config or EmbeddingSystemConfig.from_env()
        self.manager = None
    
    async def initialize(self):
        """初始化向量化器"""
        try:
            manager_config = self.config.create_manager_config(
                collection_name="ai_trend_articles"
            )
            
            from src.infrastructure.embedding import EmbeddingManager
            self.manager = EmbeddingManager(manager_config)
            
            success = await self.manager.initialize()
            if success:
                logger.info("AI趋势向量化器初始化成功")
            return success
            
        except Exception as e:
            logger.error(f"向量化器初始化失败: {e}")
            return False
    
    async def close(self):
        """关闭向量化器"""
        if self.manager:
            await self.manager.close()
    
    async def add_article(self, article_data: Dict[str, Any]) -> bool:
        """添加文章到向量数据库"""
        try:
            # 构建文档内容
            content_parts = []
            
            if article_data.get("title"):
                content_parts.append(f"标题: {article_data['title']}")
            
            if article_data.get("summary"):
                content_parts.append(f"摘要: {article_data['summary']}")
            
            if article_data.get("content"):
                content_parts.append(f"内容: {article_data['content']}")
            
            content = "\n\n".join(content_parts)
            
            # 构建元数据
            metadata = {
                "article_id": article_data.get("id"),
                "title": article_data.get("title", ""),
                "source": article_data.get("source", ""),
                "url": article_data.get("url", ""),
                "published_date": article_data.get("published_date", ""),
                "category": article_data.get("category", ""),
                "tags": article_data.get("tags", []),
                "language": article_data.get("language", "zh"),
                "indexed_at": datetime.now().isoformat()
            }
            
            # 创建文档
            document = DocumentInput(
                id=article_data.get("id"),
                content=content,
                metadata=metadata
            )
            
            # 添加到向量数据库
            success = await self.manager.add_document(document)
            
            if success:
                logger.info(f"成功添加文章: {article_data.get('title', 'Unknown')}")
            
            return success
            
        except Exception as e:
            logger.error(f"添加文章失败: {e}")
            return False
    
    async def add_articles_batch(self, articles: List[Dict[str, Any]]) -> int:
        """批量添加文章"""
        documents = []
        
        for article in articles:
            try:
                # 构建内容和元数据（同上）
                content_parts = []
                if article.get("title"):
                    content_parts.append(f"标题: {article['title']}")
                if article.get("summary"):
                    content_parts.append(f"摘要: {article['summary']}")
                if article.get("content"):
                    content_parts.append(f"内容: {article['content']}")
                
                content = "\n\n".join(content_parts)
                
                metadata = {
                    "article_id": article.get("id"),
                    "title": article.get("title", ""),
                    "source": article.get("source", ""),
                    "url": article.get("url", ""),
                    "published_date": article.get("published_date", ""),
                    "category": article.get("category", ""),
                    "tags": article.get("tags", []),
                    "language": article.get("language", "zh"),
                    "indexed_at": datetime.now().isoformat()
                }
                
                document = DocumentInput(
                    id=article.get("id"),
                    content=content,
                    metadata=metadata
                )
                documents.append(document)
                
            except Exception as e:
                logger.error(f"处理文章失败: {e}")
                continue
        
        if documents:
            success = await self.manager.add_documents(documents)
            if success:
                logger.info(f"批量添加 {len(documents)} 篇文章成功")
                return len(documents)
        
        return 0
    
    async def search_articles(self, query: str, 
                            top_k: int = 10,
                            filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """搜索相关文章"""
        try:
            results = await self.manager.search_similar_documents(
                query, top_k, filter_conditions=filters
            )
            
            articles = []
            for result in results:
                article = {
                    "id": result.document.id,
                    "content": result.document.content,
                    "metadata": result.document.metadata,
                    "similarity_score": result.score,
                    "title": result.document.metadata.get("title", ""),
                    "source": result.document.metadata.get("source", ""),
                    "url": result.document.metadata.get("url", ""),
                    "category": result.document.metadata.get("category", ""),
                    "published_date": result.document.metadata.get("published_date", "")
                }
                articles.append(article)
            
            logger.info(f"搜索查询 '{query}' 返回 {len(articles)} 个结果")
            return articles
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    async def search_by_category(self, category: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """按类别搜索文章"""
        return await self.search_articles(
            query="",  # 空查询，主要依靠过滤
            top_k=top_k,
            filters={"category": category}
        )
    
    async def search_recent_articles(self, days: int = 7, top_k: int = 10) -> List[Dict[str, Any]]:
        """搜索最近的文章"""
        from datetime import datetime, timedelta
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # 注意：这里的日期过滤需要Qdrant支持范围查询
        # 简化版本，可以在应用层过滤
        results = await self.search_articles("最新 AI 技术", top_k=top_k * 2)
        
        # 应用层过滤
        recent_articles = []
        for article in results:
            pub_date = article["metadata"].get("published_date", "")
            if pub_date and pub_date >= cutoff_date:
                recent_articles.append(article)
                if len(recent_articles) >= top_k:
                    break
        
        return recent_articles
    
    async def get_article_stats(self) -> Dict[str, Any]:
        """获取文章统计信息"""
        try:
            count = await self.manager.count_documents()
            info = await self.manager.get_collection_info()
            
            return {
                "total_articles": count,
                "collection_info": info,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}


async def demo_integration():
    """演示集成使用"""
    print("=== AI趋势向量化器集成演示 ===")
    
    # 创建向量化器
    vectorizer = AITrendVectorizer()
    
    try:
        # 初始化
        success = await vectorizer.initialize()
        if not success:
            print("初始化失败")
            return
        
        print("✓ 向量化器初始化成功")
        
        # 模拟文章数据
        sample_articles = [
            {
                "id": "article_001",
                "title": "GPT-4的最新突破：多模态能力大幅提升",
                "summary": "OpenAI发布的GPT-4在图像理解和文本生成方面取得重大进展",
                "content": "GPT-4是OpenAI最新发布的大型语言模型，具备强大的多模态处理能力...",
                "source": "AI研究院",
                "url": "https://example.com/gpt4-breakthrough",
                "published_date": "2024-01-15T10:00:00",
                "category": "AI模型",
                "tags": ["GPT-4", "多模态", "OpenAI"],
                "language": "zh"
            },
            {
                "id": "article_002", 
                "title": "深度学习在医疗诊断中的应用",
                "summary": "深度学习技术在医疗影像诊断领域展现出巨大潜力",
                "content": "近年来，深度学习技术在医疗诊断领域取得了显著进展...",
                "source": "医疗AI期刊",
                "url": "https://example.com/dl-medical",
                "published_date": "2024-01-14T15:30:00",
                "category": "AI应用",
                "tags": ["深度学习", "医疗", "诊断"],
                "language": "zh"
            },
            {
                "id": "article_003",
                "title": "Transformer架构的演进历程",
                "summary": "从原始Transformer到现代大型语言模型的发展轨迹",
                "content": "Transformer架构自2017年提出以来，经历了多次重要改进...",
                "source": "技术博客",
                "url": "https://example.com/transformer-evolution",
                "published_date": "2024-01-13T09:15:00",
                "category": "AI技术",
                "tags": ["Transformer", "架构", "演进"],
                "language": "zh"
            }
        ]
        
        # 批量添加文章
        added_count = await vectorizer.add_articles_batch(sample_articles)
        print(f"✓ 成功添加 {added_count} 篇文章")
        
        # 获取统计信息
        stats = await vectorizer.get_article_stats()
        print(f"✓ 文章总数: {stats.get('total_articles', 0)}")
        
        # 搜索测试
        print("\n--- 搜索测试 ---")
        
        # 1. 关键词搜索
        results = await vectorizer.search_articles("GPT-4 多模态", top_k=3)
        print(f"搜索 'GPT-4 多模态': {len(results)} 个结果")
        for i, article in enumerate(results, 1):
            print(f"  {i}. {article['title']} (相似度: {article['similarity_score']:.4f})")
        
        # 2. 类别搜索
        results = await vectorizer.search_by_category("AI模型", top_k=5)
        print(f"\n类别搜索 'AI模型': {len(results)} 个结果")
        for article in results:
            print(f"  - {article['title']}")
        
        # 3. 技术主题搜索
        results = await vectorizer.search_articles("深度学习医疗应用", top_k=3)
        print(f"\n搜索 '深度学习医疗应用': {len(results)} 个结果")
        for article in results:
            print(f"  - {article['title']} (相似度: {article['similarity_score']:.4f})")
        
        print("\n✓ 集成演示完成")
        
    except Exception as e:
        print(f"✗ 演示过程中出错: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await vectorizer.close()


if __name__ == "__main__":
    # 运行集成演示
    asyncio.run(demo_integration())