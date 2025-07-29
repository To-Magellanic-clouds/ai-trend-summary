"""
简化的数据库处理测试脚本
避免复杂的依赖导入问题
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 设置环境变量（如果需要）
os.environ.setdefault('DB_HOST', 'localhost')
os.environ.setdefault('DB_PORT', '5432')
os.environ.setdefault('DB_USER', 'ai_trend_summary')
os.environ.setdefault('DB_DB_NAME', 'postgres')
os.environ.setdefault('DB_PASSWORD', 'your_password')

def test_database_connection():
    """测试数据库连接"""
    try:
        from src.infrastructure.utils.db.PostgresConnector import PostgresConnector
        
        print("测试数据库连接...")
        connector = PostgresConnector()
        connection = connector.get_connection()
        
        if connection:
            print("✓ 数据库连接成功")
            
            # 检查表是否存在
            cursor = connection.cursor()
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('data_sources', 'articles', 'processing_status')
            """)
            
            tables = cursor.fetchall()
            print(f"找到 {len(tables)} 个必需的表")
            
            if len(tables) >= 3:
                print("✓ 数据库表结构正常")
                return True
            else:
                print("⚠ 数据库表结构不完整，请先执行数据库迁移")
                return False
            
        else:
            print("✗ 数据库连接失败")
            return False
            
    except Exception as e:
        print(f"✗ 数据库连接检查失败: {e}")
        return False

def test_database_manager():
    """测试数据库管理器"""
    try:
        from src.infrastructure.utils.db.DatabaseManager import DatabaseManager, AcquisitionMethod
        
        print("\n测试数据库管理器...")
        db_manager = DatabaseManager()
        
        # 创建测试数据源
        source_id = db_manager.create_data_source(
            name="test_source",
            source_type="test",
            acquisition_method=AcquisitionMethod.USER_IMPORT,
            description="测试数据源"
        )
        
        if source_id:
            print(f"✓ 数据源创建成功 (ID: {source_id})")
            
            # 创建测试文章
            article_id = db_manager.create_article(
                title="测试文章",
                source_id=source_id,
                acquisition_method=AcquisitionMethod.USER_IMPORT,
                url="http://test.com/article",
                content="这是一篇测试文章的内容",
                external_id="test_001"
            )
            
            if article_id:
                print(f"✓ 文章创建成功 (ID: {article_id})")
                
                # 获取统计信息
                stats = db_manager.get_processing_statistics()
                if stats:
                    print(f"✓ 统计信息获取成功: {stats.get('overall', {})}")
                
                return True
            else:
                print("✗ 文章创建失败")
                return False
        else:
            print("✗ 数据源创建失败")
            return False
            
    except Exception as e:
        print(f"✗ 数据库管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_processing():
    """测试简单的处理功能"""
    try:
        from src.processing.database_processor import DatabaseProcessorFactory, AcquisitionMethod
        
        print("\n测试数据库处理器...")
        
        # 创建处理器
        processor = DatabaseProcessorFactory.create_processor(
            processor_type="basic",
            data_source_name="test_processing",
            acquisition_method=AcquisitionMethod.USER_IMPORT
        )
        
        print("✓ 数据库处理器创建成功")
        
        # 模拟文章数据
        test_article = {
            'title': '测试文章标题',
            'url': 'http://test.com/test-article',
            'content': '这是一篇用于测试数据库集成功能的文章内容。',
            'author': '测试作者',
            'external_id': 'test_article_001'
        }
        
        # 处理文章
        result = processor.process_article(test_article)
        
        if result:
            print(f"✓ 文章处理成功: {result.title}")
            print(f"  - 状态: {result.status}")
            print(f"  - 数据库ID: {result.metadata.get('database_article_id', 'N/A')}")
            return True
        else:
            print("✗ 文章处理失败")
            return False
            
    except Exception as e:
        print(f"✗ 处理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("数据库集成功能测试")
    print("=" * 50)
    
    # 测试数据库连接
    if not test_database_connection():
        print("\n数据库连接失败，请检查配置")
        return
    
    # 测试数据库管理器
    if not test_database_manager():
        print("\n数据库管理器测试失败")
        return
    
    # 测试处理器
    if not test_simple_processing():
        print("\n处理器测试失败")
        return
    
    print("\n" + "=" * 50)
    print("✓ 所有测试通过！数据库集成功能正常")

if __name__ == "__main__":
    main()