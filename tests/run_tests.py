#!/usr/bin/env python3
"""
PKM Copilot 测试运行器
用于验证模块化架构的测试结构
"""

import sys
import os
import asyncio
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

async def run_basic_tests():
    """运行基础测试验证架构"""
    print("🔍 正在验证PKM Copilot测试结构...")
    
    try:
        # 测试导入
        from src.core.models import Article, VectorData, DataSource
        from src.modules.knowbase.core import KnowBaseCore
        from src.modules.vecembed.core import VecEmbedCore
        
        print("✅ 核心模块导入成功")
        
        # 测试数据模型
        article = Article(
            id="test-article-1",
            title="测试文章",
            content="这是一个测试内容",
            url="https://example.com/test"
        )
        print(f"✅ 文章模型验证: {article.title}")
        
        # 测试数据源模型
        source = DataSource(
            name="测试RSS源",
            type="rss",
            config={"url": "https://example.com/rss"},
            is_active=True
        )
        print(f"✅ 数据源模型验证: {source.name}")
        
        # 测试向量数据模型
        vector = VectorData(
            article_id="test-article-1",
            content="测试内容",
            embedding=[0.1, 0.2, 0.3],
            embedding_model="test-model"
        )
        print(f"✅ 向量数据模型验证: {vector.content}")
        
        # 测试模块初始化
        knowbase = KnowBaseCore()
        vecembed = VecEmbedCore()
        
        print("✅ KnowBase模块初始化成功")
        print("✅ VecEmbed模块初始化成功")
        
        # 测试配置系统
        from src.core.config import get_config
        config = get_config()
        print("✅ 配置系统验证成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(run_basic_tests())
    if success:
        print("\n🎉 PKM Copilot测试结构验证通过！")
        sys.exit(0)
    else:
        print("\n💥 PKM Copilot测试结构验证失败！")
        sys.exit(1)