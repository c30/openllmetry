# OpenLLMetry 模块关系图 Module Relationship Diagram

本文档描述了 OpenLLMetry 仓库中各个模块之间的关系和依赖结构。
This document describes the relationships and dependency structure between modules in the OpenLLMetry repository.

## 概览 Overview

OpenLLMetry 是一个基于 OpenTelemetry 的 LLM 应用可观测性框架，包含 31 个独立的 Python 包，通过 Nx 工作空间进行管理。
OpenLLMetry is an OpenTelemetry-based observability framework for LLM applications, containing 31 independent Python packages managed through an Nx workspace.

### 包分类 Package Categories

| 类别 Category | 数量 Count | 描述 Description |
|---------------|------------|------------------|
| 核心组件 Core Components | 2 | SDK 和语义约定 |
| LLM 提供商 LLM Providers | 15 | 各种 LLM 服务的插桩包 |
| 向量数据库 Vector Databases | 7 | 向量数据库的插桩包 |
| 框架 Frameworks | 5 | AI 框架的插桩包 |
| 示例应用 Sample Applications | 1 | 演示应用程序 |
| 其他 Others | 1 | 协议插桩包 |

## 核心组件 Core Components

### 1. traceloop-sdk
- **描述**: Traceloop 软件开发工具包 (SDK)
- **角色**: 整个框架的中心枢纽，集成所有插桩包
- **依赖**: 依赖于语义约定包和所有插桩包

### 2. opentelemetry-semantic-conventions-ai
- **描述**: AI 应用的 OpenTelemetry 语义约定扩展
- **角色**: 定义 AI 相关的标准化语义约定
- **依赖**: 无本地依赖，被所有插桩包使用

## LLM 提供商插桩包 LLM Provider Instrumentations

支持以下 LLM 提供商：

| 包名 Package | 提供商 Provider | 描述 Description |
|-------------|----------------|------------------|
| opentelemetry-instrumentation-openai | OpenAI | OpenAI 和 Azure OpenAI 服务 |
| opentelemetry-instrumentation-anthropic | Anthropic | Claude 系列模型 |
| opentelemetry-instrumentation-cohere | Cohere | Cohere AI 服务 |
| opentelemetry-instrumentation-ollama | Ollama | 本地 LLM 运行时 |
| opentelemetry-instrumentation-mistralai | Mistral AI | Mistral AI 服务 |
| opentelemetry-instrumentation-google-generativeai | Google | Gemini 模型服务 |
| opentelemetry-instrumentation-bedrock | AWS Bedrock | AWS 管理的 AI 服务 |
| opentelemetry-instrumentation-vertexai | Google Cloud | Vertex AI 服务 |
| opentelemetry-instrumentation-replicate | Replicate | AI 模型托管平台 |
| opentelemetry-instrumentation-together | Together AI | 开源模型 API |
| opentelemetry-instrumentation-alephalpha | Aleph Alpha | 欧洲 AI 提供商 |
| opentelemetry-instrumentation-groq | Groq | 高速推理芯片 |
| opentelemetry-instrumentation-watsonx | IBM Watsonx | IBM 企业 AI 平台 |
| opentelemetry-instrumentation-sagemaker | AWS SageMaker | AWS 机器学习平台 |
| opentelemetry-instrumentation-openai-agents | OpenAI Agents | OpenAI 代理框架 |

## 向量数据库插桩包 Vector Database Instrumentations

支持以下向量数据库：

| 包名 Package | 数据库 Database | 描述 Description |
|-------------|----------------|------------------|
| opentelemetry-instrumentation-pinecone | Pinecone | 托管向量数据库 |
| opentelemetry-instrumentation-qdrant | Qdrant | 开源向量搜索引擎 |
| opentelemetry-instrumentation-weaviate | Weaviate | 开源向量数据库 |
| opentelemetry-instrumentation-chromadb | ChromaDB | 嵌入式向量数据库 |
| opentelemetry-instrumentation-milvus | Milvus | 开源向量数据库 |
| opentelemetry-instrumentation-lancedb | LanceDB | 开源向量数据库 |
| opentelemetry-instrumentation-marqo | Marqo | 多模态搜索引擎 |

## 框架插桩包 Framework Instrumentations

支持以下 AI 框架：

