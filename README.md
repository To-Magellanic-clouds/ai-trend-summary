# AI趋势总结项目

一个通用的信息总结工作流系统，支持信息收集、预处理、分析、筛选、总结和输出的完整流程。

## 🚀 项目特性

- **信息收集**: 支持多种数据源的信息采集
- **智能预处理**: 自动化的数据清洗和标准化
- **深度分析**: 基于LLM的内容分析和概念提取
- **智能筛选**: 多维度评分和过滤机制
- **自动总结**: 生成高质量的信息摘要
- **向量化存储**: 支持语义搜索和RAG应用
- **灵活输出**: 多种格式的结果输出

## 📁 项目结构

```
ai-trend-summary/
├── src/                          # 源代码目录
│   ├── infrastructure/           # 基础设施层
│   │   ├── embedding/            # 向量化SDK
│   │   └── database/             # 数据库操作
│   ├── processing/               # 文章处理工具
│   └── analysis/                 # 分析工具
├── database/                     # 数据库设计和脚本
├── documentation/                # 项目文档
├── examples/                     # 使用示例
├── config/                       # 配置文件
└── test/                        # 测试文件
```

## 🛠️ 核心组件

### 1. 向量化SDK (`src/infrastructure/embedding/`)

功能完整的向量化SDK，支持将各种输入转储到向量数据库中。

**主要特性:**
- 支持多种向量数据库（目前支持Qdrant）
- 多种向量化模型（sentence-transformers、transformers、OpenAI API）
- 自动文档分块处理
- 高效的语义搜索
- 完整的文档CRUD操作

**快速开始:**
```python
from src.infrastructure.embedding import create_embedding_manager, DocumentInput

# 创建管理器
manager = await create_embedding_manager(
    vector_db_host="localhost",
    vector_db_port=6333,
    collection_name="my_documents"
)

# 添加文档
document = DocumentInput(
    content="人工智能是计算机科学的一个分支",
    metadata={"category": "AI"}
)
await manager.add_document(document)

# 搜索相似文档
results = await manager.search_similar_documents("机器学习", top_k=5)
```

### 2. 文章处理工具 (`src/processing/`)

基于LLM的文章处理系统，提供概念提取、内容分析等功能。

**主要特性:**
- 概念提取和实体识别
- 文章质量评分
- 重要性评分和分类
- 批量处理管道
- 多种输出格式

**快速开始:**
```python
from src.processing import ConceptExtractor, ArticleProcessor

# 创建处理器
extractor = ConceptExtractor()
processor = ArticleProcessor(extractor)

# 处理文章
result = processor.process_article("文章内容...")
print(f"概念: {result.concepts.concepts}")
print(f"质量评分: {result.quality_score}")
```

### 3. 数据库设计 (`database/`)

完整的PostgreSQL数据库设计，支持整个信息处理工作流。

**核心表:**
- 数据源管理
- 文章内容存储
- 概念和实体管理
- 处理结果记录
- 用户偏好设置

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd ai-trend-summary

# 安装依赖
pip install -e .

# 复制配置文件
cp .env.example .env
# 根据需要修改 .env 配置
```

### 2. 启动向量数据库

```bash
# 使用Docker启动Qdrant
docker run -p 6333:6333 qdrant/qdrant
```

### 3. 快速设置和测试

```bash
# 运行快速设置脚本
python setup_embedding.py
```

### 4. 运行示例

```bash
# 向量化集成示例
python examples/embedding_integration_example.py

# 文章处理示例
python src/processing/main.py quick --input "path/to/articles" --output "results.json"
```

## 📖 详细文档

- [向量化SDK文档](src/infrastructure/embedding/README.md)
- [文章处理工具文档](src/processing/README.md)
- [数据库设计文档](database/README.md)
- [项目介绍](documentation/项目介绍.md)

## 🔧 配置说明

### 环境变量配置

```bash
# Qdrant向量数据库
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=

# 向量化模型
EMBEDDING_MODEL_NAME=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_MODEL_TYPE=sentence_transformers

# OpenAI配置（可选）
OPENAI_API_KEY=your_api_key_here
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

# 文本处理
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### 预定义配置

项目提供多种预定义配置模板：

```bash
# 查看可用配置
python src/processing/main.py list-configs

# 使用标准配置
python src/processing/main.py config standard

# 使用开发配置
python src/processing/main.py config dev
```

## 🧪 测试

```bash
# 运行向量化SDK测试
python -m pytest src/infrastructure/embedding/test_embedding.py

# 运行文章处理测试
python -m pytest src/processing/tests/

# 运行集成测试
python test/integration_test.py
```

## 📊 使用场景

### 1. 信息收集和总结
- 新闻文章自动收集和总结
- 技术文档的智能分析
- 研究论文的概念提取

### 2. 语义搜索和RAG
- 构建知识库搜索系统
- 实现智能问答系统
- 支持多语言语义检索

### 3. 内容分析和分类
- 文章质量自动评估
- 内容重要性排序
- 主题分类和标签生成

## 🔄 工作流程

1. **数据收集**: 从各种数据源收集信息
2. **预处理**: 清洗和标准化数据
3. **向量化**: 将文本转换为向量表示
4. **存储**: 保存到向量数据库和关系数据库
5. **分析**: 使用LLM进行深度分析
6. **筛选**: 基于多维度评分进行过滤
7. **总结**: 生成高质量摘要
8. **输出**: 多种格式的结果输出

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

如果您遇到问题或有疑问：

1. 查看相关文档
2. 检查 [Issues](../../issues) 中是否有类似问题
3. 创建新的 Issue 描述您的问题

## 🔗 相关链接

- [Qdrant文档](https://qdrant.tech/documentation/)
- [LangChain文档](https://python.langchain.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [OpenAI API](https://platform.openai.com/docs/)

---

**注意**: 这是一个活跃开发中的项目，API可能会发生变化。建议在生产环境使用前进行充分测试。