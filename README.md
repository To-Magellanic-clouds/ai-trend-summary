# PKM Copilot - 个人知识管理系统

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-green.svg)](tests/)

## 🎯 项目简介

PKM Copilot 是一套基于AI技术的个人知识管理工具集，解决信息碎片化、知识关联弱、复用效率低等核心痛点，覆盖从信息聚合到智能分析的全流程。

系统包含6个核心模块，既可独立使用，也可协同工作，构建完整的知识管理生态：

- **KnowBase (知库)** - 多源信息聚合中枢
- **VecEmbed (向量工坊)** - 多模态信息向量化引擎  
- **SiftFlow (筛流)** - AI智能过滤系统
- **SumAgent (总结代理)** - 自动化内容提炼工具
- **LinkVerse (关联宇宙)** - 可视化知识图谱模块
- **CollectDeck (收藏甲板)** - 个人知识交互入口

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/your-username/pkm-copilot.git
cd pkm-copilot

# 安装依赖
pip install -r requirements.txt

# 或使用uv
uv pip install -r requirements.txt
```

### 初始化配置

```bash
# 创建开发环境配置
python -m src.main init --template development

# 或创建生产环境配置
python -m src.main init --template production
```

### 启动服务

```bash
# 启动完整工作流
python -m src.main start --workflow full

# 启动特定模块
python -m src.main start --workflow collect  # 仅收集
python -m src.main start --workflow embed    # 仅向量化
```

### 查看状态

```bash
# 查看系统状态
python -m src.main status

# 列出可用模块
python -m src.main module list

# 测试特定模块
python -m src.main module test knowbase
```

## 📊 系统架构

### 模块协作流程

```
KnowBase → VecEmbed → SiftFlow → SumAgent → LinkVerse → CollectDeck
   ↓        ↓        ↓        ↓        ↓        ↓
原始数据   语义向量   过滤提纯   结构化内容  知识关联   用户交互
```

### 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| **后端** | Python + FastAPI | 核心服务 |
| **向量存储** | Qdrant/Pinecone | 语义搜索 |
| **图数据库** | Neo4j | 知识图谱 |
| **关系型数据库** | PostgreSQL | 结构化数据 |
| **文档数据库** | MongoDB | 非结构化数据 |
| **缓存** | Redis | 热点数据 |
| **消息队列** | Redis/RabbitMQ | 异步任务 |

### 数据流架构

```
信息收集 → 预处理 → 向量化 → 过滤 → 分析 → 存储 → 应用
    ↓        ↓       ↓       ↓      ↓      ↓      ↓
  RSS/邮件  清洗    嵌入     评分   概念   数据库  搜索/推荐
```

## 🧩 核心模块

### 1. KnowBase (知库) - 信息聚合

**功能**：统一收集RSS、邮件、爬虫、API等多种数据源

```python
from src.modules.knowbase.core import KnowBaseCore

knowbase = KnowBaseCore()

# 添加RSS源
source = DataSource(
    name="技术博客",
    type=DataSourceType.RSS,
    config={"url": "https://example.com/rss"}
)

# 同步数据源
await knowbase.sync_all_sources([source])
```

**支持的数据源**：
- RSS/Atom订阅
- 邮件订阅 (IMAP)
- 网络爬虫
- API接口
- 手动导入
- 文件上传

### 2. VecEmbed (向量工坊) - 语义处理

**功能**：将文本内容转换为语义向量，支持多种模型

```python
from src.modules.vecembed.core import VecEmbedCore

vecembed = VecEmbedCore()

# 文本向量化
embedding = await vecembed.vectorize_text("AI技术发展")

# 语义搜索
results = await vecembed.search_similar("机器学习应用", limit=10)
```

**支持的模型**：
- Sentence Transformers
- OpenAI Embeddings
- Hugging Face Transformers
- 本地模型

### 3. SiftFlow (筛流) - 智能过滤 *(开发中)*

**功能**：基于AI的内容质量评估和个性化过滤

### 4. SumAgent (总结代理) - 内容提炼 *(开发中)*

**功能**：自动生成摘要、提取关键词、识别概念

### 5. LinkVerse (关联宇宙) - 知识图谱 *(开发中)*

**功能**：构建实体关系图，支持可视化查询

### 6. CollectDeck (收藏甲板) - 用户交互 *(开发中)*

**功能**：收藏管理、语义搜索、批注笔记

## 🏗️ 项目结构

```
pkm-copilot/
├── src/
│   ├── core/              # 核心接口和数据模型
│   ├── modules/           # 模块化组件
│   │   ├── knowbase/     # 信息聚合
│   │   ├── vecembed/     # 向量化
│   │   ├── siftflow/     # 过滤
│   │   ├── sumagent/     # 总结
│   │   ├── linkverse/    # 知识图谱
│   │   └── collectdeck/  # 收藏管理
│   └── main.py           # 主入口
├── tests/                 # 测试套件
├── config/               # 配置文件
├── docs/                 # 文档
├── migrations/           # 数据迁移脚本
└── scripts/              # 工具脚本
```

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/test_modules/test_knowbase.py -v

# 运行集成测试
pytest tests/integration/ -v

# 运行性能测试
pytest tests/performance/ -v
```

### 测试覆盖率

```bash
# 生成覆盖率报告
pytest --cov=src --cov-report=html

# 查看报告
open htmlcov/index.html
```

## 📖 迁移指南

从旧架构迁移到新架构，请参考 [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)。

## 📖 详细文档

- [向量化SDK文档](src/infrastructure/embedding/README.md)
- [文章处理工具文档](src/processing/README.md)
- [数据库设计文档](database/README.md)
- [项目介绍](documentation/项目介绍.md)

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Sentence Transformers](https://www.sbert.net/) - 文本向量化
- [FastAPI](https://fastapi.tiangolo.com/) - Web框架
- [Qdrant](https://qdrant.tech/) - 向量数据库
- [Neo4j](https://neo4j.com/) - 图数据库

---

**PKM Copilot** - 让知识管理更智能 🚀