-- 数据库初始化脚本
-- 执行顺序：先执行此文件，再根据需要选择schema版本

-- 1. 创建数据库（如果需要）
-- CREATE DATABASE ai_trend_summary;
-- \c ai_trend_summary;

-- 2. 创建必要的扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- 用于模糊匹配
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- 用于复合索引优化

-- 3. 创建基础枚举类型（schema_v2需要）
DO $$ 
BEGIN
    -- 检查枚举类型是否存在，不存在则创建
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'acquisition_method') THEN
        CREATE TYPE acquisition_method AS ENUM (
            'batch_crawl',      -- 批量爬取
            'stream_crawl',     -- 实时流爬取  
            'user_import',      -- 用户导入
            'api_sync',         -- API同步
            'manual_entry'      -- 手动录入
        );
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'processing_stage') THEN
        CREATE TYPE processing_stage AS ENUM (
            'ingested',         -- 已摄入
            'deduplicated',     -- 已去重
            'preprocessed',     -- 已预处理
            'content_extracted', -- 内容提取完成
            'concepts_extracted', -- 概念提取完成
            'classified',       -- 已分类
            'relations_extracted', -- 关系提取完成
            'summarized',       -- 已总结
            'quality_assessed', -- 质量评估完成
            'indexed',          -- 已索引
            'completed'         -- 完全处理完成
        );
    END IF;
END $$;

-- 4. 创建基础用户表（schema_v2需要引用）
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    full_name VARCHAR(200),
    preferences JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 创建基础的domains表（如果schema.sql中有定义）
CREATE TABLE IF NOT EXISTS domains (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    parent_id INTEGER REFERENCES domains(id),
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. 创建基础的article_types表
CREATE TABLE IF NOT EXISTS article_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. 创建基础的concepts表
CREATE TABLE IF NOT EXISTS concepts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    normalized_name VARCHAR(200) NOT NULL,
    type VARCHAR(50),
    description TEXT,
    aliases JSONB,
    frequency INTEGER DEFAULT 1,
    importance_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(normalized_name, type)
);

-- 提示信息
SELECT 'Database setup completed. Now you can run either schema.sql or schema_v2.sql' as message;