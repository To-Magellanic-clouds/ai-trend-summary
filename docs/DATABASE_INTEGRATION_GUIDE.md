# 数据库集成使用指南

本指南介绍如何使用AI趋势总结项目的数据库集成功能，将文章处理过程和结果存储到PostgreSQL数据库中。

## 前置条件

### 1. 数据库准备

确保PostgreSQL数据库已安装并运行，且已创建必要的表结构：

```bash
# 1. 创建数据库
createdb ai_trend_summary

# 2. 执行数据库初始化脚本
psql -d ai_trend_summary -f database/setup_database.sql

# 3. 执行主表结构（选择其一）
# 基础版本（推荐新用户）
psql -d ai_trend_summary -f database/schema.sql

# 或增强版本（功能更完整）
psql -d ai_trend_summary -f database/schema_v2.sql
psql -d ai_trend_summary -f database/fix_schema_v2_indexes.sql
```

### 2. 环境变量配置

设置数据库连接参数：

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=ai_trend_summary
export DB_USER=postgres
export DB_PASSWORD=your_password
```

或在`.env`文件中配置：

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_trend_summary
DB_USER=postgres
DB_PASSWORD=your_password
```

## 快速开始

### 1. 创建数据库配置

```bash
# 创建数据库配置文件
python src/processing/main.py init-db-configs
```

这将创建以下配置文件：
- `config/db_file_import.json` - 文件导入配置
- `config/db_batch_crawl.json` - 批量爬取配置
- `config/db_stream_processing.json` - 流式处理配置
- `config/db_api_sync.json` - API同步配置
- `config/db_manual_entry.json` - 手动录入配置

### 2. 使用数据库配置处理文章

```bash
# 使用文件导入配置处理
python src/processing/main.py database db_file_import --input "result/Huggingface/Blog" --output "results/db_import.json"

# 使用批量爬取配置处理
python src/processing/main.py database db_batch_crawl --input "data/crawled" --output "results/db_crawl.json"
```

## 配置详解

### 数据库配置模板

项目提供了5种预配置的数据库处理模板：

#### 1. 文件导入配置 (`db_file_import`)
- **用途**: 处理本地文件导入
- **获取方式**: `USER_IMPORT`
- **特点**: 适合处理已下载的文章文件

#### 2. 批量爬取配置 (`db_batch_crawl`)
- **用途**: 处理批量爬取的数据
- **获取方式**: `BATCH_CRAWL`
- **特点**: 启用去重功能，适合大批量数据

#### 3. 流式处理配置 (`db_stream_processing`)
- **用途**: 实时流式数据处理
- **获取方式**: `STREAM_CRAWL`
- **特点**: 快速处理，跳过摘要生成

#### 4. API同步配置 (`db_api_sync`)
- **用途**: 通过API同步的数据
- **获取方式**: `API_SYNC`
- **特点**: 标准处理流程

#### 5. 手动录入配置 (`db_manual_entry`)
- **用途**: 手动录入的文章
- **获取方式**: `MANUAL_ENTRY`
- **特点**: 完整处理，不启用去重

### 自定义配置

```python
from src.processing.database_config import DatabaseConfigTemplates
from src.processing.database_processor import AcquisitionMethod

# 创建自定义配置
custom_config = DatabaseConfigTemplates.create_custom_database_config(
    data_source_name="my_custom_source",
    acquisition_method=AcquisitionMethod.USER_IMPORT,
    input_path="my_input_directory",
    processor_type="full",
    enable_concept_extraction=True,
    enable_summary_generation=True,
    enable_classification=True,
    enable_quality_assessment=True,
    enable_deduplication=True,
    max_files=100
)
```

## 编程接口

### 基本使用

```python
from src.processing.main import ArticleProcessingTool

# 创建处理工具
tool = ArticleProcessingTool()

# 使用数据库配置处理
output_path = tool.process_with_database(
    config_name="db_file_import",
    input_path="your_input_path",
    output_path="your_output_path"
)
```

### 直接使用数据库处理器

```python
from src.processing.database_processor import DatabaseProcessorFactory, AcquisitionMethod

# 创建数据库处理器
processor = DatabaseProcessorFactory.create_processor(
    processor_type="standard",
    data_source_name="my_source",
    acquisition_method=AcquisitionMethod.USER_IMPORT
)

# 处理单个文章
result = processor.process_article("article_content", "article_url")

# 获取处理统计
stats = processor.get_processing_stats()
```

## 数据库存储内容

### 存储的数据包括：

1. **数据源信息** (`data_sources`)
   - 数据源名称、描述
   - 获取方式、配置参数
   - 创建和更新时间

2. **文章内容** (`articles`)
   - 原始内容、URL、标题
   - 内容指纹、重复检测
   - 质量评分、重要性评分

3. **处理状态** (`processing_status`)
   - 处理阶段、状态
   - 开始和完成时间
   - 错误信息

4. **处理结果**
   - 概念提取结果
   - 分类结果
   - 摘要生成结果
   - 质量评估结果

### 查询示例

```sql
-- 查看处理统计
SELECT 
    ds.name as data_source,
    COUNT(*) as total_articles,
    COUNT(CASE WHEN ps.status = 'completed' THEN 1 END) as completed,
    COUNT(CASE WHEN ps.status = 'failed' THEN 1 END) as failed
FROM articles a
JOIN data_sources ds ON a.data_source_id = ds.id
LEFT JOIN processing_status ps ON a.id = ps.article_id
GROUP BY ds.name;

-- 查看最近处理的文章
SELECT 
    a.title,
    a.url,
    ps.status,
    ps.completed_at
FROM articles a
JOIN processing_status ps ON a.id = ps.article_id
ORDER BY ps.completed_at DESC
LIMIT 10;
```

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库服务是否运行
   - 验证连接参数是否正确
   - 确认防火墙设置

2. **表不存在错误**
   - 确保已执行数据库迁移脚本
   - 检查表结构是否完整

3. **权限错误**
   - 确认数据库用户有足够权限
   - 检查表的读写权限

4. **处理失败**
   - 查看错误日志
   - 检查输入数据格式
   - 验证LLM配置

### 调试方法

```python
# 检查数据库连接
from src.infrastructure.utils.db.PostgresConnector import PostgresConnector

connector = PostgresConnector()
connection = connector.get_connection()
if connection:
    print("数据库连接成功")
else:
    print("数据库连接失败")
```

## 性能优化

### 批量处理优化

1. **调整批次大小**
   ```python
   config.max_files = 100  # 根据系统性能调整
   ```

2. **启用并行处理**
   ```python
   config.enable_parallel = True
   config.max_workers = 4
   ```

3. **优化数据库连接**
   ```python
   # 使用连接池
   config.db_pool_size = 10
   config.db_max_overflow = 20
   ```

### 监控和日志

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.INFO)

# 监控处理进度
config.enable_progress = True
```

## 示例脚本

运行完整示例：

```bash
python examples/database_processing_example.py
```

这个示例脚本演示了：
- 数据库连接检查
- 配置文件创建
- 文章处理流程
- 结果查询和统计

## 下一步

1. 根据需要调整配置参数
2. 集成到现有工作流程
3. 设置定期处理任务
4. 配置监控和告警
5. 优化性能参数