| 包名 Package | 框架 Framework | 描述 Description |
|-------------|----------------|------------------|
| opentelemetry-instrumentation-langchain | LangChain | 流行的 LLM 应用开发框架 |
| opentelemetry-instrumentation-llamaindex | LlamaIndex | RAG 应用开发框架 |
| opentelemetry-instrumentation-haystack | Haystack | NLP 框架 |
| opentelemetry-instrumentation-crewai | CrewAI | 多代理 AI 系统 |
| opentelemetry-instrumentation-transformers | Transformers | HuggingFace Transformers 库 |

## 其他组件 Other Components

### opentelemetry-instrumentation-mcp
- **描述**: 模型上下文协议 (Model Context Protocol) 插桩
- **用途**: 支持 MCP 协议的可观测性

### sample-app
- **描述**: 示例应用程序
- **用途**: 演示如何使用 Traceloop SDK 和各种插桩包

## 依赖关系 Dependency Relationships

### 主要依赖流 Main Dependency Flow

```
traceloop-sdk (核心 SDK)
├── opentelemetry-semantic-conventions-ai (语义约定)
├── [所有 LLM 提供商插桩包]
├── [所有向量数据库插桩包]
├── [所有框架插桩包]
└── [其他插桩包]

各插桩包 → opentelemetry-semantic-conventions-ai (使用语义约定)
sample-app → traceloop-sdk (使用 SDK)
```

### 包间关系类型 Package Relationship Types

1. **直接依赖 Direct Dependencies**: traceloop-sdk 依赖所有插桩包
2. **语义使用 Semantic Usage**: 所有插桩包使用语义约定包
3. **用户应用 User Applications**: 示例应用使用 SDK

## 架构设计原则 Architecture Design Principles

### 1. 模块化设计 Modular Design
- 每个插桩包都是独立的，可以单独使用
- 通过 SDK 提供统一的入口点和配置

### 2. 标准化 Standardization
- 所有插桩包遵循统一的语义约定
- 基于 OpenTelemetry 标准实现

### 3. 可扩展性 Extensibility
- 易于添加新的 LLM 提供商或向量数据库支持
- 插件式架构便于第三方扩展

### 4. 松耦合 Loose Coupling
- 各组件之间保持松耦合
- 用户可以选择性地使用特定的插桩包

## 使用场景 Usage Scenarios

### 场景 1: 使用 SDK (推荐)
```python
from traceloop.sdk import Traceloop
Traceloop.init()  # 自动启用所有已安装的插桩
```

### 场景 2: 使用特定插桩包
```python
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
OpenAIInstrumentor().instrument()
```

### 场景 3: 自定义配置
```python
from traceloop.sdk import Traceloop
from traceloop.sdk.instruments import Instruments

Traceloop.init(
    instruments={Instruments.OPENAI, Instruments.PINECONE}
)
```

## 开发贡献 Development Contributions

### 添加新插桩包 Adding New Instrumentations

1. 在 `packages/` 目录创建新包
2. 遵循命名约定: `opentelemetry-instrumentation-{provider}`
3. 实现 `{Provider}Instrumentor` 类
4. 使用语义约定包中的标准
5. 在 traceloop-sdk 中添加依赖
6. 添加相应的测试和文档

### 项目结构 Project Structure

```
openllmetry/
├── packages/
│   ├── traceloop-sdk/                     # 核心 SDK
│   ├── opentelemetry-semantic-conventions-ai/  # 语义约定
│   ├── opentelemetry-instrumentation-*/   # 各种插桩包
│   └── sample-app/                        # 示例应用
├── docs/                                  # 文档和图表
├── scripts/                               # 构建脚本
└── nx.json                               # Nx 工作空间配置
```

## 版本管理 Version Management

- 所有包使用语义版本控制
- 核心组件和插桩包版本同步
- 通过 Poetry 管理依赖关系

## 测试策略 Testing Strategy

- 使用 VCR 录制的测试用例
- 每个插桩包都有独立的测试套件
- 集成测试验证端到端功能

## 部署和发布 Deployment and Release

- 每个包独立发布到 PyPI
- 通过 GitHub Actions 自动化 CI/CD
- 支持多种 Python 版本 (3.9+)

---

*此文档由自动化脚本生成，描述了 OpenLLMetry 项目的模块关系。*
*This document is generated by automated scripts and describes the module relationships of the OpenLLMetry project.*