-- 重复检测和复用机制的核心查询
-- 演示如何实现智能重复检测和处理结果复用

-- =============================================================================
-- 1. 重复检测查询
-- =============================================================================

-- 基于内容hash的精确重复检测
CREATE OR REPLACE FUNCTION detect_exact_duplicates(input_content_hash VARCHAR(64))
RETURNS TABLE (
    article_id INTEGER,
    title TEXT,
    similarity_score DECIMAL(5,4),
    detection_method VARCHAR(50)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.id,
        a.title,
        1.0::DECIMAL(5,4) as similarity_score,
        'content_hash'::VARCHAR(50) as detection_method
    FROM articles a
    JOIN content_fingerprints cf ON a.fingerprint_id = cf.id
    WHERE cf.content_hash = input_content_hash
    AND a.is_duplicate = false;
END;
$$ LANGUAGE plpgsql;

-- 基于标题相似度的模糊重复检测
CREATE OR REPLACE FUNCTION detect_title_similarity(input_title TEXT, threshold DECIMAL(3,2) DEFAULT 0.8)
RETURNS TABLE (
    article_id INTEGER,
    title TEXT,
    similarity_score DECIMAL(5,4),
    detection_method VARCHAR(50)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.id,
        a.title,
        similarity(a.title, input_title)::DECIMAL(5,4) as similarity_score,
        'title_similarity'::VARCHAR(50) as detection_method
    FROM articles a
    WHERE similarity(a.title, input_title) >= threshold
    AND a.is_duplicate = false
    ORDER BY similarity(a.title, input_title) DESC;
END;
$$ LANGUAGE plpgsql;

-- 基于SimHash的近似重复检测
CREATE OR REPLACE FUNCTION detect_simhash_duplicates(input_simhash BIGINT, hamming_threshold INTEGER DEFAULT 3)
RETURNS TABLE (
    article_id INTEGER,
    title TEXT,
    hamming_distance INTEGER,
    similarity_score DECIMAL(5,4),
    detection_method VARCHAR(50)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.id,
        a.title,
        bit_count(cf.simhash # input_simhash) as hamming_distance,
        (1.0 - bit_count(cf.simhash # input_simhash)::DECIMAL / 64.0)::DECIMAL(5,4) as similarity_score,
        'simhash'::VARCHAR(50) as detection_method
    FROM articles a
    JOIN content_fingerprints cf ON a.fingerprint_id = cf.id
    WHERE bit_count(cf.simhash # input_simhash) <= hamming_threshold
    AND a.is_duplicate = false
    ORDER BY bit_count(cf.simhash # input_simhash);
END;
$$ LANGUAGE plpgsql;

-- 综合重复检测函数
CREATE OR REPLACE FUNCTION comprehensive_duplicate_detection(
    input_content_hash VARCHAR(64),
    input_title TEXT,
    input_simhash BIGINT DEFAULT NULL,
    input_author VARCHAR(200) DEFAULT NULL,
    input_url VARCHAR(1000) DEFAULT NULL
)
RETURNS TABLE (
    article_id INTEGER,
    title TEXT,
    author VARCHAR(200),
    url VARCHAR(1000),
    similarity_score DECIMAL(5,4),
    detection_method VARCHAR(50),
    confidence_level VARCHAR(20)
) AS $$
BEGIN
    -- 1. 精确内容匹配 (最高优先级)
    IF EXISTS (SELECT 1 FROM content_fingerprints WHERE content_hash = input_content_hash) THEN
        RETURN QUERY
        SELECT * FROM detect_exact_duplicates(input_content_hash);
        RETURN;
    END IF;
    
    -- 2. URL匹配
    IF input_url IS NOT NULL THEN
        RETURN QUERY
        SELECT 
            a.id,
            a.title,
            a.author,
            a.url,
            1.0::DECIMAL(5,4) as similarity_score,
            'url_match'::VARCHAR(50) as detection_method,
            'high'::VARCHAR(20) as confidence_level
        FROM articles a
        WHERE a.url = input_url
        AND a.is_duplicate = false;
        
        IF FOUND THEN
            RETURN;
        END IF;
    END IF;
    
    -- 3. 作者+标题组合匹配
    IF input_author IS NOT NULL THEN
        RETURN QUERY
        SELECT 
            a.id,
            a.title,
            a.author,
            a.url,
            similarity(a.title, input_title)::DECIMAL(5,4) as similarity_score,
            'author_title'::VARCHAR(50) as detection_method,
            CASE 
                WHEN similarity(a.title, input_title) > 0.9 THEN 'high'
                WHEN similarity(a.title, input_title) > 0.7 THEN 'medium'
                ELSE 'low'
            END::VARCHAR(20) as confidence_level
        FROM articles a
        WHERE a.author = input_author
        AND similarity(a.title, input_title) >= 0.6
        AND a.is_duplicate = false
        ORDER BY similarity(a.title, input_title) DESC
        LIMIT 5;
        
        IF FOUND THEN
            RETURN;
        END IF;
    END IF;
    
    -- 4. SimHash近似匹配
    IF input_simhash IS NOT NULL THEN
        RETURN QUERY
        SELECT 
            d.article_id,
            a.title,
            a.author,
            a.url,
            d.similarity_score,
            d.detection_method,
            CASE 
                WHEN d.hamming_distance <= 2 THEN 'high'
                WHEN d.hamming_distance <= 5 THEN 'medium'
                ELSE 'low'
            END::VARCHAR(20) as confidence_level
        FROM detect_simhash_duplicates(input_simhash, 8) d
        JOIN articles a ON d.article_id = a.id
        LIMIT 5;
        
        IF FOUND THEN
            RETURN;
        END IF;
    END IF;
    
    -- 5. 标题相似度匹配 (最后的兜底策略)
    RETURN QUERY
    SELECT 
        d.article_id,
        a.title,
        a.author,
        a.url,
        d.similarity_score,
        d.detection_method,
        CASE 
            WHEN d.similarity_score > 0.9 THEN 'high'
            WHEN d.similarity_score > 0.7 THEN 'medium'
            ELSE 'low'
        END::VARCHAR(20) as confidence_level
    FROM detect_title_similarity(input_title, 0.6) d
    JOIN articles a ON d.article_id = a.id
    LIMIT 3;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 2. 处理结果复用查询
-- =============================================================================

-- 查找可复用的处理结果
CREATE OR REPLACE FUNCTION find_reusable_processing_results(target_article_id INTEGER)
RETURNS TABLE (
    source_article_id INTEGER,
    available_stages processing_stage[],
    reuse_confidence DECIMAL(3,2),
    similarity_basis VARCHAR(50)
) AS $$
DECLARE
    target_fingerprint_id INTEGER;
    target_content_hash VARCHAR(64);
BEGIN
    -- 获取目标文章的指纹信息
    SELECT a.fingerprint_id, cf.content_hash 
    INTO target_fingerprint_id, target_content_hash
    FROM articles a
    JOIN content_fingerprints cf ON a.fingerprint_id = cf.id
    WHERE a.id = target_article_id;
    
    -- 1. 查找完全相同的内容 (可以完全复用)
    RETURN QUERY
    SELECT 
        a.id as source_article_id,
        array_agg(DISTINCT ps.stage ORDER BY ps.stage) as available_stages,
        1.0::DECIMAL(3,2) as reuse_confidence,
        'exact_content_match'::VARCHAR(50) as similarity_basis
    FROM articles a
    JOIN content_fingerprints cf ON a.fingerprint_id = cf.id
    JOIN processing_status ps ON a.id = ps.article_id
    WHERE cf.content_hash = target_content_hash
    AND a.id != target_article_id
    AND ps.status = 'completed'
    GROUP BY a.id
    HAVING count(ps.stage) > 0;
    
    -- 如果找到完全匹配，直接返回
    IF FOUND THEN
        RETURN;
    END IF;
    
    -- 2. 查找高度相似的内容 (可以部分复用)
    RETURN QUERY
    SELECT 
        ddr.target_article_id as source_article_id,
        array_agg(DISTINCT ps.stage ORDER BY ps.stage) as available_stages,
        GREATEST(ddr.similarity_score * 0.8, 0.5)::DECIMAL(3,2) as reuse_confidence,
        ddr.detection_method as similarity_basis
    FROM duplicate_detection_results ddr
    JOIN processing_status ps ON ddr.target_article_id = ps.article_id
    WHERE ddr.source_article_id = target_article_id
    AND ddr.similarity_score >= 0.8
    AND ddr.confidence_level IN ('high', 'medium')
    AND ps.status = 'completed'
    GROUP BY ddr.target_article_id, ddr.similarity_score, ddr.detection_method
    HAVING count(ps.stage) > 0
    ORDER BY reuse_confidence DESC
    LIMIT 3;
END;
$$ LANGUAGE plpgsql;

-- 执行处理结果复用
CREATE OR REPLACE FUNCTION reuse_processing_results(
    source_article_id INTEGER,
    target_article_id INTEGER,
    stages_to_reuse processing_stage[],
    reuse_strategy VARCHAR(50) DEFAULT 'partial_copy'
)
RETURNS BOOLEAN AS $$
DECLARE
    stage processing_stage;
    source_result RECORD;
    reuse_confidence DECIMAL(3,2);
BEGIN
    -- 计算复用置信度
    SELECT similarity_score INTO reuse_confidence
    FROM duplicate_detection_results
    WHERE (source_article_id = source_article_id AND target_article_id = target_article_id)
    OR (source_article_id = target_article_id AND target_article_id = source_article_id)
    ORDER BY similarity_score DESC
    LIMIT 1;
    
    IF reuse_confidence IS NULL THEN
        reuse_confidence := 0.7; -- 默认置信度
    END IF;
    
    -- 遍历要复用的阶段
    FOREACH stage IN ARRAY stages_to_reuse
    LOOP
        -- 获取源文章的处理结果
        SELECT * INTO source_result
        FROM processing_status
        WHERE article_id = source_article_id
        AND stage = stage
        AND status = 'completed';
        
        IF FOUND THEN
            -- 复制处理状态
            INSERT INTO processing_status (
                article_id, stage, status, processor_name, processor_version,
                result_data, confidence_score, completed_at, created_at
            ) VALUES (
                target_article_id, stage, 'completed', 
                source_result.processor_name || '_reused',
                source_result.processor_version,
                source_result.result_data,
                LEAST(source_result.confidence_score, reuse_confidence),
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            ) ON CONFLICT (article_id, stage) DO UPDATE SET
                status = 'completed',
                result_data = EXCLUDED.result_data,
                confidence_score = EXCLUDED.confidence_score,
                completed_at = CURRENT_TIMESTAMP;
            
            -- 根据阶段类型复用具体数据
            CASE stage
                WHEN 'concepts_extracted' THEN
                    -- 复用概念提取结果
                    INSERT INTO article_concepts (
                        article_id, concept_id, relevance_score, mention_count,
                        context_snippets, extraction_method, created_at
                    )
                    SELECT 
                        target_article_id, concept_id, 
                        relevance_score * reuse_confidence,
                        mention_count, context_snippets,
                        extraction_method || '_reused',
                        CURRENT_TIMESTAMP
                    FROM article_concepts
                    WHERE article_id = source_article_id
                    ON CONFLICT (article_id, concept_id) DO NOTHING;
                    
                WHEN 'classified' THEN
                    -- 复用分类结果
                    INSERT INTO article_classifications (
                        article_id, domain_id, article_type_id,
                        confidence_score, created_at
                    )
                    SELECT 
                        target_article_id, domain_id, article_type_id,
                        confidence_score * reuse_confidence,
                        CURRENT_TIMESTAMP
                    FROM article_classifications
                    WHERE article_id = source_article_id
                    ON CONFLICT (article_id, domain_id, article_type_id) DO NOTHING;
                    
                ELSE
                    -- 其他阶段只复用状态，不复用具体数据
                    NULL;
            END CASE;
        END IF;
    END LOOP;
    
    -- 记录复用日志
    INSERT INTO processing_reuse_log (
        source_article_id, target_article_id, reused_stages,
        reuse_strategy, reuse_confidence, reused_by, created_at
    ) VALUES (
        source_article_id, target_article_id, stages_to_reuse,
        reuse_strategy, reuse_confidence, 'system_auto', CURRENT_TIMESTAMP
    );
    
    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 3. 用户导入重复检测查询
-- =============================================================================

-- 批量检测用户导入数据的重复情况
CREATE OR REPLACE FUNCTION batch_detect_import_duplicates(batch_id VARCHAR(100))
RETURNS TABLE (
    import_item_id INTEGER,
    duplicate_detected BOOLEAN,
    duplicate_article_id INTEGER,
    duplicate_confidence DECIMAL(3,2),
    detection_method VARCHAR(50)
) AS $$
DECLARE
    item RECORD;
    dup_result RECORD;
    content_hash VARCHAR(64);
    title TEXT;
    author VARCHAR(200);
    url VARCHAR(1000);
BEGIN
    -- 遍历批次中的所有导入项目
    FOR item IN 
        SELECT id, raw_data, normalized_data 
        FROM import_items 
        WHERE batch_id = batch_id
        AND processing_status = 'pending'
    LOOP
        -- 提取关键字段
        title := COALESCE(
            item.normalized_data->>'title',
            item.raw_data->>'title'
        );
        
        author := COALESCE(
            item.normalized_data->>'author',
            item.raw_data->>'author'
        );
        
        url := COALESCE(
            item.normalized_data->>'url',
            item.raw_data->>'url'
        );
        
        -- 计算内容hash
        content_hash := encode(
            sha256(
                COALESCE(item.normalized_data->>'content', item.raw_data->>'content', '')::bytea
            ), 
            'hex'
        );
        
        -- 执行重复检测
        SELECT * INTO dup_result
        FROM comprehensive_duplicate_detection(
            content_hash, title, NULL, author, url
        )
        ORDER BY similarity_score DESC
        LIMIT 1;
        
        -- 返回检测结果
        IF FOUND THEN
            RETURN QUERY VALUES (
                item.id,
                TRUE,
                dup_result.article_id,
                dup_result.similarity_score::DECIMAL(3,2),
                dup_result.detection_method
            );
            
            -- 更新导入项目状态
            UPDATE import_items SET
                duplicate_detected = TRUE,
                duplicate_article_id = dup_result.article_id,
                duplicate_confidence = dup_result.similarity_score::DECIMAL(3,2)
            WHERE id = item.id;
        ELSE
            RETURN QUERY VALUES (
                item.id,
                FALSE,
                NULL::INTEGER,
                NULL::DECIMAL(3,2),
                NULL::VARCHAR(50)
            );
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 4. 监控和统计查询
-- =============================================================================

-- 重复检测效果统计
CREATE OR REPLACE VIEW v_deduplication_stats AS
SELECT 
    DATE_TRUNC('day', created_at) as date,
    COUNT(*) as total_articles,
    COUNT(*) FILTER (WHERE is_duplicate = true) as duplicate_count,
    COUNT(*) FILTER (WHERE is_duplicate = false) as unique_count,
    ROUND(
        COUNT(*) FILTER (WHERE is_duplicate = true)::DECIMAL / COUNT(*) * 100, 2
    ) as duplicate_rate,
    acquisition_method
FROM articles
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', created_at), acquisition_method
ORDER BY date DESC, acquisition_method;

-- 处理结果复用统计
CREATE OR REPLACE VIEW v_reuse_stats AS
SELECT 
    DATE_TRUNC('day', created_at) as date,
    COUNT(*) as total_reuse_events,
    COUNT(DISTINCT target_article_id) as articles_benefited,
    AVG(reuse_confidence) as avg_confidence,
    reuse_strategy,
    unnest(reused_stages) as stage
FROM processing_reuse_log
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', created_at), reuse_strategy, unnest(reused_stages)
ORDER BY date DESC;