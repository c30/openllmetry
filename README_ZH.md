<p align="center">
<a href="https://www.traceloop.com/openllmetry#gh-light-mode-only">
<img width="600" src="https://raw.githubusercontent.com/traceloop/openllmetry/main/img/logo-light.png">
</a>
<a href="https://www.traceloop.com/openllmetry#gh-dark-mode-only">
<img width="600" src="https://raw.githubusercontent.com/traceloop/openllmetry/main/img/logo-dark.png">
</a>
</p>

<p align="center">
  <p align="center">为您的 LLM 应用程序提供开源可观测性</p>
</p>

<h4 align="center">
    <a href="https://traceloop.com/docs/openllmetry/getting-started-python"><strong>快速开始 »</strong></a>
    <br />
    <br />
  <a href="https://traceloop.com/slack">Slack</a> |
  <a href="https://traceloop.com/docs/openllmetry/introduction">文档</a> |
  <a href="https://www.traceloop.com/openllmetry">官网</a>
</h4>

<h4 align="center">
  <a href="https://github.com/traceloop/openllmetry/releases">
    <img src="https://img.shields.io/github/release/traceloop/openllmetry">
  </a>
  <a href="https://pepy.tech/project/opentelemetry-instrumentation-openai">
  <img src="https://static.pepy.tech/badge/opentelemetry-instrumentation-openai/month">
  </a>
   <a href="https://github.com/traceloop/openllmetry/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-Apache 2.0-blue.svg" alt="OpenLLMetry 基于 Apache-2.0 许可证发布">
  </a>
  <a href="https://github.com/traceloop/openllmetry/actions/workflows/ci.yml">
  <img src="https://github.com/traceloop/openllmetry/actions/workflows/ci.yml/badge.svg">
  </a>
  <a href="https://traceloop.com/slack">
    <img src="https://img.shields.io/badge/chat-on%20Slack-blueviolet" alt="Slack 社区频道" />
  </a>
</h4>

# OpenLLMetry 用户使用手册

## 📖 目录

