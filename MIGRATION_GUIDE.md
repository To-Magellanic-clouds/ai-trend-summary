# PKM Copilot 架构迁移指南

## 概述

本指南帮助您从现有的单体架构迁移到新的PKM Copilot模块化架构。新的架构基于完整产品构想，将系统分解为6个核心模块：

1. **KnowBase (知库)** - 多源信息聚合中枢
2. **VecEmbed (向量工坊)** - 多模态信息向量化引擎
3. **SiftFlow (筛流)** - AI智能过滤系统
4. **SumAgent (总结代理)** - 自动化内容提炼工具
5. **LinkVerse (关联宇宙)** - 可视化知识图谱模块
6. **CollectDeck (收藏甲板)** - 个人知识交互入口

## 迁移前准备

### 1. 备份现有数据

```bash
# 备份配置文件
cp -r config/ config_backup/

# 备份数据库数据
pg_dump your_database_name > backup.sql

# 备份MongoDB数据
mongodump --out=mongodb_backup/

# 备份结果文件
cp -r result/ result_backup/
```

### 2. 创建新配置

```bash
# 创建新的PKM Copilot配置
python -m src.main init --template development --output config/pkm_copilot.yaml

# 或创建生产环境配置
python -m src.main init --template production --output config/pkm_copilot_prod.yaml
```

## 架构变化对比

### 旧架构 vs 新架构

| 组件 | 旧架构 | 新架构 |
|------|--------|--------|
| **数据处理** | 单体处理管道 | 模块化工作流 |
| **配置管理** | 分散配置 | 统一配置系统 |
| **API接口** | 无统一接口 | 标准化RESTful API |
| **扩展性** | 难以扩展 | 插件式架构 |
| **数据模型** | 不一致 | 统一数据模型 |
| **测试** | 集成测试为主 | 单元+集成测试 |

### 代码结构变化

```
# 旧结构
src/
├── processing/           # 处理逻辑
├── scraper/             # 爬虫
├── infrastructure/      # 基础设施
└── NER/                # 命名实体识别

# 新结构
src/
├── core/               # 核心接口和模型
├── modules/            # 模块化组件
│   ├── knowbase/      # 信息聚合
│   ├── vecembed/      # 向量化
│   ├── siftflow/      # 过滤
│   ├── sumagent/      # 总结
│   ├── linkverse/     # 知识图谱
│   └── collectdeck/   # 收藏管理
├── api/               # API接口
└── tests/             # 测试套件
```

## 逐步迁移步骤

### 阶段1：环境准备（1-2天）

1. **安装依赖**
   ```bash
   # 安装新的依赖
   pip install sentence-transformers qdrant-client
   pip install fastapi uvicorn
   pip install aiohttp feedparser
   ```

2. **创建新目录结构**
   ```bash
   mkdir -p src/modules/{knowbase,vecembed,siftflow,sumagent,linkverse,collectdeck}
   mkdir -p tests/test_modules
   mkdir -p config
   ```

### 阶段2：数据模型迁移（2-3天）

1. **统一数据模型**
   - 将所有Article类替换为新的`Article`模型
   - 更新数据库模式以支持新字段
   - 迁移现有数据到新格式

2. **配置迁移**
   ```python
   # 旧配置
   from src.config.configReader import ConfigReader
   
   # 新配置
   from src.core.config import get_config
   config = get_config()
   ```

### 阶段3：模块迁移（按模块逐步进行）

#### 3.1 KnowBase模块迁移

**旧代码位置**: `src/scraper/huggingface/`
**新代码位置**: `src/modules/knowbase/`

**迁移步骤**:

1. **迁移爬虫逻辑**
   ```python
   # 旧代码
   from src.scraper.huggingface.Huggingface_crawler import HuggingfaceCrawler
   
   # 新代码
   from src.modules.knowbase.core import WebCollector
   ```

2. **更新数据源配置**
   ```python
   # 旧配置
   config = {
       "url": "https://huggingface.co/blog",
       "selector": "article"
   }
   
   # 新配置
   source = DataSource(
       name="Hugging Face博客",
       type=DataSourceType.CRAWLER,
       config={
           "url": "https://huggingface.co/blog",
           "selector": "article"
       }
   )
   ```

#### 3.2 VecEmbed模块迁移

**旧代码位置**: `src/infrastructure/embedding/`
**新代码位置**: `src/modules/vecembed/`

**迁移步骤**:

1. **迁移向量化逻辑**
   ```python
   # 旧代码
   from src.infrastructure.embedding.embedding_service import EmbeddingService
   
   # 新代码
   from src.modules.vecembed.core import VecEmbedCore
   ```

2. **更新向量存储**
   ```python
   # 旧代码
   embedding_service.store_vectors(vectors)
   
   # 新代码
   vecembed_core.store_vectors(vectors)
   ```

### 阶段4：测试验证（1-2天）

1. **运行新测试**
   ```bash
   pytest tests/test_modules/ -v
   ```

