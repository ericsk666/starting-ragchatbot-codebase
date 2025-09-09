# 项目上下文和开发指南

## 项目概述
这是一个课程材料RAG（检索增强生成）系统，旨在通过语义搜索和AI驱动的响应来回答关于课程材料的问题。

### 技术栈
- **后端**: Python 3.13+, FastAPI, Uvicorn
- **向量数据库**: ChromaDB（用于语义搜索）
- **AI模型**: Anthropic Claude API
- **前端**: Web界面
- **包管理**: uv（Python包管理器）

## 项目结构
```
starting-ragchatbot-codebase/
├── backend/          # 后端服务代码
├── frontend/         # 前端界面代码
├── docs/            # 文档目录
├── main.py          # 主入口文件
├── run.sh           # 启动脚本
├── pyproject.toml   # Python项目配置
└── .env.example     # 环境变量示例
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
4. **AI生成**: 使用Claude API生成智能回答
5. **Web界面**: 提供用户友好的交互界面

### API端点
- `GET /`: 主页面
- `GET /docs`: API文档（Swagger UI）
- `POST /query`: 处理用户查询请求
- `POST /upload`: 上传课程材料

### 环境配置
必需的环境变量：
- `ANTHROPIC_API_KEY`: Claude API密钥

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

## 开发优先级
1. 核心RAG功能的稳定性和准确性
2. 用户体验和界面友好性
3. 性能优化和响应速度
4. 扩展性和维护性
- 总是使用 uv 来运行server ,不要直接使用 pip
- 确保使用 uv 来管理所有依赖