- [简介](#-简介)
- [快速开始](#-快速开始)
- [安装指南](#-安装指南)
- [基础使用](#-基础使用)
- [支持的集成](#-支持的集成)
- [高级配置](#-高级配置)
- [最佳实践](#-最佳实践)
- [故障排除](#-故障排除)
- [社区与支持](#-社区与支持)

## 🌟 简介

OpenLLMetry 是构建在 [OpenTelemetry](https://opentelemetry.io/) 之上的扩展集合，为您的 LLM 应用程序提供完整的可观测性。由于底层使用 OpenTelemetry，它可以[连接到您现有的可观测性解决方案](https://www.traceloop.com/docs/openllmetry/integrations/introduction) - Datadog、Honeycomb 等。

**🎉 最新消息**：我们的语义约定现在已经成为 OpenTelemetry 的一部分！加入[讨论](https://github.com/open-telemetry/community/blob/1c71595874e5d125ca92ec3b0e948c4325161c8a/projects/llm-semconv.md)，帮助我们塑造 LLM 可观测性的未来。

### 主要特性

- 🔍 **自动跟踪**：自动记录您的 LLM 调用、向量数据库操作和框架交互
- 🔧 **简单集成**：仅需一行代码即可开始使用
- 🌐 **广泛支持**：支持所有主流 LLM 提供商和向量数据库
- 📊 **标准兼容**：基于 OpenTelemetry 标准，可与现有监控工具集成
- 🔒 **隐私保护**：可控制记录内容，保护敏感数据
- 🛡️ **生产就绪**：由 Traceloop 维护，Apache 2.0 许可证

## 🚀 快速开始

### 1. 安装 SDK

```bash
pip install traceloop-sdk
```

### 2. 初始化跟踪

在您的代码中添加以下行：

```python
from traceloop.sdk import Traceloop

Traceloop.init()
```

就是这样！您现在正在使用 OpenLLMetry 跟踪您的代码。

### 3. 完整示例

```python
from traceloop.sdk import Traceloop
import openai

# 初始化 OpenLLMetry
Traceloop.init(app_name="my-llm-app")

# 您的现有代码将自动被跟踪
client = openai.OpenAI()

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "什么是人工智能？"}]
)

print(response.choices[0].message.content)
```

### 4. 本地开发设置

如果您在本地运行，可能希望禁用批量发送以立即查看跟踪：

```python
Traceloop.init(disable_batch=True)
```

## 📦 安装指南

### 使用 SDK（推荐）

最简单的方式是使用我们的 SDK：

```bash
pip install traceloop-sdk
```

### 使用特定的仪器包

如果您只需要特定的集成，可以安装单独的仪器包：

```bash
# OpenAI
pip install opentelemetry-instrumentation-openai

# Anthropic
pip install opentelemetry-instrumentation-anthropic

# LangChain
pip install opentelemetry-instrumentation-langchain

# 向量数据库
pip install opentelemetry-instrumentation-pinecone
pip install opentelemetry-instrumentation-chromadb
pip install opentelemetry-instrumentation-qdrant
```

### 系统要求

- Python 3.8+
- 支持的操作系统：Linux, macOS, Windows

## 🛠️ 基础使用

### 使用 SDK

```python
from traceloop.sdk import Traceloop

# 基础初始化
Traceloop.init(app_name="my-app")

# 带配置的初始化
Traceloop.init(
    app_name="my-app",
    disable_batch=True,  # 立即发送跟踪数据
    api_endpoint="https://api.traceloop.com",  # 自定义端点
    api_key="your-api-key",  # API 密钥
    disable_content_tracing=False  # 控制内容记录
)
```

### 使用装饰器

```python
from traceloop.sdk import Traceloop
from traceloop.sdk.decorators import workflow, task

Traceloop.init(app_name="my-workflow-app")

@task(name="data_processing")
def process_data(data):
    # 您的数据处理逻辑
    return processed_data

@workflow(name="llm_pipeline")  
def run_pipeline():
    data = load_data()
    processed_data = process_data(data)
    
    # LLM 调用会自动被跟踪
    response = openai.ChatCompletion.create(...)
    
    return response
```

### 手动仪器化

如果您已经有 OpenTelemetry 设置，可以直接使用仪器：

```python
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from opentelemetry.instrumentation.langchain import LangchainInstrumentor

# 仪器化特定的库
OpenAIInstrumentor().instrument()
LangchainInstrumentor().instrument()
```

## 🔌 支持的集成

### LLM 提供商

| 提供商 | 包名 | 状态 |
|--------|------|------|
| OpenAI / Azure OpenAI | `opentelemetry-instrumentation-openai` | ✅ |
| Anthropic | `opentelemetry-instrumentation-anthropic` | ✅ |
| Google Gemini | `opentelemetry-instrumentation-google-generativeai` | ✅ |
| Cohere | `opentelemetry-instrumentation-cohere` | ✅ |
| Ollama | `opentelemetry-instrumentation-ollama` | ✅ |
| Mistral AI | `opentelemetry-instrumentation-mistralai` | ✅ |
| HuggingFace | `opentelemetry-instrumentation-transformers` | ✅ |
| Bedrock (AWS) | `opentelemetry-instrumentation-bedrock` | ✅ |
| Vertex AI (GCP) | `opentelemetry-instrumentation-vertexai` | ✅ |
| IBM Watsonx | `opentelemetry-instrumentation-watsonx` | ✅ |
| Groq | `opentelemetry-instrumentation-groq` | ✅ |

### 向量数据库

| 数据库 | 包名 | 状态 |
|--------|------|------|
| Chroma | `opentelemetry-instrumentation-chromadb` | ✅ |
| Pinecone | `opentelemetry-instrumentation-pinecone` | ✅ |
| Qdrant | `opentelemetry-instrumentation-qdrant` | ✅ |
| Weaviate | `opentelemetry-instrumentation-weaviate` | ✅ |
| Milvus | `opentelemetry-instrumentation-milvus` | ✅ |
| LanceDB | `opentelemetry-instrumentation-lancedb` | ✅ |

### 框架和工具

| 框架 | 包名 | 状态 |
|------|------|------|
| LangChain | `opentelemetry-instrumentation-langchain` | ✅ |
| LangGraph | `opentelemetry-instrumentation-langchain` | ✅ |
| LlamaIndex | `opentelemetry-instrumentation-llamaindex` | ✅ |
| Haystack | `opentelemetry-instrumentation-haystack` | ✅ |
| CrewAI | `opentelemetry-instrumentation-crewai` | ✅ |
| OpenAI Agents | `opentelemetry-instrumentation-openai-agents` | ✅ |

## ⚙️ 高级配置

### 环境变量配置

```bash
# 禁用内容跟踪（保护隐私）
export TRACELOOP_TRACE_CONTENT=false

# 禁用遥测
export TRACELOOP_TELEMETRY=false

# 设置 API 端点
export TRACELOOP_BASE_URL=https://api.traceloop.com

# 设置 API 密钥
export TRACELOOP_API_KEY=your-api-key

# 设置批量配置
export TRACELOOP_DISABLE_BATCH=true
```

### 自定义导出器

```python
from traceloop.sdk import Traceloop
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# 使用自定义 OTLP 导出器
custom_exporter = OTLPSpanExporter(endpoint="http://your-otel-collector:4317")
custom_processor = BatchSpanProcessor(custom_exporter)

Traceloop.init(
    app_name="custom-export-app",
    exporter=custom_exporter
)
```

### 内容过滤

```python
from traceloop.sdk import Traceloop

# 初始化时配置内容过滤
Traceloop.init(
    app_name="filtered-app",
    disable_content_tracing=True  # 完全禁用内容记录
)

# 或使用环境变量
import os
os.environ['TRACELOOP_TRACE_CONTENT'] = 'false'
```

## 📈 监控和可视化

### 支持的监控平台

OpenLLMetry 可以将数据发送到以下平台：

- **Traceloop**：专为 LLM 应用设计
- **Datadog**：企业级监控平台  
- **Honeycomb**：现代可观测性平台
- **New Relic**：应用性能监控
- **Grafana**：开源监控和可视化
- **Azure Application Insights**：微软云监控
- **Google Cloud Monitoring**：谷歌云监控
- **更多...**

### 配置监控平台

#### Datadog

```python
from traceloop.sdk import Traceloop

Traceloop.init(
    app_name="datadog-app",
    exporter="datadog",
    api_key="your-datadog-api-key"
)
```

#### Honeycomb

```python
from traceloop.sdk import Traceloop

Traceloop.init(
    app_name="honeycomb-app", 
    exporter="honeycomb",
    api_key="your-honeycomb-api-key"
)
```

## 📋 最佳实践

### 1. 应用命名

```python
# 好的做法：使用描述性的应用名称
Traceloop.init(app_name="customer-support-chatbot")

# 避免：通用名称
Traceloop.init(app_name="app")
```

### 2. 工作流组织

```python
from traceloop.sdk.decorators import workflow, task

@task(name="document_retrieval")
def retrieve_documents(query):
    # 文档检索逻辑
    return documents

@task(name="llm_generation")  
def generate_response(context, question):
    # LLM 响应生成
    return response

@workflow(name="rag_pipeline")
def rag_workflow(question):
    documents = retrieve_documents(question)
    response = generate_response(documents, question)
    return response
```

### 3. 错误处理

```python
from traceloop.sdk import Traceloop
from opentelemetry import trace

@workflow(name="robust_llm_call")
def make_llm_call():
    tracer = trace.get_tracer(__name__)
    
    with tracer.start_as_current_span("llm_request") as span:
        try:
            # LLM 调用
            response = client.chat.completions.create(...)
            span.set_status(trace.Status(trace.StatusCode.OK))
            return response
        except Exception as e:
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise
```

### 4. 性能优化

```python
# 生产环境：启用批量处理
Traceloop.init(
    app_name="production-app",
    disable_batch=False,  # 默认值
    batch_timeout=30000,  # 30 秒
    max_export_batch_size=512
)

# 开发环境：禁用批量处理
Traceloop.init(
    app_name="dev-app", 
    disable_batch=True
)
```

### 5. 隐私保护

```python
# 方法 1：全局禁用内容跟踪
Traceloop.init(
    app_name="privacy-app",
    disable_content_tracing=True
)

# 方法 2：使用环境变量
import os
os.environ['TRACELOOP_TRACE_CONTENT'] = 'false'

# 方法 3：选择性过滤敏感内容
from traceloop.sdk.decorators import workflow

@workflow(name="sensitive_workflow")
def handle_sensitive_data():
    # 这里的 LLM 调用不会记录内容
    with trace.get_tracer(__name__).start_as_current_span("sensitive_call") as span:
        span.set_attribute("content.filtered", True)
        response = make_llm_call()
    return response
```

## 🔧 故障排除

### 常见问题

#### 1. 没有看到跟踪数据

**解决方案**：
```python
# 确保正确初始化
from traceloop.sdk import Traceloop

Traceloop.init(
    app_name="debug-app",
    disable_batch=True,  # 立即发送数据
    debug=True  # 启用调试日志
)
```

#### 2. 导入错误

**错误**：`ModuleNotFoundError: No module named 'traceloop'`

**解决方案**：
```bash
pip install traceloop-sdk
# 或
pip install --upgrade traceloop-sdk
```

#### 3. SSL 证书问题

**解决方案**：
```python
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# 或设置环境变量
import os
os.environ['PYTHONHTTPSVERIFY'] = '0'
```

#### 4. 内存使用过高

**解决方案**：
```python
Traceloop.init(
    app_name="memory-optimized-app",
    max_export_batch_size=100,  # 减少批量大小
    disable_content_tracing=True  # 禁用内容跟踪
)
```

### 调试工具

#### 控制台导出器

用于调试跟踪层次结构问题：

```python
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from traceloop.sdk import Traceloop

Traceloop.init(
    app_name="debug-app",
    exporter=ConsoleSpanExporter()
)
```

#### 日志记录

```python
import logging

# 启用 OpenTelemetry 日志
logging.getLogger("opentelemetry").setLevel(logging.DEBUG)
logging.getLogger("traceloop").setLevel(logging.DEBUG)

# 配置日志格式
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
```

### 性能监控

```python
from traceloop.sdk import Traceloop
import time

@workflow(name="performance_test")
def test_performance():
    start_time = time.time()
    
    # 您的代码逻辑
    result = expensive_operation()
    
    end_time = time.time()
    print(f"操作耗时: {end_time - start_time:.2f} 秒")
    
    return result
```

## 🎯 实际使用案例

### 案例 1: RAG 应用

```python
from traceloop.sdk import Traceloop
from traceloop.sdk.decorators import workflow, task
import openai
import chromadb

Traceloop.init(app_name="rag-chatbot")

@task(name="document_embedding")
def embed_documents(documents):
    # Chroma 操作会自动被跟踪
    client = chromadb.Client()
    collection = client.create_collection("documents")
    collection.add(documents=documents)
    return collection

@task(name="similarity_search")  
def search_similar(query, collection):
    results = collection.query(query_texts=[query], n_results=3)
    return results

@task(name="llm_generation")
def generate_answer(context, question):
    # OpenAI 调用会自动被跟踪
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"基于以下上下文回答问题：{context}"},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content

@workflow(name="rag_pipeline")
def rag_chat(question):
    # 搜索相关文档
    results = search_similar(question, document_collection)
    context = " ".join([doc for doc in results['documents'][0]])
    
    # 生成回答
    answer = generate_answer(context, question)
    
    return answer
```

### 案例 2: 多模型比较

```python
from traceloop.sdk import Traceloop
from traceloop.sdk.decorators import workflow, task
import openai
import anthropic

Traceloop.init(app_name="model-comparison")

@task(name="openai_generation")
def get_openai_response(prompt):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

@task(name="anthropic_generation") 
def get_anthropic_response(prompt):
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

@workflow(name="model_comparison")
def compare_models(prompt):
    # 同时调用两个模型
    openai_result = get_openai_response(prompt)
    anthropic_result = get_anthropic_response(prompt)
    
    return {
        "openai": openai_result,
        "anthropic": anthropic_result
    }
```

### 案例 3: 批量处理

```python
from traceloop.sdk import Traceloop
from traceloop.sdk.decorators import workflow, task
import concurrent.futures

Traceloop.init(app_name="batch-processor")

@task(name="process_single_item")
def process_item(item):
    # 单项处理逻辑
    result = expensive_llm_call(item)
    return result

@workflow(name="batch_processing")
def process_batch(items):
    results = []
    
    # 并行处理
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_item = {
            executor.submit(process_item, item): item 
            for item in items
        }
        
        for future in concurrent.futures.as_completed(future_to_item):
            item = future_to_item[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                print(f'项目 {item} 处理失败: {exc}')
    
    return results
```

## 🔐 安全和隐私

### 数据保护

OpenLLMetry 提供多种方式保护您的敏感数据：

#### 1. 完全禁用内容跟踪

```python
# 方法 1: 初始化时设置
Traceloop.init(
    app_name="secure-app",
    disable_content_tracing=True
)

# 方法 2: 环境变量
import os
os.environ['TRACELOOP_TRACE_CONTENT'] = 'false'
```

#### 2. 选择性内容过滤

```python
from traceloop.sdk.decorators import workflow
from opentelemetry import trace

@workflow(name="selective_filtering")
def handle_mixed_content():
    # 公开内容 - 正常跟踪
    public_response = get_public_info()
    
    # 敏感内容 - 不跟踪内容
    with trace.get_tracer(__name__).start_as_current_span("sensitive") as span:
        span.set_attribute("content.filtered", True)
        sensitive_response = get_sensitive_info()
    
    return combine_responses(public_response, sensitive_response)
```

#### 3. 自定义数据清理

```python
from opentelemetry import trace

def sanitize_span_data(span):
    """清理敏感数据的回调函数"""
    # 移除 PII 数据
    attributes = span.attributes
    if attributes:
        # 清理邮箱
        for key, value in attributes.items():
            if isinstance(value, str) and '@' in value:
                span.set_attribute(key, "[EMAIL_REDACTED]")

# 在初始化时注册清理函数
Traceloop.init(
    app_name="sanitized-app",
    span_processor_callback=sanitize_span_data
)
```

### 遥测控制

OpenLLMetry SDK 包含匿名使用情况收集功能。您可以：

```python
# 禁用遥测
Traceloop.init(
    app_name="no-telemetry-app",
    telemetry_enabled=False
)

# 或使用环境变量
import os
os.environ['TRACELOOP_TELEMETRY'] = 'FALSE'
```

## 📊 监控最佳实践

### 关键指标

监控以下关键指标：

1. **延迟指标**
   - LLM 调用响应时间
   - 端到端请求延迟
   - 向量搜索时间

2. **错误指标**  
   - API 调用失败率
   - 超时错误
   - 令牌限制错误

3. **使用指标**
   - 令牌消耗量
   - API 调用频率
   - 模型使用分布

4. **成本指标**
   - 每个请求的成本
   - 日/月总成本
   - 模型成本分析

### 警报设置

```python
# 示例：设置成本监控
@workflow(name="cost_monitored_workflow")
def monitor_costs():
    start_time = time.time()
    
    # 执行 LLM 调用
    response = expensive_llm_call()
    
    end_time = time.time()
    duration = end_time - start_time
    
    # 记录自定义指标
    with trace.get_tracer(__name__).start_as_current_span("cost_tracking") as span:
        span.set_attribute("cost.duration", duration)
        span.set_attribute("cost.estimated", calculate_cost(response))
        
        # 成本过高时发出警报
        if calculate_cost(response) > COST_THRESHOLD:
            span.add_event("high_cost_alert")
    
    return response
```

## 🌍 社区与支持

### 获取帮助

- **📖 官方文档**：[https://traceloop.com/docs/openllmetry/introduction](https://traceloop.com/docs/openllmetry/introduction)
- **💬 Slack 社区**：[https://traceloop.com/slack](https://traceloop.com/slack) - 与社区和 Traceloop 团队实时讨论
- **🐛 GitHub Issues**：[https://github.com/traceloop/openllmetry/issues](https://github.com/traceloop/openllmetry/issues) - 报告错误和问题
- **💡 GitHub Discussions**：[https://github.com/traceloop/openllmetry/discussions](https://github.com/traceloop/openllmetry/discussions) - 深入讨论和功能建议
- **🐦 Twitter**：[@traceloopdev](https://twitter.com/traceloopdev) - 获取最新消息

### 贡献指南

我们欢迎各种形式的贡献：

1. **报告问题**：发现 bug？请在 GitHub Issues 中报告
2. **功能建议**：有想法？在 Discussions 中分享
3. **代码贡献**：查看我们的[贡献指南](https://github.com/traceloop/openllmetry/blob/main/CONTRIBUTING.md)
4. **文档改进**：帮助我们改进文档

### 社区资源

- **示例代码**：[GitHub 示例仓库](https://github.com/traceloop/openllmetry/tree/main/packages/sample-app)
- **博客文章**：[Traceloop 博客](https://traceloop.com/blog)
- **视频教程**：[YouTube 频道](https://youtube.com/@traceloop)

## 📄 许可证

OpenLLMetry 基于 Apache 2.0 许可证开源。查看 [LICENSE](https://github.com/traceloop/openllmetry/blob/main/LICENSE) 文件了解详情。

## 🙏 致谢

特别感谢 [@patrickdebois](https://x.com/patrickdebois/status/1695518950715473991?s=46&t=zn2SOuJcSVq-Pe2Ysevzkg)，他建议了我们现在使用的这个很棒的仓库名称！

---

**需要帮助？**加入我们的 [Slack 社区](https://traceloop.com/slack)或查看我们的[文档](https://traceloop.com/docs/openllmetry/introduction)。

**有问题？**在 [GitHub Issues](https://github.com/traceloop/openllmetry/issues) 中创建一个问题。

**想要贡献？**查看我们的[贡献指南](https://github.com/traceloop/openllmetry/blob/main/CONTRIBUTING.md)开始吧！