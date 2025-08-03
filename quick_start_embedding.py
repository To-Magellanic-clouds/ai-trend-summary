#!/usr/bin/env python3
"""
Qdrant低配置快速开始脚本
演示如何在不同场景下使用最简单的配置运行向量化SDK
"""

import asyncio
import logging
from pathlib import Path
import sys

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """设置简单日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )

async def quick_start_memory_mode():
    """快速开始 - 内存模式（最简单）"""
    print("🚀 快速开始 - 内存模式")
    print("="*40)
    
    try:
        from src.infrastructure.embedding import (
            EmbeddingSystemConfig,
            EmbeddingManager,
            DocumentInput
        )
        
        # 创建内存模式配置
        config = EmbeddingSystemConfig(
            qdrant_host=":memory:",  # 内存模式
            qdrant_port=None,
            default_embedding_model="sentence-transformers/all-MiniLM-L6-v2",  # 轻量级模型
            default_embedding_type="sentence_transformers"
        )
        
        # 创建管理器
        manager_config = config.create_manager_config("quick_start")
        manager = EmbeddingManager(manager_config)
        
        print("⏳ 初始化向量化SDK...")
        success = await manager.initialize()
        
        if not success:
            print("❌ 初始化失败")
            return False
        
        print("✅ 初始化成功！")
        
        # 添加一些示例文档
        documents = [
            DocumentInput(
                id="doc1",
                content="人工智能是计算机科学的一个重要分支，致力于创建能够执行通常需要人类智能的任务的系统。",
                metadata={"category": "AI基础", "language": "zh"}
            ),
            DocumentInput(
                id="doc2",
                content="机器学习是人工智能的一个子领域，通过算法让计算机从数据中学习模式。",
                metadata={"category": "机器学习", "language": "zh"}
            ),
            DocumentInput(
                id="doc3",
                content="深度学习使用神经网络来模拟人脑的学习过程，在图像识别和自然语言处理方面取得了突破。",
                metadata={"category": "深度学习", "language": "zh"}
            ),
            DocumentInput(
                id="doc4",
                content="自然语言处理(NLP)是人工智能的一个分支，专注于让计算机理解和生成人类语言。",
                metadata={"category": "NLP", "language": "zh"}
            ),
            DocumentInput(
                id="doc5",
                content="计算机视觉让机器能够识别和理解图像内容，广泛应用于自动驾驶和医疗诊断。",
                metadata={"category": "计算机视觉", "language": "zh"}
            )
        ]
        
        print(f"⏳ 添加 {len(documents)} 个文档...")
        
        for doc in documents:
            await manager.add_document(doc)
        
        print("✅ 文档添加完成！")
        
        # 进行一些搜索测试
        search_queries = [
            "什么是人工智能？",
            "机器学习算法",
            "神经网络深度学习",
            "图像识别技术",
            "语言处理"
        ]
        
        print("\n🔍 搜索测试:")
        print("-" * 40)
        
        for query in search_queries:
            results = await manager.search_similar_documents(query, top_k=2)
            
            print(f"\n查询: '{query}'")
            if results:
                for i, result in enumerate(results, 1):
                    print(f"  {i}. 相似度: {result.score:.4f}")
                    print(f"     类别: {result.document.metadata.get('category', 'Unknown')}")
                    print(f"     内容: {result.document.content[:60]}...")
            else:
                print("  未找到相关结果")
        
        # 获取统计信息
        count = await manager.count_documents()
        print(f"\n📊 统计信息:")
        print(f"   总文档数: {count}")
        
        # 关闭连接
        await manager.close()
        print("\n✅ 演示完成！")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

async def quick_start_file_mode():
    """快速开始 - 文件存储模式"""
    print("\n🚀 快速开始 - 文件存储模式")
    print("="*40)
    
    try:
        from src.infrastructure.embedding import (
            EmbeddingSystemConfig,
            EmbeddingManager,
            DocumentInput
        )
        
        # 创建文件存储模式配置
        storage_path = "./quick_start_data"
        config = EmbeddingSystemConfig(
            qdrant_host=storage_path,
            qdrant_port=None,
            qdrant_path=storage_path,
            default_embedding_model="sentence-transformers/all-MiniLM-L6-v2",
            default_embedding_type="sentence_transformers"
        )
        
        # 创建管理器
        manager_config = config.create_manager_config("file_test")
        manager = EmbeddingManager(manager_config)
        
        print(f"⏳ 初始化向量化SDK（文件存储: {storage_path}）...")
        success = await manager.initialize()
        
        if not success:
            print("❌ 初始化失败")
            return False
        
        print("✅ 初始化成功！")
        
        # 添加文档
        doc = DocumentInput(
            id="file_doc1",
            content="这是一个存储在文件中的测试文档，重启后数据仍然存在。",
            metadata={"type": "persistent", "created": "2024-01-15"}
        )
        
        await manager.add_document(doc)
        print("✅ 文档已保存到文件存储")
        
        # 搜索测试
        results = await manager.search_similar_documents("文件存储", top_k=1)
        if results:
            print(f"✅ 搜索成功，相似度: {results[0].score:.4f}")
        
        await manager.close()
        print(f"✅ 数据已持久化到: {storage_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def print_usage_guide():
    """打印使用指南"""
    print("\n" + "="*60)
    print("📖 Qdrant低配置使用指南")
    print("="*60)
    
    print("\n🎯 选择合适的模式:")
    print("┌─────────────────┬─────────────────┬─────────────────┐")
    print("│      场景       │    推荐模式     │    连接方式     │")
    print("├─────────────────┼─────────────────┼─────────────────┤")
    print("│ 开发测试        │ 内存模式        │ ':memory:'      │")
    print("│ 原型验证        │ 内存模式        │ ':memory:'      │")
    print("│ 小型应用        │ 文件存储模式    │ './data'        │")
    print("│ 单机部署        │ 文件存储模式    │ './data'        │")
    print("│ 生产环境        │ 服务器模式      │ 'host:6333'     │")
    print("│ 大规模应用      │ 服务器模式      │ 'host:6333'     │")
    print("└─────────────────┴─────────────────┴─────────────────┘")
    
    print("\n💡 代码示例:")
    
    print("\n1️⃣ 内存模式（最简单）:")
    print("```python")
    print("from qdrant_client import QdrantClient")
    print("client = QdrantClient(':memory:')")
    print("```")
    
    print("\n2️⃣ 文件存储模式:")
    print("```python")
    print("from qdrant_client import QdrantClient")
    print("client = QdrantClient(path='./my_data')")
    print("```")
    
    print("\n3️⃣ 服务器模式:")
    print("```python")
    print("from qdrant_client import QdrantClient")
    print("client = QdrantClient(url='http://localhost:6333')")
    print("```")
    
    print("\n🔧 使用我们的SDK:")
    print("```python")
    print("from src.infrastructure.embedding import EmbeddingSystemConfig")
    print("")
    print("# 内存模式")
    print("config = EmbeddingSystemConfig(qdrant_host=':memory:')")
    print("")
    print("# 文件模式")
    print("config = EmbeddingSystemConfig(")
    print("    qdrant_host='./data',")
    print("    qdrant_path='./data'")
    print(")")
    print("```")

async def main():
    """主函数"""
    print("🎉 Qdrant低配置快速开始")
    print("="*30)
    
    setup_logging()
    
    # 检查依赖
    try:
        import qdrant_client
        import sentence_transformers
        print("✅ 依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install qdrant-client sentence-transformers")
        return
    
    # 运行内存模式演示
    memory_success = await quick_start_memory_mode()
    
    if memory_success:
        # 运行文件存储模式演示
        await quick_start_file_mode()
    
    # 打印使用指南
    print_usage_guide()
    
    print("\n🎊 快速开始完成！")
    print("\n📚 更多信息:")
    print("- 详细文档: src/infrastructure/embedding/README.md")
    print("- 完整示例: examples/qdrant_low_config_example.py")
    print("- 集成示例: examples/embedding_integration_example.py")

if __name__ == "__main__":
    asyncio.run(main())