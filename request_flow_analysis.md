# 课程材料RAG系统 - 请求处理流程分析

## 系统架构概览
- **前端**: HTML + JavaScript (原生JS)
- **后端**: FastAPI (Python)
- **向量数据库**: ChromaDB
- **AI模型**: Anthropic Claude API
- **嵌入模型**: SentenceTransformer

## 完整请求处理流程

### 1. 前端用户交互入口
**文件**: `frontend/index.html`, `frontend/script.js`

#### 用户输入方式:
- 文本输入框 (`chatInput`) - 用户直接输入问题
- 快捷建议按钮 - 预设的常见问题
- Enter键或发送按钮触发查询

#### 页面加载初始化:
```javascript
// script.js:11-22
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();    // 设置事件监听
    createNewSession();       // 创建新会话
    loadCourseStats();        // 加载课程统计信息
});
```

### 2. 前端发送请求流程
**文件**: `frontend/script.js:45-96`

#### 请求发送步骤:
1. **获取用户输入** - 从输入框获取查询内容
2. **禁用输入** - 防止重复提交
3. **显示用户消息** - 在聊天界面显示用户问题
4. **显示加载动画** - 创建loading消息提示用户
5. **发送POST请求**:
   ```javascript
   // script.js:63-72
   fetch(`${API_URL}/query`, {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({
           query: query,
           session_id: currentSessionId
       })
   })
   ```
6. **处理响应** - 更新session_id，显示AI回答和来源
7. **错误处理** - 显示错误信息
8. **恢复输入** - 重新启用输入框

### 3. 后端API路由接收
**文件**: `backend/app.py:56-74`

#### API端点: `POST /api/query`
```python
@app.post("/api/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    # 创建或获取session_id
    session_id = request.session_id or rag_system.session_manager.create_session()
    
    # 调用RAG系统处理查询
    answer, sources = rag_system.query(request.query, session_id)
    
    # 返回响应
    return QueryResponse(
        answer=answer,
        sources=sources,
        session_id=session_id
    )
```

### 4. RAG系统业务逻辑处理
**文件**: `backend/rag_system.py:102-140`

#### 核心处理流程:
1. **构建提示词** - 为AI准备查询提示
2. **获取会话历史** - 从SessionManager获取历史对话
3. **调用AI生成器**:
   ```python
   # rag_system.py:122-127
   response = self.ai_generator.generate_response(
       query=prompt,
       conversation_history=history,
       tools=self.tool_manager.get_tool_definitions(),
       tool_manager=self.tool_manager
   )
   ```
4. **获取搜索来源** - 从ToolManager获取搜索结果来源
5. **更新会话历史** - 保存本轮对话

### 5. 向量数据库查询过程
**文件**: `backend/vector_store.py`, `backend/search_tools.py`

#### 查询执行流程:

##### 5.1 工具定义与注册
```python
# search_tools.py:27-50
CourseSearchTool提供三个参数:
- query: 搜索内容
- course_name: 课程名称（支持模糊匹配）
- lesson_number: 课程编号
```

##### 5.2 向量搜索执行
```python
# vector_store.py:61-100
def search():
    1. 解析课程名称 - 使用向量相似度找到最匹配的课程
    2. 构建过滤条件 - 根据课程和课号过滤
    3. 执行向量查询 - 在ChromaDB中搜索相关内容
    4. 返回搜索结果 - 包含文档、元数据和距离分数
```

##### 5.3 ChromaDB存储结构:
- **course_catalog集合**: 存储课程元数据（标题、讲师、链接等）
- **course_content集合**: 存储课程内容块（按chunk分割的文本）

### 6. AI生成响应过程
**文件**: `backend/ai_generator.py:43-135`

#### Claude API调用流程:

##### 6.1 初始请求
```python
# ai_generator.py:60-82
1. 构建系统提示词（包含历史对话）
2. 准备API参数（model, temperature, max_tokens）
3. 添加工具定义（如果有）
4. 发送请求到Claude API
```

##### 6.2 工具调用处理
```python
# ai_generator.py:89-135
如果AI决定使用工具:
1. 执行工具调用（搜索课程内容）
2. 收集工具结果
3. 将结果作为新消息添加
4. 再次调用Claude生成最终响应
```

##### 6.3 系统提示词策略:
- 仅对课程特定问题使用搜索工具
- 每次查询最多一次搜索
- 提供简洁、教育性的回答
- 不包含元评论或搜索过程说明

### 7. 响应返回链路

#### 7.1 后端响应组装
```
RAG系统 -> API端点 -> FastAPI响应
         ↓
    {
        "answer": "AI生成的回答",
        "sources": ["课程1 - 第2课", ...],
        "session_id": "会话ID"
    }
```

#### 7.2 前端响应处理
```javascript
// script.js:83-85
1. 移除加载动画
2. 显示AI回答（Markdown渲染）
3. 显示来源信息（可折叠）
4. 滚动到最新消息
```

## 关键组件交互图

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   前端界面   │────>│  FastAPI后端  │────>│  RAG系统    │
│             │<────│              │<────│             │
└─────────────┘     └──────────────┘     └─────────────┘
                            │                    │
                            │                    ├────────────┐
                            │                    ↓            ↓
                    ┌───────────────┐    ┌─────────────┐ ┌──────────┐
                    │  静态文件服务  │    │  向量数据库  │ │ Claude AI│
                    └───────────────┘    │  ChromaDB   │ │   API    │
                                        └─────────────┘ └──────────┘
```

## 数据流特点

1. **会话管理**: 通过session_id维护对话上下文
2. **工具调用**: AI可自主决定是否搜索数据库
3. **向量搜索**: 支持语义搜索和精确过滤
4. **来源追踪**: 每个回答都包含信息来源
5. **错误处理**: 各层都有异常捕获和处理

## 性能优化点

1. **缓存策略**: 
   - 预构建的系统提示词
   - 基础API参数复用
   
2. **数据库优化**:
   - 分离目录和内容集合
   - 避免重复处理已存在的课程
   
3. **前端优化**:
   - 禁用输入防止重复提交
   - 异步加载课程统计
   - 使用loading状态提升用户体验

## 安全考虑

1. **CORS配置**: 允许跨域请求
2. **环境变量**: API密钥通过.env管理
3. **输入验证**: Pydantic模型验证请求数据
4. **错误处理**: 避免敏感信息泄露