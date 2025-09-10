# 课程材料RAG系统 - 双模型智能路由架构

source: https://github.com/https-deeplearning-ai/starting-ragchatbot-codebase

一个先进的检索增强生成（RAG）系统，使用**双模型智能路由架构**和语义搜索来回答关于课程材料的问题。

## 🚀 系统特性

### 核心架构 - V2.0 双模型智能路由
- **智能路由器**: 根据任务类型自动选择最适合的AI模型
- **DeepSeek-R1**: 专门处理复杂推理和对话任务
- **DeepSeek-V3**: 专门处理工具调用和函数执行
- **Claude支持**: 保留作为后备选项，确保高可用性
- **多提供商架构**: 支持Claude和DeepSeek的无缝切换

### 技术栈
- **前端**: HTML + JavaScript (原生JS)
- **后端**: FastAPI (Python 3.13+)
- **向量数据库**: ChromaDB + SentenceTransformer嵌入
- **AI提供商**: DeepSeek双模型 + Anthropic Claude后备
- **包管理**: uv（现代Python包管理器）

## 📋 先决条件

- Python 3.13或更高版本
- uv（Python包管理器）
- DeepSeek API密钥（主要AI提供商）
- Anthropic API密钥（可选，后备支持）
- **Windows用户**：使用Git Bash运行命令 - [下载Git for Windows](https://git-scm.com/downloads/win)

## 🛠️ 安装

### 1. 安装uv（如果尚未安装）
```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 安装Python依赖
```bash
uv sync
```

### 3. 环境配置

在根目录创建`.env`文件：

#### 双模型配置（推荐）:
```bash
# 主AI提供商 - DeepSeek双模型路由
LLM_PROVIDER=deepseek
LLM_API_KEY=your_deepseek_api_key_here
LLM_BASE_URL=https://llm.chutes.ai/v1

# 双模型配置
MODEL_REASON=deepseek-ai/DeepSeek-R1      # 推理模型
MODEL_TOOLCALL=deepseek-ai/DeepSeek-V3    # 工具调用模型

# 后备支持（可选）
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

#### Claude单模型配置（备选）:
```bash
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

## 🚀 运行应用程序

### 快速启动
```bash
chmod +x run.sh
./run.sh
```

### 手动启动
```bash
cd backend
uv run uvicorn app:app --reload --port 8000
```

### 访问地址
- **Web界面**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/courses

## 🧪 测试系统

项目包含完整的测试套件，按功能分类组织：

### 测试目录结构
```
tests/
├── integration/          # 集成测试
│   └── test_rag_integration.py    # 完整RAG流程测试
├── unit/                # 单元测试  
│   ├── test_ai_generator.py       # AI生成器测试
│   ├── test_deepseek_*.py         # DeepSeek连接测试
│   └── test_router*.py            # 智能路由器测试
└── debug/               # 调试脚本
    └── debug_function_calling.py  # 函数调用调试
```

### 运行测试

#### 完整RAG集成测试（推荐）:
```bash
uv run python tests/integration/test_rag_integration.py
```
验证内容:
- ✅ 向量检索系统
- ✅ 双模型智能路由  
- ✅ 工具调用机制
- ✅ 对话上下文保持
- ✅ 错误处理机制

#### AI生成器单元测试:
```bash
uv run python tests/unit/test_ai_generator.py
```

#### 路由器功能测试:
```bash
uv run python tests/unit/test_router_comprehensive.py
```

#### DeepSeek连接测试:
```bash
uv run python tests/unit/test_deepseek_connection.py
```

### 测试说明

- **集成测试**: 验证完整RAG流程，包括双模型协同工作
- **单元测试**: 验证各组件独立功能
- **调试脚本**: 用于开发时问题诊断

**测试结果示例**:
```
RAG系统集成测试结果: 7/7 测试通过
✅ 向量检索系统正常
✅ 双模型智能路由有效  
✅ 工具调用机制完善
✅ RAG端到端流程稳定
```

## 📖 架构文档

项目提供详细的架构文档：

### 核心文档
- [`CLAUDE.md`](CLAUDE.md) - 开发指南和项目上下文
- [`LLM_MIGRATION_GUIDE.md`](LLM_MIGRATION_GUIDE.md) - LLM迁移完整技术方案

### V2.0 架构文档
- [`docs/architecture/request_flow_analysis_v2.md`](docs/architecture/request_flow_analysis_v2.md) - 双模型架构流程分析
- [`docs/architecture/request_flow_diagram_v2.md`](docs/architecture/request_flow_diagram_v2.md) - 智能路由流程图

### 历史文档
- [`docs/legacy/`](docs/legacy/) - V1.0版本文档存档

## 🏗️ 项目结构

```
starting-ragchatbot-codebase/
├── backend/                    # 后端服务
│   ├── ai_generator.py            # 多提供商AI生成器 ⭐
│   ├── llm_router.py              # 智能路由器 🆕
│   ├── search_tools.py            # 搜索工具管理
│   ├── vector_store.py            # 向量数据库接口
│   ├── rag_system.py              # RAG系统核心
│   ├── config.py                  # 配置管理
│   └── app.py                     # FastAPI应用
├── frontend/                   # 前端界面
├── tests/                      # 测试套件 🆕
├── docs/                       # 文档系统 🆕
├── main.py                     # 项目入口
├── run.sh                      # 启动脚本
└── README.md                   # 本文档
```

## 🔧 配置选项

### 基础配置
```python
# config.py 主要配置项
LLM_PROVIDER = "deepseek"          # AI提供商选择
CHROMA_PATH = "./chroma_db"        # 向量数据库路径  
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 嵌入模型
MAX_RESULTS = 5                    # 最大搜索结果数
```

### 双模型路由配置
```python
# 智能路由设置
MODEL_REASON = "deepseek-ai/DeepSeek-R1"      # 推理任务
MODEL_TOOLCALL = "deepseek-ai/DeepSeek-V3"    # 工具调用任务  
LLM_BASE_URL = "https://llm.chutes.ai/v1"     # API端点
```

## 🚀 系统优势

### V2.0 双模型架构优势
- **任务导向优化**: 推理用R1，工具调用用V3，各自发挥优势
- **智能路由**: 自动选择最适合的模型，无需手动切换
- **成本控制**: 按需选择模型，优化API调用成本
- **高可用性**: 多提供商支持，自动降级机制

### 性能特性
- **响应速度**: 智能路由减少不必要的模型切换
- **准确性**: 专门模型处理专门任务
- **稳定性**: 完善的错误处理和重试机制
- **扩展性**: 支持新AI提供商的快速集成

## 🐛 故障排除

### 常见问题

**1. API连接失败**
```bash
# 检查API密钥配置
uv run python tests/unit/test_deepseek_connection.py
```

**2. 依赖安装问题**
```bash
# 重新安装依赖
uv sync --reinstall
```

**3. 模型路由异常**
```bash
# 运行路由器测试
uv run python tests/unit/test_router_comprehensive.py
```

**4. 向量数据库问题**
```bash
# 清理并重建向量数据库
rm -rf ./chroma_db
# 重新启动应用，系统将自动重建
```

### 调试模式
启动时添加环境变量开启详细日志：
```bash
DEBUG=1 uv run uvicorn app:app --reload --port 8000
```

## 📝 开发指南

### 添加新AI提供商
1. 在`ai_generator.py`中添加新的生成方法
2. 在`config.py`中添加相应配置
3. 更新`search_tools.py`支持新的工具格式
4. 编写相应的单元测试

### 扩展工具功能
1. 在`search_tools.py`中定义新工具类
2. 实现Claude和OpenAI两种格式定义
3. 在`rag_system.py`中注册新工具
4. 添加相应测试验证

## 📖 项目文档索引

### 🎯 入门指南
- **[RAG_SYSTEM_COMPLETE_GUIDE.md](RAG_SYSTEM_COMPLETE_GUIDE.md)** - 🆕 RAG系统完整指南（图文详解）

### 核心文档
- **[CLAUDE.md](CLAUDE.md)** - 开发指南和项目上下文
- **[LLM_MIGRATION_GUIDE.md](LLM_MIGRATION_GUIDE.md)** - LLM迁移完整技术方案

### V2.0 架构文档
- **[request_flow_analysis_v2.md](request_flow_analysis_v2.md)** - V2.0双模型架构流程分析
- **[request_flow_diagram_v2.md](request_flow_diagram_v2.md)** - V2.0智能路由流程图

### V1.0 归档文档
- **[request_flow_analysis.md](request_flow_analysis.md)** - V1.0架构流程分析
- **[request_flow_diagram.md](request_flow_diagram.md)** - V1.0系统流程图

## 📜 许可证

本项目基于原始DeepLearning.AI项目开发，保持开源许可证。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

---

**🎯 V2.0 总结**: 通过双模型智能路由架构，系统实现了AI任务的专业化处理，在保持高性能的同时提供了更好的用户体验和系统稳定性。智能路由器自动为不同类型的查询选择最适合的模型，确保了响应质量和成本效益的最佳平衡。