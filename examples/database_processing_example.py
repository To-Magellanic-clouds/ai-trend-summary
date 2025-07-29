"""
数据库处理示例脚本
演示如何使用数据库集成的文章处理功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.processing.main import ArticleProcessingTool
from src.processing.database_config import DatabaseConfigTemplates
from src.processing.database_processor import AcquisitionMethod


def setup_environment():
    """设置环境变量"""
    # 设置数据库连接参数（如果未设置）
    if not os.getenv('DB_HOST'):
        os.environ['DB_HOST'] = 'localhost'
    if not os.getenv('DB_PORT'):
        os.environ['DB_PORT'] = '5432'
    if not os.getenv('DB_NAME'):
        os.environ['DB_NAME'] = 'ai_trend_summary'
    if not os.getenv('DB_USER'):
        os.environ['DB_USER'] = 'postgres'
    if not os.getenv('DB_PASSWORD'):
        os.environ['DB_PASSWORD'] = 'your_password'


def example_file_import():
    """示例：文件导入处理"""
    print("=== 文件导入处理示例 ===")
    
    tool = ArticleProcessingTool()
    
    # 创建数据库配置
    tool.create_database_configs()
    
    # 使用文件导入配置处理
    try:
        output_path = tool.process_with_database(
            config_name="db_file_import",
            input_path="result/Huggingface/Blog",
            output_path="results/db_file_import_example.json"
        )
        
        if output_path:
            print(f"文件导入处理完成: {output_path}")
        else:
            print("文件导入处理失败")
            
    except Exception as e:
        print(f"处理过程中出错: {e}")


def example_batch_crawl():
    """示例：批量爬取处理"""
    print("\n=== 批量爬取处理示例 ===")
    
    tool = ArticleProcessingTool()
    
    try:
        output_path = tool.process_with_database(
            config_name="db_batch_crawl",
            input_path="data/crawled",
            output_path="results/db_batch_crawl_example.json"
        )
        
        if output_path:
            print(f"批量爬取处理完成: {output_path}")
        else:
            print("批量爬取处理失败")
            
    except Exception as e:
        print(f"处理过程中出错: {e}")


def example_custom_config():
    """示例：自定义数据库配置"""
    print("\n=== 自定义数据库配置示例 ===")
    
    # 创建自定义配置
    custom_config = DatabaseConfigTemplates.create_custom_database_config(
        data_source_name="custom_example",
        acquisition_method=AcquisitionMethod.USER_IMPORT,
        input_path="your_input_directory",
        processor_type="full",
        enable_concept_extraction=True,
        enable_summary_generation=True,
        enable_classification=True,
        enable_quality_assessment=True,
        enable_deduplication=True,
        max_files=50
    )
    
    print("自定义配置创建完成:")
    print(f"  - 数据源: {custom_config.data_source_name}")
    print(f"  - 获取方式: {custom_config.acquisition_method}")
    print(f"  - 处理器类型: {custom_config.processor_type}")
    print(f"  - 最大文件数: {custom_config.max_files}")


def check_database_connection():
    """检查数据库连接"""
    print("\n=== 检查数据库连接 ===")
    
    try:
        from src.infrastructure.utils.db.PostgresConnector import PostgresConnector
        
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
            if len(tables) >= 3:
                print("✓ 数据库表结构正常")
            else:
                print("⚠ 数据库表结构不完整，请先执行数据库迁移")
            
            cursor.close()
            connector.close_connection()
        else:
            print("✗ 数据库连接失败")
            
    except Exception as e:
        print(f"✗ 数据库连接检查失败: {e}")
        print("请检查数据库配置和连接参数")


def main():
    """主函数"""
    print("数据库处理示例脚本")
    print("=" * 50)
    
    # 设置环境
    setup_environment()
    
    # 检查数据库连接
    check_database_connection()
    
    # 运行示例
    try:
        # 示例1: 文件导入
        example_file_import()
        
        # 示例2: 批量爬取
        # example_batch_crawl()
        
        # 示例3: 自定义配置
        example_custom_config()
        
    except KeyboardInterrupt:
        print("\n用户中断执行")
    except Exception as e:
        print(f"\n执行过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()