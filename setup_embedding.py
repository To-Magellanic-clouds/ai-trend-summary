#!/usr/bin/env python3
"""
向量化SDK快速启动脚本
用于快速设置和测试向量化环境
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('embedding_setup.log')
        ]
    )

def check_dependencies():
    """检查依赖包"""
    print("检查依赖包...")
    
    required_packages = [
        'qdrant-client',
        'sentence-transformers', 
        'torch',
        'transformers',
        'langchain'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (缺失)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n缺失的包: {', '.join(missing_packages)}")
        print("请运行: pip install " + " ".join(missing_packages))
        return False
    
    print("✓ 所有依赖包已安装")
    return True

def check_qdrant_connection():
    """检查Qdrant连接"""
    print("\n检查Qdrant连接...")
    
    try:
        from qdrant_client import QdrantClient
        
        # 尝试连接本地Qdrant
        client = QdrantClient(host="localhost", port=6333)
        collections = client.get_collections()
        print("✓ Qdrant连接成功")
        print(f"  现有集合数量: {len(collections.collections)}")
        return True
        
    except Exception as e:
        print(f"✗ Qdrant连接失败: {e}")
        print("\n请确保Qdrant服务正在运行:")
        print("  Docker方式: docker run -p 6333:6333 qdrant/qdrant")
        print("  或访问: https://qdrant.tech/documentation/quick-start/")
        return False

def setup_environment():
    """设置环境配置"""
    print("\n设置环境配置...")
    
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        print("复制环境配置模板...")
        with open(env_example, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ 已创建 {env_file}")
        print("  请根据需要修改配置")
    elif env_file.exists():
        print(f"✓ 环境配置文件已存在: {env_file}")
    else:
        print("✗ 未找到环境配置模板")

async def test_embedding_sdk():
    """测试向量化SDK"""
    print("\n测试向量化SDK...")
    
    try:
        # 导入SDK
        from src.infrastructure.embedding import (
            EmbeddingSystemConfig,
            EmbeddingManager,
            DocumentInput
        )
        
        print("✓ SDK导入成功")
        
        # 创建配置
        config = EmbeddingSystemConfig.from_env()
        manager_config = config.create_manager_config(
            collection_name="test_collection"
        )
        
        # 创建管理器
        manager = EmbeddingManager(manager_config)
        
        # 初始化
        success = await manager.initialize()
        if not success:
            print("✗ 管理器初始化失败")
            return False
        
        print("✓ 管理器初始化成功")
        
        # 测试文档添加
        test_doc = DocumentInput(
            id="test_001",
            content="这是一个测试文档，用于验证向量化SDK的功能。",
            metadata={"type": "test", "created_at": "2024-01-01"}
        )
        
        success = await manager.add_document(test_doc)
        if success:
            print("✓ 文档添加成功")
        else:
            print("✗ 文档添加失败")
            return False
        
        # 测试搜索
        results = await manager.search_similar_documents("测试文档", top_k=1)
        if results:
            print(f"✓ 搜索成功，找到 {len(results)} 个结果")
            print(f"  相似度: {results[0].score:.4f}")
        else:
            print("✗ 搜索失败")
            return False
        
        # 清理测试数据
        await manager.delete_document("test_001")
        print("✓ 测试数据清理完成")
        
        # 关闭连接
        await manager.close()
        print("✓ 连接已关闭")
        
        return True
        
    except Exception as e:
        print(f"✗ SDK测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_integration_example():
    """运行集成示例"""
    print("\n运行集成示例...")
    
    try:
        # 检查示例文件
        example_file = project_root / "examples" / "embedding_integration_example.py"
        if not example_file.exists():
            print(f"✗ 示例文件不存在: {example_file}")
            return False
        
        print("✓ 找到集成示例文件")
        
        # 导入并运行示例
        sys.path.insert(0, str(project_root / "examples"))
        from embedding_integration_example import demo_integration
        
        await demo_integration()
        return True
        
    except Exception as e:
        print(f"✗ 集成示例运行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_next_steps():
    """打印后续步骤"""
    print("\n" + "="*50)
    print("🎉 向量化SDK设置完成！")
    print("="*50)
    
    print("\n📋 后续步骤:")
    print("1. 根据需要修改 .env 配置文件")
    print("2. 查看 src/infrastructure/embedding/README.md 了解详细用法")
    print("3. 运行 examples/embedding_integration_example.py 查看集成示例")
    print("4. 在项目中导入并使用向量化SDK:")
    print("   from src.infrastructure.embedding import EmbeddingManager")
    
    print("\n📚 文档位置:")
    print("- README: src/infrastructure/embedding/README.md")
    print("- 配置示例: .env.example")
    print("- 集成示例: examples/embedding_integration_example.py")
    print("- 测试文件: src/infrastructure/embedding/test_embedding.py")
    
    print("\n🔧 常用命令:")
    print("- 启动Qdrant: docker run -p 6333:6333 qdrant/qdrant")
    print("- 运行测试: python -m pytest src/infrastructure/embedding/test_embedding.py")
    print("- 查看日志: tail -f embedding_setup.log")

async def main():
    """主函数"""
    print("🚀 向量化SDK快速启动")
    print("="*30)
    
    setup_logging()
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请安装缺失的包后重试")
        return
    
    # 检查Qdrant连接
    qdrant_ok = check_qdrant_connection()
    
    # 设置环境
    setup_environment()
    
    if qdrant_ok:
        # 测试SDK
        sdk_ok = await test_embedding_sdk()
        
        if sdk_ok:
            # 运行集成示例
            await run_integration_example()
    
    # 打印后续步骤
    print_next_steps()

if __name__ == "__main__":
    asyncio.run(main())