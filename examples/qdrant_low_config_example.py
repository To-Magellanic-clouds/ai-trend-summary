"""
Qdrant低配置运行示例
演示不同的Qdrant连接方式及其优缺点
"""

import asyncio
import logging
from typing import List, Dict, Any
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demo_memory_mode():
    """演示内存模式 - 最低配置"""
    print("=== 内存模式演示 ===")
    
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams, PointStruct
        
        # 内存模式 - 无需任何外部依赖
        client = QdrantClient(":memory:")
        print("✓ 内存模式连接成功")
        
        # 创建集合
        collection_name = "test_memory"
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        print(f"✓ 创建集合: {collection_name}")
        
        # 添加一些测试向量
        points = [
            PointStruct(
                id=1,
                vector=[0.1] * 384,
                payload={"text": "这是第一个测试文档", "category": "test"}
            ),
            PointStruct(
                id=2,
                vector=[0.2] * 384,
                payload={"text": "这是第二个测试文档", "category": "test"}
            )
        ]
        
        client.upsert(collection_name=collection_name, points=points)
        print(f"✓ 添加了 {len(points)} 个向量")
        
        # 搜索测试
        search_result = client.search(
            collection_name=collection_name,
            query_vector=[0.15] * 384,
            limit=2
        )
        
        print(f"✓ 搜索结果: {len(search_result)} 个")
        for result in search_result:
            print(f"  ID: {result.id}, Score: {result.score:.4f}")
        
        # 获取集合信息
        info = client.get_collection(collection_name)
        print(f"✓ 集合信息: {info.points_count} 个点")
        
        return True
        
    except Exception as e:
        print(f"✗ 内存模式失败: {e}")
        return False

def demo_file_mode():
    """演示文件存储模式"""
    print("\n=== 文件存储模式演示 ===")
    
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams, PointStruct
        
        # 文件存储模式 - 数据持久化到本地文件
        storage_path = "./qdrant_local_data"
        client = QdrantClient(path=storage_path)
        print(f"✓ 文件存储模式连接成功，存储路径: {storage_path}")
        
        # 创建集合
        collection_name = "test_file"
        
        # 检查集合是否已存在
        try:
            existing_collections = client.get_collections()
            collection_exists = any(
                col.name == collection_name 
                for col in existing_collections.collections
            )
            
            if not collection_exists:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
                print(f"✓ 创建新集合: {collection_name}")
            else:
                print(f"✓ 使用现有集合: {collection_name}")
                
        except Exception as e:
            print(f"集合操作警告: {e}")
            return False
        
        # 添加测试数据
        points = [
            PointStruct(
                id=10,
                vector=[0.3] * 384,
                payload={"text": "文件存储测试文档1", "mode": "file"}
            ),
            PointStruct(
                id=11,
                vector=[0.4] * 384,
                payload={"text": "文件存储测试文档2", "mode": "file"}
            )
        ]
        
        client.upsert(collection_name=collection_name, points=points)
        print(f"✓ 添加了 {len(points)} 个向量到文件存储")
        
        # 搜索测试
        search_result = client.search(
            collection_name=collection_name,
            query_vector=[0.35] * 384,
            limit=2
        )
        
        print(f"✓ 搜索结果: {len(search_result)} 个")
        for result in search_result:
            print(f"  ID: {result.id}, Score: {result.score:.4f}")
        
        return True
        
    except Exception as e:
        print(f"✗ 文件存储模式失败: {e}")
        return False

def demo_server_mode():
    """演示服务器模式（需要外部Qdrant服务）"""
    print("\n=== 服务器模式演示 ===")
    
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams, PointStruct
        
        # 服务器模式 - 连接到外部Qdrant服务
        client = QdrantClient(url="http://localhost:6333")
        # 或者使用: client = QdrantClient(host="localhost", port=6333)
        
        # 测试连接
        collections = client.get_collections()
        print(f"✓ 服务器模式连接成功，现有集合数: {len(collections.collections)}")
        
        # 创建集合
        collection_name = "test_server"
        
        try:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
            print(f"✓ 创建集合: {collection_name}")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"✓ 集合已存在: {collection_name}")
            else:
                raise e
        
        # 添加测试数据
        points = [
            PointStruct(
                id=20,
                vector=[0.5] * 384,
                payload={"text": "服务器模式测试文档1", "mode": "server"}
            ),
            PointStruct(
                id=21,
                vector=[0.6] * 384,
                payload={"text": "服务器模式测试文档2", "mode": "server"}
            )
        ]
        
        client.upsert(collection_name=collection_name, points=points)
        print(f"✓ 添加了 {len(points)} 个向量到服务器")
        
        # 搜索测试
        search_result = client.search(
            collection_name=collection_name,
            query_vector=[0.55] * 384,
            limit=2
        )
        
        print(f"✓ 搜索结果: {len(search_result)} 个")
        for result in search_result:
            print(f"  ID: {result.id}, Score: {result.score:.4f}")
        
        return True
        
    except Exception as e:
        print(f"✗ 服务器模式失败: {e}")
        print("  提示: 请确保Qdrant服务正在运行")
        print("  启动命令: docker run -p 6333:6333 qdrant/qdrant")
        return False

