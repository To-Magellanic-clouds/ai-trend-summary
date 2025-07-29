# 数据库执行指南

## 问题分析
你遇到的执行错误主要是因为：
1. `schema_v2.sql` 依赖一些在 `schema.sql` 中定义的表（如 `users`, `domains`, `concepts` 等）
2. `schema_v2.sql` 使用了自定义枚举类型，需要先创建
3. `schema_v2.sql` 中有索引语法错误（第242-243行）
4. 两个schema文件不能同时执行，需要选择其中一个

## 推荐执行步骤

### 方案一：使用基础版本 (schema.sql) - 简单稳定
```bash
# 1. 连接到PostgreSQL
psql -U your_username -d your_database

# 2. 执行基础schema
\i database/schema.sql

# 3. 如果需要视图和索引，执行迁移脚本
\i database/migrations/001_initial_schema.sql
```

### 方案二：使用增强版本 (schema_v2.sql) - 功能完整，推荐
```bash
# 1. 连接到PostgreSQL
psql -U your_username -d your_database

# 2. 先执行初始化脚本（解决依赖问题）
\i database/setup_database.sql

# 3. 执行增强版schema（跳过有问题的索引）
\i database/schema_v2.sql

# 4. 修复索引问题
\i database/fix_schema_v2_indexes.sql
```

### 方案三：从零开始创建数据库 - 最安全
```bash
# 1. 创建新数据库
createdb ai_trend_summary

# 2. 连接到新数据库
psql -U your_username -d ai_trend_summary

# 3. 执行完整初始化
\i database/setup_database.sql
\i database/schema_v2.sql
\i database/fix_schema_v2_indexes.sql
```

## 常见错误解决

### 错误1: 枚举类型不存在
```
ERROR: type "acquisition_method" does not exist
ERROR: type "processing_stage" does not exist
```
**解决**: 先执行 `setup_database.sql`

### 错误2: 表不存在
```
ERROR: relation "users" does not exist
ERROR: relation "domains" does not exist
ERROR: relation "concepts" does not exist
```
**解决**: 确保先执行了 `setup_database.sql`

### 错误3: 索引语法错误
```
ERROR: syntax error at or near "INDEX"
```
**解决**: 这是 `schema_v2.sql` 第242-243行的问题，执行 `fix_schema_v2_indexes.sql` 修复

### 错误4: 扩展不存在
```
ERROR: extension "uuid-ossp" does not exist
ERROR: extension "pg_trgm" does not exist
```
**解决**: 确保有创建扩展的权限，或联系数据库管理员

### 错误5: 权限不足
```
ERROR: permission denied to create extension
ERROR: permission denied to create database
```
**解决**: 使用超级用户权限或请求管理员协助

### 错误6: 外键约束错误
```
ERROR: insert or update on table violates foreign key constraint
```
**解决**: 确保按正确顺序执行脚本，先创建被引用的表

## 版本选择建议

### 选择 schema.sql 如果：
- ✅ 你只需要基础功能
- ✅ 不需要重复检测
- ✅ 不需要多种数据获取方式
- ✅ 想要更简单的表结构
- ✅ 快速开始，稳定性优先

### 选择 schema_v2.sql 如果：
- ✅ 需要重复检测功能
- ✅ 需要支持多种数据获取方式（批量爬取、流式爬取、用户导入等）
- ✅ 需要更完善的状态管理
- ✅ 需要内容指纹和相似度检测
- ✅ 计划长期使用和扩展
- ✅ 需要处理大量数据

## 执行验证

### 检查安装是否成功
```sql
-- 检查表是否创建成功
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- 检查枚举类型
SELECT typname FROM pg_type WHERE typtype = 'e';

-- 检查扩展
SELECT extname FROM pg_extension;

-- 检查索引
SELECT indexname, tablename FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename, indexname;
```

### 测试基本功能
```sql
-- 插入测试数据源
INSERT INTO data_sources (name, type, acquisition_method, base_url) 
VALUES ('test_source', 'blog', 'batch_crawl', 'https://example.com');

-- 检查是否成功
SELECT * FROM data_sources;
```

## 故障排除

### 如果执行中断了怎么办？
1. 检查哪些表已经创建：`\dt`
2. 删除已创建的表：`DROP TABLE table_name CASCADE;`
3. 重新开始执行

### 如何完全重置数据库？
```sql
-- 删除所有表（谨慎操作！）
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO your_username;
GRANT ALL ON SCHEMA public TO public;
```

### 如何备份当前状态？
```bash
# 备份整个数据库
pg_dump -U your_username your_database > backup.sql

# 只备份表结构
pg_dump -U your_username -s your_database > schema_backup.sql
```

## 下一步
安装完成后，你可以：
1. 运行 `src/processing/main.py` 开始处理文章
2. 查看 `database/queries/examples.sql` 了解常用查询
3. 根据需要调整配置文件
4. 查看 `database/deduplication_design.md` 了解重复检测机制（如果使用schema_v2）

## 性能优化建议
- 如果数据量大，考虑对 `articles` 表按时间分区
- 定期运行 `VACUUM ANALYZE` 更新统计信息
- 监控慢查询并添加必要的索引