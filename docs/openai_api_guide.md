# OpenAI 兼容 API 使用指南

本文档介绍如何在 AI 趋势总结工具中使用 OpenAI 兼容的模型 API。

## 支持的 API 类型

### 1. OpenAI 官方 API
- 提供商：`openai`
- 支持模型：`gpt-3.5-turbo`, `gpt-4`, `gpt-4-turbo` 等
- 需要有效的 OpenAI API 密钥

### 2. OpenAI 兼容 API
- 提供商：`openai_compatible`
- 支持任何兼容 OpenAI API 格式的服务
- 例如：Ollama、LocalAI、vLLM、Text Generation WebUI 等

## 配置文件

### OpenAI 官方 API 配置 (`openai.json`)

```json
{
  "llm_provider": "openai",
  "llm_model": "gpt-3.5-turbo",
  "llm_temperature": 0.1,
  "llm_max_tokens": 2000,
  "openai_api_key": "your-openai-api-key-here",
  "openai_api_base": null,
  "openai_organization": null,
  "processor_type": "standard",
  "output_format": "json"
}
```

### OpenAI 兼容 API 配置 (`openai_compatible.json`)

```json
{
  "llm_provider": "openai_compatible",
  "llm_model": "qwen2.5:7b",
  "llm_temperature": 0.1,
  "llm_max_tokens": 2000,
  "openai_api_key": "your-api-key-here",
  "openai_api_base": "http://localhost:11434/v1",
  "openai_organization": null,
  "processor_type": "standard",
  "output_format": "json"
}
```

## 使用方法

### 1. 初始化配置文件

```bash
uv run python src/processing/main.py init-configs
```

这将创建包括 `openai.json` 和 `openai_compatible.json` 在内的所有默认配置文件。

### 2. 修改配置文件

根据你的需求修改配置文件：

#### 对于 OpenAI 官方 API：
- 将 `openai_api_key` 设置为你的 OpenAI API 密钥
- 根据需要修改 `llm_model`（如 `gpt-4`）

#### 对于 OpenAI 兼容 API：
- 将 `openai_api_base` 设置为你的 API 服务地址
- 将 `openai_api_key` 设置为你的 API 密钥（某些服务可能不需要）
- 将 `llm_model` 设置为你要使用的模型名称

### 3. 运行处理

```bash
# 使用 OpenAI 官方 API
uv run python src/processing/main.py config openai --input "path/to/articles" --output "results.json"

# 使用 OpenAI 兼容 API
uv run python src/processing/main.py config openai_compatible --input "path/to/articles" --output "results.json"
```

## 常见的 OpenAI 兼容服务配置

### Ollama
```json
{
  "llm_provider": "openai_compatible",
  "llm_model": "llama2:7b",
  "openai_api_key": "ollama",
  "openai_api_base": "http://localhost:11434/v1"
}
```

### LocalAI
```json
{
  "llm_provider": "openai_compatible",
  "llm_model": "gpt-3.5-turbo",
  "openai_api_key": "your-localai-key",
  "openai_api_base": "http://localhost:8080/v1"
}
```

### vLLM
```json
{
  "llm_provider": "openai_compatible",
  "llm_model": "meta-llama/Llama-2-7b-chat-hf",
  "openai_api_key": "EMPTY",
  "openai_api_base": "http://localhost:8000/v1"
}
```

### Text Generation WebUI (oobabooga)
```json
{
  "llm_provider": "openai_compatible",
  "llm_model": "your-model-name",
  "openai_api_key": "your-key",
  "openai_api_base": "http://localhost:5000/v1"
}
```

## 环境变量

你也可以通过环境变量设置 API 密钥：

```bash
# OpenAI 官方 API
export OPENAI_API_KEY="your-openai-api-key"

# OpenAI 兼容 API（在代码中会设置为 COMPATIBLE_API_KEY）
export COMPATIBLE_API_KEY="your-compatible-api-key"
```

## 故障排除

### 1. 连接错误
- 确保 API 服务正在运行
- 检查 `openai_api_base` 地址是否正确
- 验证网络连接

### 2. 认证错误
- 检查 API 密钥是否正确
- 某些服务可能不需要 API 密钥，可以设置为任意值

### 3. 模型不存在
- 确保指定的模型在服务中可用
- 使用 `list-configs` 命令查看当前配置

### 4. 参数错误
- 检查 `llm_temperature` 和 `llm_max_tokens` 是否在合理范围内
- 某些模型可能有特定的参数限制

## 测试配置

使用测试脚本验证配置：

```bash
uv run python test_openai_support.py
```

这将测试配置创建和对象初始化，但不会实际调用 API。

## 性能优化建议

1. **批处理**：对于大量文章，使用 `batch_size` 参数控制批处理大小
2. **并行处理**：设置 `enable_parallel: true` 和适当的 `max_workers`
3. **温度设置**：对于一致性要求高的任务，使用较低的 `llm_temperature`（如 0.1）
4. **令牌限制**：根据模型能力设置合适的 `llm_max_tokens`

## 注意事项

1. **成本控制**：使用 OpenAI 官方 API 时注意 token 使用量和成本
2. **速率限制**：遵守 API 提供商的速率限制
3. **数据隐私**：确保敏感数据的处理符合隐私要求
4. **模型选择**：根据任务复杂度选择合适的模型