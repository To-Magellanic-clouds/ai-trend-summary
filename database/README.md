# 数据库设计文档

## 概述
本文档描述了AI趋势总结项目的PostgreSQL数据库设计，支持信息收集、分析、筛选和总结的完整工作流。

## 设计原则
1. **可扩展性**: 支持多种数据源和内容类型
2. **灵活性**: 使用JSONB存储动态配置和元数据
3. **性能优化**: 合理的索引设计和分区策略
4. **数据完整性**: 外键约束和数据验证
5. **可追溯性**: 完整的处理状态跟踪

## 表结构设计

### 1. 数据源管理 (Data Source Management)
- `data_sources`: 数据源配置表，支持多种平台的爬取配置

### 2. 内容存储 (Content Storage)
- `articles`: 文章主表，存储基本元数据和评分
- `article_sections`: 文章内容片段，支持结构化内容存储

### 3. 分类系统 (Classification System)
- `domains`: 领域分类，支持层级结构
- `article_types`: 文章类型分类
- `article_classifications`: 文章分类关联表

### 4. 概念和关键词 (Concepts & Keywords)
- `concepts`: 概念/关键词主表，支持别名和类型
- `article_concepts`: 文章-概念关联，包含相关性评分

### 5. 关系和知识图谱 (Relations & Knowledge Graph)
- `concept_relations`: 概念间关系
- `article_relations`: 文章间关系

### 6. 处理工作流 (Processing Workflow)
- `processing_status`: 处理状态跟踪
- `processing_queue`: 异步任务队列

### 7. 用户和个性化 (Users & Personalization)
- `users`: 用户表
- `user_subscriptions`: 用户订阅偏好
- `user_feedback`: 用户反馈数据

### 8. 报告生成 (Report Generation)
- `report_templates`: 报告模板
- `generated_reports`: 生成的报告记录

## 核心特性

### 评分系统
- **质量评分** (quality_score): 基于内容质量的0-1评分
- **重要性评分** (importance_score): 基于影响力的0-1评分  
- **热度评分** (trending_score): 基于时效性和关注度的评分
- **相关性评分** (relevance_score): 概念与文章的相关程度

### 处理工作流
1. **信息收集**: data_sources → articles
2. **预处理**: article_sections
3. **分析**: concepts, article_concepts
4. **分类**: article_classifications
5. **关系抽取**: concept_relations, article_relations
6. **状态跟踪**: processing_status, processing_queue

### 知识图谱支持
- 概念实体和关系的完整建模
- 支持多种关系类型 (based_on, applies_to, competes_with等)
- 关系强度和证据计数

### 个性化功能
- 用户订阅和偏好设置
- 反馈收集和学习
- 自定义报告模板

## 索引策略
- 时间序列查询优化 (published_at, created_at)
- 评分排序优化 (quality_score, trending_score)
- 关联查询优化 (外键字段)
- 全文搜索支持 (可扩展GIN索引)

## 扩展建议
1. **分区策略**: 按时间分区articles表
2. **全文搜索**: 添加PostgreSQL全文搜索索引
3. **缓存层**: Redis缓存热点数据
4. **归档策略**: 历史数据归档机制

## 与其他存储的集成
- **MongoDB**: 存储原始内容和报告内容 (raw_content_mongo_id)
- **向量数据库**: 文章向量化表示，支持语义搜索
- **文件系统**: 生成的报告文件存储 (file_path)