async def demo_with_embedding_sdk():
    """演示与我们的向量化SDK集成"""
    print("\n=== 与向量化SDK集成演示 ===")
    
    try:
        # 导入我们的SDK
        import sys
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        from src.infrastructure.embedding import (
            EmbeddingSystemConfig,
            EmbeddingManager,
            DocumentInput
        )
        
        # 使用内存模式配置
        config = EmbeddingSystemConfig(
            qdrant_host=":memory:",  # 内存模式
            qdrant_port=None,
        )
        
        manager_config = config.create_manager_config(
            collection_name="sdk_test"
        )
        
        # 创建管理器
        manager = EmbeddingManager(manager_config)
        
        # 初始化
        success = await manager.initialize()
        if not success:
            print("✗ SDK初始化失败")
            return False
        
        print("✓ 向量化SDK初始化成功（内存模式）")
        
        # 添加文档
        documents = [
            DocumentInput(
                id="doc1",
                content="人工智能是计算机科学的一个重要分支",
                metadata={"category": "AI", "language": "zh"}
            ),
            DocumentInput(
                id="doc2", 
                content="机器学习是实现人工智能的重要方法",
                metadata={"category": "ML", "language": "zh"}
            )
        ]
        
        for doc in documents:
            await manager.add_document(doc)
        
        print(f"✓ 添加了 {len(documents)} 个文档")
        
        # 搜索测试
        results = await manager.search_similar_documents("深度学习", top_k=2)
        print(f"✓ 搜索结果: {len(results)} 个")
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. 相似度: {result.score:.4f}")
            print(f"     内容: {result.document.content[:50]}...")
        
        # 关闭连接
        await manager.close()
        print("✓ SDK连接已关闭")
        
        return True
        
    except Exception as e:
        print(f"✗ SDK集成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_comparison():
    """打印各种模式的对比"""
    print("\n" + "="*60)
    print("📊 Qdrant连接模式对比")
    print("="*60)
    
    comparison_data = [
        {
            "模式": "内存模式",
            "连接方式": 'QdrantClient(":memory:")',
            "优点": [
                "无需外部依赖",
                "启动速度快",
                "适合测试和开发",
                "资源占用少"
            ],
            "缺点": [
                "数据不持久化",
                "重启后数据丢失",
                "内存限制",
                "不支持分布式"
            ],
            "适用场景": "开发测试、原型验证、临时计算"
        },
        {
            "模式": "文件存储模式",
            "连接方式": 'QdrantClient(path="./data")',
            "优点": [
                "数据持久化",
                "无需外部服务",
                "简单部署",
                "适合单机应用"
            ],
            "缺点": [
                "性能相对较低",
                "不支持分布式",
                "并发能力有限",
                "扩展性差"
            ],
            "适用场景": "小型应用、单机部署、离线处理"
        },
        {
            "模式": "服务器模式",
            "连接方式": 'QdrantClient(url="http://host:6333")',
            "优点": [
                "高性能",
                "支持分布式",
                "高并发",
                "生产级稳定性"
            ],
            "缺点": [
                "需要外部服务",
                "部署复杂",
                "资源消耗大",
                "网络依赖"
            ],
            "适用场景": "生产环境、大规模应用、高并发场景"
        }
    ]
    
    for mode in comparison_data:
        print(f"\n🔹 {mode['模式']}")
        print(f"   连接方式: {mode['连接方式']}")
        print(f"   ✅ 优点: {', '.join(mode['优点'])}")
        print(f"   ❌ 缺点: {', '.join(mode['缺点'])}")
        print(f"   🎯 适用场景: {mode['适用场景']}")

def print_recommendations():
    """打印使用建议"""
    print("\n" + "="*60)
    print("💡 使用建议")
    print("="*60)
    
    recommendations = [
        {
            "阶段": "开发阶段",
            "推荐": "内存模式",
            "原因": "快速迭代，无需配置外部服务"
        },
        {
            "阶段": "测试阶段", 
            "推荐": "文件存储模式",
            "原因": "数据持久化，便于测试验证"
        },
        {
            "阶段": "生产阶段",
            "推荐": "服务器模式",
            "原因": "高性能，高可用，支持扩展"
        },
        {
            "阶段": "演示/原型",
            "推荐": "内存模式",
            "原因": "简单快速，无需额外配置"
        }
    ]
    
    for rec in recommendations:
        print(f"🔸 {rec['阶段']}: 推荐使用 {rec['推荐']}")
        print(f"   理由: {rec['原因']}")

async def main():
    """主函数"""
    print("🚀 Qdrant低配置运行方式演示")
    print("="*40)
    
    # 演示各种连接模式
    memory_ok = demo_memory_mode()
    file_ok = demo_file_mode()
    server_ok = demo_server_mode()
    
    # 演示SDK集成
    if memory_ok:
        sdk_ok = await demo_with_embedding_sdk()
    
    # 打印对比和建议
    print_comparison()
    print_recommendations()
    
    print("\n" + "="*60)
    print("✅ 演示完成！")
    print("="*60)
    
    print("\n📋 快速开始建议:")
    print("1. 开发测试: 使用内存模式 QdrantClient(':memory:')")
    print("2. 本地应用: 使用文件模式 QdrantClient(path='./data')")
    print("3. 生产环境: 使用服务器模式 QdrantClient(url='http://host:6333')")
    
    print("\n🔧 安装命令:")
    print("pip install qdrant-client sentence-transformers")
    
    print("\n🐳 Docker启动Qdrant服务器:")
    print("docker run -p 6333:6333 qdrant/qdrant")

if __name__ == "__main__":
    asyncio.run(main())