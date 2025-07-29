"""
简单的导入测试脚本
验证数据库处理器的导入是否正常
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试各个模块的导入"""
    print("测试模块导入...")
    
    try:
        print("1. 测试 article_processor 导入...")
        from src.processing.article_processor import BaseArticleProcessor, ProcessingResult, ProcessingStatus
        print("   ✓ article_processor 导入成功")
    except Exception as e:
        print(f"   ✗ article_processor 导入失败: {e}")
        return False
    
    try:
        print("2. 测试 DatabaseManager 导入...")
        from src.infrastructure.utils.db.DatabaseManager import DatabaseManager, AcquisitionMethod, ProcessingStage
        print("   ✓ DatabaseManager 导入成功")
    except Exception as e:
        print(f"   ✗ DatabaseManager 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        print("3. 测试 database_processor 导入...")
        from src.processing.database_processor import DatabaseIntegratedProcessor, DatabaseProcessorFactory
        print("   ✓ database_processor 导入成功")
    except Exception as e:
        print(f"   ✗ database_processor 导入失败: {e}")
        return False
    
    try:
        print("4. 测试 main 模块导入...")
        from src.processing.main import ArticleProcessingTool
        print("   ✓ main 模块导入成功")
    except Exception as e:
        print(f"   ✗ main 模块导入失败: {e}")
        return False
    
    return True

def test_basic_functionality():
    """测试基本功能"""
    try:
        print("\n测试基本功能...")
        from src.processing.main import ArticleProcessingTool
        
        tool = ArticleProcessingTool()
        print("✓ ArticleProcessingTool 实例化成功")
        
        # 测试配置列表
        tool.list_configs()
        print("✓ 配置列表功能正常")
        
        return True
    except Exception as e:
        print(f"✗ 基本功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("数据库处理器导入测试")
    print("=" * 50)
    
    # 测试导入
    if not test_imports():
        print("\n导入测试失败")
        return
    
    # 测试基本功能
    if not test_basic_functionality():
        print("\n基本功能测试失败")
        return
    
    print("\n" + "=" * 50)
    print("✓ 所有测试通过！导入问题已修复")

if __name__ == "__main__":
    main()