-- 示例查询脚本
-- 演示如何使用数据库进行常见的查询操作

-- =============================================================================
-- 1. 基础查询示例
-- =============================================================================

-- 查询最近7天的热门文章
SELECT 
    title,
    author,
    published_at,
    quality_score,
    trending_score,
    url
FROM articles 
WHERE published_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY trending_score DESC, quality_score DESC
LIMIT 10;

-- 查询特定领域的文章
SELECT 
    a.title,
    a.published_at,
    d.name as domain,
    a.quality_score
FROM articles a
JOIN article_classifications ac ON a.id = ac.article_id
JOIN domains d ON ac.domain_id = d.id
WHERE d.name = 'AI模型能力'
ORDER BY a.published_at DESC;

-- =============================================================================
-- 2. 概念分析查询
-- =============================================================================

-- 查询最热门的概念
SELECT 
    c.name,
    c.type,
    c.frequency,
    COUNT(ac.article_id) as recent_articles,
    AVG(ac.relevance_score) as avg_relevance
FROM concepts c
LEFT JOIN article_concepts ac ON c.id = ac.concept_id
LEFT JOIN articles a ON ac.article_id = a.id
WHERE a.published_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY c.id, c.name, c.type, c.frequency
HAVING COUNT(ac.article_id) > 0
ORDER BY recent_articles DESC, c.frequency DESC
LIMIT 20;

-- 查询概念共现关系
SELECT 
    c1.name as concept1,
    c2.name as concept2,
    COUNT(*) as co_occurrence_count
FROM article_concepts ac1
JOIN article_concepts ac2 ON ac1.article_id = ac2.article_id AND ac1.concept_id < ac2.concept_id
JOIN concepts c1 ON ac1.concept_id = c1.id
JOIN concepts c2 ON ac2.concept_id = c2.id
JOIN articles a ON ac1.article_id = a.id
WHERE a.published_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY c1.name, c2.name
HAVING COUNT(*) >= 3
ORDER BY co_occurrence_count DESC;

-- =============================================================================
-- 3. 数据源分析查询
-- =============================================================================

-- 各数据源的文章质量分析
SELECT 
    ds.name as source,
    COUNT(a.id) as total_articles,
    AVG(a.quality_score) as avg_quality,
    AVG(a.importance_score) as avg_importance,
    MAX(a.published_at) as latest_article
FROM data_sources ds
LEFT JOIN articles a ON ds.id = a.source_id
WHERE a.published_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY ds.id, ds.name
ORDER BY avg_quality DESC;

-- 数据源的爬取状态
SELECT 
    name,
    last_crawl_time,
    crawl_frequency_hours,
    CASE 
        WHEN last_crawl_time < CURRENT_TIMESTAMP - INTERVAL '1 hour' * crawl_frequency_hours 
        THEN 'OVERDUE'
        ELSE 'OK'
    END as status
FROM data_sources
WHERE is_active = true;

-- =============================================================================
-- 4. 处理状态监控查询
-- =============================================================================

-- 处理队列状态
SELECT 
    task_type,
    status,
    COUNT(*) as count,
    AVG(retry_count) as avg_retries
FROM processing_queue
GROUP BY task_type, status
ORDER BY task_type, status;

-- 处理性能分析
SELECT 
    stage,
    COUNT(*) as total_processed,
    AVG(processing_time_seconds) as avg_time_seconds,
    MIN(processing_time_seconds) as min_time,
    MAX(processing_time_seconds) as max_time
FROM processing_status
WHERE status = 'completed'
GROUP BY stage
ORDER BY avg_time_seconds DESC;

-- 失败任务分析
SELECT 
    pq.task_type,
    pq.error_message,
    COUNT(*) as failure_count
FROM processing_queue pq
WHERE pq.status = 'failed'
GROUP BY pq.task_type, pq.error_message
ORDER BY failure_count DESC;

-- =============================================================================
-- 5. 用户行为分析查询
-- =============================================================================

-- 用户反馈统计
SELECT 
    feedback_type,
    COUNT(*) as count,
    AVG(rating) as avg_rating
FROM user_feedback
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY feedback_type
ORDER BY count DESC;

-- 最受欢迎的文章
SELECT 
    a.title,
    a.author,
    COUNT(uf.id) as feedback_count,
    AVG(uf.rating) as avg_rating,
    a.quality_score
FROM articles a
JOIN user_feedback uf ON a.id = uf.article_id
WHERE uf.created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY a.id, a.title, a.author, a.quality_score
HAVING COUNT(uf.id) >= 5
ORDER BY avg_rating DESC, feedback_count DESC;

-- =============================================================================
-- 6. 报告生成相关查询
-- =============================================================================

-- 周报数据汇总
WITH weekly_stats AS (
    SELECT 
        DATE_TRUNC('week', published_at) as week,
        COUNT(*) as article_count,
        AVG(quality_score) as avg_quality,
        COUNT(DISTINCT source_id) as source_count
    FROM articles
    WHERE published_at >= CURRENT_DATE - INTERVAL '4 weeks'
    GROUP BY DATE_TRUNC('week', published_at)
)
SELECT 
    week,
    article_count,
    ROUND(avg_quality::numeric, 2) as avg_quality,
    source_count
FROM weekly_stats
ORDER BY week DESC;

-- 领域趋势分析
SELECT 
    d.name as domain,
    DATE_TRUNC('week', a.published_at) as week,
    COUNT(a.id) as article_count,
    AVG(a.importance_score) as avg_importance
FROM domains d
JOIN article_classifications ac ON d.id = ac.domain_id
JOIN articles a ON ac.article_id = a.id
WHERE a.published_at >= CURRENT_DATE - INTERVAL '8 weeks'
GROUP BY d.name, DATE_TRUNC('week', a.published_at)
ORDER BY d.name, week DESC;

-- =============================================================================
-- 7. 数据清理和维护查询
-- =============================================================================

-- 查找重复文章
SELECT 
    content_hash,
    COUNT(*) as duplicate_count,
    array_agg(id) as article_ids
FROM articles
GROUP BY content_hash
HAVING COUNT(*) > 1;

-- 查找孤立的概念（没有关联文章的概念）
SELECT 
    c.id,
    c.name,
    c.type
FROM concepts c
LEFT JOIN article_concepts ac ON c.id = ac.concept_id
WHERE ac.concept_id IS NULL;

-- 查找处理异常的文章
SELECT 
    a.id,
    a.title,
    ps.stage,
    ps.status,
    ps.error_message
FROM articles a
JOIN processing_status ps ON a.id = ps.article_id
WHERE ps.status = 'failed'
ORDER BY ps.created_at DESC;