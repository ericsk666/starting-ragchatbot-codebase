# 项目结构说明

## 📁 目录结构

```
starting-ragchatbot-codebase/
├── backend/                    # 后端服务
│   ├── ai_generator.py        # AI生成器（多提供商支持）
│   ├── llm_router.py          # 智能路由器
│   ├── rag_system.py          # RAG核心系统
│   ├── session_manager.py     # 会话管理
│   ├── config.py              # 配置管理
│   └── app.py                 # FastAPI应用
│
├── frontend/                   # 前端界面
│   ├── index.html             # 主页面
│   ├── style.css              # 样式文件
│   └── script.js              # JavaScript逻辑
│
├── tests/                      # 测试套件
│   ├── unit/                  # 单元测试
│   │   ├── test_ai_generator.py
│   │   ├── test_router*.py
│   │   └── test_*.py
│   ├── integration/           # 集成测试
│   │   └── test_rag_integration.py
│   ├── debug/                 # 调试测试
│   │   └── debug_*.py
│   └── html_demos/           # HTML测试演示
│       ├── rag_system_demo*.html
│       └── test_*.html
│
├── project_docs/              # 项目文档
│   ├── planning/             # 计划文档
│   │   ├── NEW_CHAT_FEATURE_PLAN.md
│   │   ├── HTML_DEMO_IMPROVEMENT_PLAN.md
│   │   └── UI_OPTIMIZATION_PLAN.md
│   ├── technical/            # 技术文档
│   │   ├── LLM_MIGRATION_GUIDE.md
│   │   ├── RAG_SYSTEM_COMPLETE_GUIDE.md
│   │   └── request_flow_*.md
│   ├── implementation/       # 实施记录
│   │   ├── FIX_*.md
│   │   └── sources_links_implementation.md
│   └── quality/             # 质量报告
│       └── QUALITY_CHECK_REPORT.md
│
├── docs/                      # 课程材料（RAG数据源）
│   └── *.txt                 # 课程文本文件
│
├── chroma_db/                # ChromaDB向量数据库
│   └── (自动生成的数据库文件)
│
├── .venv/                    # Python虚拟环境
├── .vscode/                  # VSCode配置
├── .git/                     # Git版本控制
│
├── README.md                 # 项目说明
├── CLAUDE.md                # Claude开发指南
├── PROJECT_STRUCTURE.md    # 本文件
├── run.sh                   # 启动脚本
├── main.py                  # Python主入口
├── pyproject.toml          # 项目配置
├── uv.lock                 # 依赖锁定
├── .env                    # 环境变量
├── .env.example           # 环境变量示例
├── .gitignore            # Git忽略规则
└── .python-version       # Python版本
```

## 📂 目录说明

### 核心代码目录

#### `backend/` - 后端服务
- **作用**：提供API服务和业务逻辑
- **主要文件**：
  - `app.py`: FastAPI应用主文件
  - `rag_system.py`: RAG系统核心实现
  - `ai_generator.py`: 多AI提供商支持
  - `llm_router.py`: 智能模型路由

#### `frontend/` - 前端界面
- **作用**：用户交互界面
- **技术栈**：原生HTML/CSS/JavaScript
- **特点**：响应式设计，紫色主题

#### `docs/` - 课程材料
- **作用**：RAG系统的知识库来源
- **内容**：课程文本文件
- **格式**：支持txt, pdf等格式

### 测试目录

#### `tests/unit/` - 单元测试
- **内容**：独立功能测试
- **覆盖**：AI生成器、路由器、过滤器等

#### `tests/integration/` - 集成测试
- **内容**：系统集成测试
- **覆盖**：完整RAG流程测试

#### `tests/html_demos/` - HTML演示
- **内容**：前端功能演示页面
- **用途**：可视化测试和演示

### 文档目录

#### `project_docs/planning/` - 计划文档
- **内容**：功能规划、设计方案
- **格式**：Markdown文档

#### `project_docs/technical/` - 技术文档
- **内容**：技术指南、架构说明
- **重要文档**：
  - LLM迁移指南
  - RAG系统完整指南

#### `project_docs/implementation/` - 实施记录
- **内容**：问题修复、功能实现记录
- **用途**：开发过程追踪

#### `project_docs/quality/` - 质量文档
- **内容**：测试报告、质量检查
- **用途**：质量保证记录

## 🚀 快速开始

### 1. 安装依赖
```bash
uv sync
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，设置API密钥
```

### 3. 启动服务
```bash
./run.sh
# 或
cd backend && uv run uvicorn app:app --reload --port 8000
```

### 4. 访问应用
- 主界面：http://localhost:8000
- API文档：http://localhost:8000/docs

## 🧪 运行测试

### 单元测试
```bash
cd tests/unit
uv run python test_ai_generator.py
```

### 集成测试
```bash
cd tests/integration
uv run python test_rag_integration.py
```

### HTML演示
直接在浏览器中打开 `tests/html_demos/` 下的HTML文件

## 📝 开发规范

1. **代码位置**：
   - 后端代码放在 `backend/`
   - 前端代码放在 `frontend/`
   - 测试代码放在 `tests/`

2. **文档管理**：
   - 技术文档放在 `project_docs/technical/`
   - 计划文档放在 `project_docs/planning/`
   - 实施记录放在 `project_docs/implementation/`

3. **命名规范**：
   - Python文件：snake_case
   - 测试文件：test_*.py
   - 文档文件：UPPER_SNAKE_CASE.md

## 🔧 维护指南

### 添加新功能
1. 在 `project_docs/planning/` 创建计划文档
2. 在相应目录开发代码
3. 在 `tests/` 添加测试
4. 更新相关文档

### 问题修复
1. 在 `project_docs/implementation/` 记录问题
2. 修复代码
3. 添加测试用例
4. 更新文档

### 文档更新
1. 技术变更更新 `project_docs/technical/`
2. 质量检查更新 `project_docs/quality/`
3. 重要变更更新 `README.md`

## 📊 项目统计

- **代码文件数**：~30个
- **测试文件数**：~20个
- **文档文件数**：~15个
- **总代码行数**：~5000行

## 🏷️ 版本信息

- **Python版本**：3.13+
- **框架版本**：FastAPI 0.104+
- **向量数据库**：ChromaDB 1.0+
- **AI模型**：DeepSeek/Claude

---

*最后更新：2024-12-XX*
*维护者：开发团队*