2. **验证数据一致性**
   ```bash
   python -m src.main module test knowbase
   python -m src.main module test vecembed
   ```

## 兼容层

为了平滑迁移，我们提供了兼容层：

### 向后兼容API

```python
# src/legacy/compatibility.py

from src.modules.knowbase.core import KnowBaseCore
from src.modules.vecembed.core import VecEmbedCore

class LegacyProcessor:
    """兼容旧处理接口"""
    
    def __init__(self):
        self.knowbase = KnowBaseCore()
        self.vecembed = VecEmbedCore()
    
    async def process_articles(self, input_path: str, output_path: str):
        """兼容旧的处理方法"""
        # 使用新模块实现旧接口
        pass
```

### 配置文件兼容

```python
# config/migration.py

import json
from pathlib import Path

def migrate_old_config(old_config_path: str, new_config_path: str):
    """迁移旧配置文件"""
    with open(old_config_path, 'r') as f:
        old_config = json.load(f)
    
    # 映射旧配置到新配置
    new_config = {
        "knowbase": {
            "sources": old_config.get("sources", {})
        },
        "vecembed": {
            "embedding_model": old_config.get("embedding_model", "all-MiniLM-L6-v2")
        }
    }
    
    with open(new_config_path, 'w') as f:
        json.dump(new_config, f, indent=2)
```

## 数据迁移脚本

### 数据库迁移

```bash
#!/bin/bash
# migrate_database.sh

# 迁移PostgreSQL表结构
psql -d your_database << EOF
-- 添加新字段
ALTER TABLE articles ADD COLUMN IF NOT EXISTS concepts TEXT[];
ALTER TABLE articles ADD COLUMN IF NOT EXISTS embedding VECTOR(384);
ALTER TABLE articles ADD COLUMN IF NOT EXISTS content_type VARCHAR(50);

-- 创建新表
CREATE TABLE IF NOT EXISTS data_sources (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    last_sync TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
EOF

# 迁移MongoDB数据
python migrate_mongodb.py
```

### 文件迁移

```python
# migrate_files.py

import shutil
from pathlib import Path

def migrate_file_structure():
    """迁移文件结构"""
    
    # 创建新目录结构
    new_dirs = [
        "src/modules/knowbase/sources",
        "src/modules/vecembed/models",
        "tests/test_modules"
    ]
    
    for dir_path in new_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # 移动现有文件
    migrations = [
        ("src/scraper/huggingface", "src/modules/knowbase/sources/huggingface"),
        ("src/infrastructure/embedding", "src/modules/vecembed/legacy"),
    ]
    
    for old_path, new_path in migrations:
        if Path(old_path).exists():
            shutil.move(old_path, new_path)
            print(f"Moved: {old_path} -> {new_path}")

if __name__ == "__main__":
    migrate_file_structure()
```

## 验证检查清单

### 功能验证

- [ ] 数据源收集功能正常
- [ ] 文本向量化功能正常
- [ ] 配置文件正确加载
- [ ] API接口响应正常
- [ ] 数据一致性检查通过

### 性能验证

- [ ] 新架构性能不低于旧架构
- [ ] 内存使用在合理范围内
- [ ] 响应时间满足要求

### 兼容性验证

- [ ] 旧数据可以正常读取
- [ ] 旧配置文件可以迁移
- [ ] 现有API调用仍然有效

## 回滚计划

如果迁移过程中出现问题，可以按以下步骤回滚：

1. **停止新服务**
   ```bash
   pkill -f pkm_copilot
   ```

2. **恢复配置**
   ```bash
   cp config_backup/* config/
   ```

3. **恢复数据库**
   ```bash
   psql -d your_database < backup.sql
   mongorestore mongodb_backup/
   ```

4. **恢复文件结构**
   ```bash
   cp -r result_backup/* result/
   ```

## 常见问题

### Q: 迁移后原有数据会丢失吗？
A: 不会，迁移过程会保留所有原有数据，并提供数据验证脚本。

### Q: 需要修改现有代码吗？
A: 是的，需要更新导入路径和配置方式，但提供了兼容层减少修改量。

### Q: 新架构支持哪些数据库？
A: 支持PostgreSQL、MongoDB、Redis和Neo4j，可根据需要选择。

### Q: 如何测试新架构？
A: 可以使用提供的测试套件：`pytest tests/test_modules/`

## 技术支持

如果在迁移过程中遇到问题，可以：

1. 查看日志：`tail -f logs/pkm_copilot.log`
2. 运行诊断：`python -m src.main status`
3. 测试模块：`python -m src.main module test [模块名]`
4. 查看文档：`docs/migration/`目录下的详细文档

## 后续计划

迁移完成后，建议：

1. **性能优化**：监控新架构性能
2. **功能扩展**：逐步实现剩余模块
3. **文档更新**：更新技术文档
4. **团队培训**：让团队熟悉新架构

---

**注意**：建议先在测试环境完成迁移验证，再应用到生产环境。