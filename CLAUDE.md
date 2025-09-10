# 项目上下文和开发指南

## 项目概述
这是一个课程材料RAG（检索增强生成）系统，旨在通过语义搜索和AI驱动的响应来回答关于课程材料的问题。

### 技术栈
- **后端**: Python 3.13+, FastAPI, Uvicorn
- **向量数据库**: ChromaDB（用于语义搜索）
- **AI模型**: 
  - **V2.0 主架构**: DeepSeek双模型智能路由（R1推理 + V3工具调用）
  - **后备支持**: Anthropic Claude API
- **前端**: Web界面
- **包管理**: uv（Python包管理器）

## 项目结构
```
starting-ragchatbot-codebase/
├── backend/              # 后端服务代码
│   ├── ai_generator.py    # 多提供商AI生成器 (V2.0新增)
│   ├── llm_router.py       # 智能路由器 (V2.0新增)
│   ├── config.py           # 配置管理
│   └── ...                 # 其他核心模块
├── frontend/             # 前端界面代码
├── docs/                 # 课程材料目录
├── tests/                # 测试套件 (V2.0新增)
│   ├── integration/        # 集成测试
│   └── unit/               # 单元测试
├── main.py               # 主入口文件
├── run.sh                # 启动脚本
├── pyproject.toml        # Python项目配置
└── .env                  # 环境变量配置
```

## 开发要求

### 质量标准
1. **深度思考**: 每个开发步骤都需要进行ultra thinking深度思考
2. **遵循设计**: 严格遵循项目设计方案和架构
3. **代码质量**: 
   - 遵循Python PEP8规范
   - 使用类型注解
   - 编写清晰的注释和文档字符串
4. **测试覆盖**: 为新功能编写单元测试和集成测试

### 开发流程
1. **分析需求**: 深入理解用户需求和使用场景
2. **设计方案**: 制定详细的技术实现方案
3. **实现功能**: 按照设计方案实现功能
4. **质量检查**: 代码审查、测试、性能优化
5. **文档更新**: 更新相关文档和README
6. **版本控制**: 提交代码到Git仓库

### TODO管理
- 使用TodoWrite工具管理任务
- 保持任务状态实时更新
- 完成任务后立即标记为completed
- 质量不达标不能继续下一步

### 关键功能模块
1. **文档处理**: 支持多种格式的课程材料上传和处理
2. **向量化存储**: 将文档内容转换为向量并存储在ChromaDB
3. **语义搜索**: 基于用户查询进行相似度搜索
4. **AI生成**: 
   - V2.0: 双模型智能路由（DeepSeek-R1 + DeepSeek-V3）
   - 后备: Claude API支持
5. **Web界面**: 提供用户友好的交互界面

#### V2.0 新增核心模块
6. **智能路由器** (llm_router.py): 根据任务类型自动选择最优模型
7. **多提供商支持** (ai_generator.py): 统一接口支持多种AI提供商
8. **格式转换器**: Claude工具格式↔OpenAI格式自动转换

### API端点
- `GET /`: 主页面
- `GET /docs`: API文档（Swagger UI）
- `POST /api/query`: 处理用户查询请求（修正路径）
- `GET /api/courses`: 获取课程统计信息（V2.0新增）

### 环境配置

#### V2.0 双模型配置（推荐）
```bash
LLM_PROVIDER=deepseek
LLM_API_KEY=your_deepseek_api_key
LLM_BASE_URL=https://llm.chutes.ai/v1
MODEL_REASON=deepseek-ai/DeepSeek-R1      # 推理模型
MODEL_TOOLCALL=deepseek-ai/DeepSeek-V3    # 工具调用模型
```

#### Claude配置（后备选项）
```bash
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=your_anthropic_api_key
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

### 运行命令
```bash
# 安装依赖
uv sync

# 启动应用
./run.sh
# 或
cd backend && uv run uvicorn app:app --reload --port 8000
```

### 访问地址
- Web界面: http://localhost:8000
- API文档: http://localhost:8000/docs

## 注意事项
1. Windows用户需使用Git Bash运行命令
2. 确保Python版本 >= 3.13
3. API密钥保密，不要提交到版本控制
4. 定期更新依赖包以获取安全更新

## V2.0 架构特性

### 双模型智能路由
- **DeepSeek-R1**: 处理复杂推理和对话任务
- **DeepSeek-V3**: 专门处理工具调用和函数执行
- **智能选择**: 路由器自动根据任务类型选择最优模型
- **成本优化**: 按需使用不同模型，平衡性能与成本

### 工具系统
- **双格式支持**: 同时支持Claude和OpenAI工具格式
- **自动转换**: 格式间无缝转换，提高兼容性
- **搜索增强**: 向量搜索工具与AI生成深度集成

## 测试指南

### 运行测试
```bash
# 完整RAG集成测试
uv run python tests/integration/test_rag_integration.py

# AI生成器单元测试
uv run python tests/unit/test_ai_generator.py

# 路由器功能测试
uv run python tests/unit/test_router_comprehensive.py

# DeepSeek连接测试
uv run python tests/unit/test_deepseek_connection.py
```

### 测试覆盖
- ✅ 向量检索系统
- ✅ 双模型智能路由
- ✅ 工具调用机制
- ✅ 对话上下文保持
- ✅ 错误处理机制

## 故障排查

### 常见问题解决
1. **API连接失败**: 检查.env中的API密钥配置
2. **模型路由异常**: 运行路由器测试验证配置
3. **向量数据库问题**: 删除chroma_db目录后重启
4. **依赖安装失败**: 使用`uv sync --reinstall`重新安装

### 调试模式
```bash
DEBUG=1 uv run uvicorn app:app --reload --port 8000
```

## 开发优先级
1. 核心RAG功能的稳定性和准确性
2. 用户体验和界面友好性
3. 性能优化和响应速度
4. 扩展性和维护性
- 总是使用 uv 来运行server ,不要直接使用 pip
- 确保使用 uv 来管理所有依赖

## 版本历史
- **V2.0 (当前)**: 双模型智能路由架构，支持DeepSeek-R1/V3
- **V1.0**: 基础RAG系统，单一Claude模型