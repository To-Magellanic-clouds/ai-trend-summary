-- 数据库迁移脚本 - 版本 1.0.0
-- 创建AI趋势总结项目的初始表结构

-- 检查并创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 执行主要的表结构创建
\i schema.sql

-- 创建一些有用的视图
CREATE OR REPLACE VIEW v_article_summary AS
SELECT 
    a.id,
    a.title,
    a.url,
    a.author,
    a.published_at,
    ds.name as source_name,
    a.quality_score,
    a.importance_score,
    a.trending_score,
    array_agg(DISTINCT d.name) as domains,
    array_agg(DISTINCT at.name) as article_types,
    array_agg(DISTINCT c.name) as concepts
FROM articles a
LEFT JOIN data_sources ds ON a.source_id = ds.id
LEFT JOIN article_classifications ac ON a.id = ac.article_id
LEFT JOIN domains d ON ac.domain_id = d.id
LEFT JOIN article_types at ON ac.article_type_id = at.id
LEFT JOIN article_concepts arc ON a.id = arc.article_id
LEFT JOIN concepts c ON arc.concept_id = c.id
GROUP BY a.id, ds.name;

-- 创建热门文章视图
CREATE OR REPLACE VIEW v_trending_articles AS
SELECT 
    a.*,
    ds.name as source_name,
    COUNT(uf.id) as feedback_count,
    AVG(uf.rating) as avg_rating
FROM articles a
LEFT JOIN data_sources ds ON a.source_id = ds.id
LEFT JOIN user_feedback uf ON a.id = uf.article_id
WHERE a.published_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY a.id, ds.name
ORDER BY a.trending_score DESC, feedback_count DESC
LIMIT 100;

-- 创建概念热度视图
CREATE OR REPLACE VIEW v_concept_trends AS
SELECT 
    c.id,
    c.name,
    c.type,
    c.frequency,
    COUNT(ac.article_id) as recent_mentions,
    AVG(ac.relevance_score) as avg_relevance,
    MAX(a.published_at) as last_mentioned
FROM concepts c
LEFT JOIN article_concepts ac ON c.id = ac.concept_id
LEFT JOIN articles a ON ac.article_id = a.id
WHERE a.published_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY c.id, c.name, c.type, c.frequency
ORDER BY recent_mentions DESC, c.frequency DESC;

-- 创建处理状态统计视图
CREATE OR REPLACE VIEW v_processing_stats AS
SELECT 
    stage,
    status,
    COUNT(*) as count,
    AVG(processing_time_seconds) as avg_processing_time,
    MAX(completed_at) as last_completed
FROM processing_status
GROUP BY stage, status
ORDER BY stage, status;

COMMENT ON VIEW v_article_summary IS '文章摘要视图，包含基本信息和关联的分类、概念';
COMMENT ON VIEW v_trending_articles IS '热门文章视图，基于评分和用户反馈';
COMMENT ON VIEW v_concept_trends IS '概念趋势视图，显示最近的热门概念';
COMMENT ON VIEW v_processing_stats IS '处理状态统计视图，用于监控系统性能';