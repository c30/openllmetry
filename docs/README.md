# OpenLLMetry 模块关系图 Module Relationship Documentation

本目录包含了 OpenLLMetry 项目的模块关系图和相关文档。

## 文件说明 File Descriptions

| 文件名 | 类型 | 描述 |
|--------|------|------|
| `MODULE_RELATIONSHIPS.md` | 文档 | 详细的模块关系说明文档 |
| `openllmetry_modules.svg` | 图表 | 可缩放的矢量格式模块关系图 |
| `openllmetry_modules.png` | 图表 | PNG 格式模块关系图 |
| `openllmetry_modules.dot` | 源码 | GraphViz DOT 格式源文件 |
| `openllmetry_modules.mmd` | 源码 | Mermaid 格式源文件 |
| `openllmetry_summary.json` | 数据 | 模块统计信息 JSON 文件 |

## 快速查看 Quick View

### 项目统计 Project Statistics

- **总包数**: 31 个 Python 包
- **核心组件**: 2 个 (SDK + 语义约定)
- **LLM 提供商**: 15 个插桩包
- **向量数据库**: 7 个插桩包
- **AI 框架**: 5 个插桩包
- **示例应用**: 1 个
- **其他组件**: 1 个

### 核心架构 Core Architecture

```
traceloop-sdk (主 SDK)
├── 语义约定 (opentelemetry-semantic-conventions-ai)
├── LLM 插桩包 (OpenAI, Anthropic, Cohere, 等)
├── 向量数据库插桩包 (Pinecone, Qdrant, Weaviate, 等)
├── 框架插桩包 (LangChain, LlamaIndex, 等)
└── 示例应用 (演示用法)
```

## 查看图表 Viewing Diagrams

### 在线查看 Online Viewing

1. **SVG 格式**: 直接在浏览器中打开 `openllmetry_modules.svg`
2. **Mermaid 格式**: 复制 `openllmetry_modules.mmd` 内容到 [Mermaid Live Editor](https://mermaid.live/)

### 本地查看 Local Viewing

1. **GraphViz**: 
   ```bash
   dot -Tpng openllmetry_modules.dot -o output.png
   dot -Tsvg openllmetry_modules.dot -o output.svg
   ```

2. **Mermaid CLI**:
   ```bash
   mmdc -i openllmetry_modules.mmd -o output.png
   mmdc -i openllmetry_modules.mmd -o output.svg
   ```

## 图表说明 Diagram Legend

### 节点类型 Node Types

- 🟦 **方形**: 核心组件 (Core Components)
- 🟡 **椭圆形**: LLM 提供商 (LLM Providers)
- 🟨 **椭圆形**: 向量数据库 (Vector Databases)
- 🟩 **椭圆形**: AI 框架 (AI Frameworks)
- 🟪 **菱形**: 示例应用 (Sample Applications)
- ⬢ **六边形**: 其他组件 (Other Components)

### 连接类型 Connection Types

- **实线箭头**: 本地包依赖 (Local Package Dependencies)
- **虚线箭头**: 使用关系 (Usage Relationships)

## 更新图表 Updating Diagrams

如需更新模块关系图，请运行：

```bash
python scripts/generate_module_diagram.py
```

该脚本会：
1. 分析 `packages/` 目录下的所有包
2. 解析 `pyproject.toml` 文件的依赖关系
3. 生成新的图表文件
4. 更新统计信息

## 技术细节 Technical Details

### 依赖分析 Dependency Analysis

图表通过以下方式生成：
1. 扫描所有 `pyproject.toml` 文件
2. 提取 Poetry 依赖信息
3. 识别本地路径依赖 (`path = "../package"`)
4. 按功能分类包 (LLM、向量数据库、框架等)
5. 生成可视化图表

### 分类规则 Categorization Rules

- **核心组件**: `traceloop-sdk`, `opentelemetry-semantic-conventions-ai`
- **LLM 提供商**: 包含提供商名称的插桩包
- **向量数据库**: 包含数据库名称的插桩包
- **框架**: 包含框架名称的插桩包
- **示例**: 包含 "sample" 的包
- **其他**: 剩余的包 (如 MCP 协议)

---

*有关详细的模块关系说明，请参阅 `MODULE_RELATIONSHIPS.md`*