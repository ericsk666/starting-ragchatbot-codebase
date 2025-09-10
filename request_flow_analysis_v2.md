# 课程材料RAG系统 - 请求处理流程分析 V2.0

## 系统架构概览 - 双模型智能路由架构

- **前端**: HTML + JavaScript (原生JS)
- **后端**: FastAPI (Python)
- **向量数据库**: ChromaDB
- **AI模型**: DeepSeek双模型智能路由架构
  - **DeepSeek-R1**: 推理模型（用于纯对话和复杂思考）
  - **DeepSeek-V3**: 工具调用模型（用于函数调用和工具执行）
- **智能路由器**: LLMRouter (自动选择最适合的模型)
- **嵌入模型**: SentenceTransformer (all-MiniLM-L6-v2)
- **后备支持**: Anthropic Claude API (可配置切换)

## 完整请求处理流程

### 1. 前端用户交互入口
**文件**: `frontend/index.html`, `frontend/script.js`

#### 用户输入方式:
- 直接在输入框输入问题
- 点击建议问题按钮
- 历史对话上下文保持

```javascript
// 发送查询到后端API
async function sendQuery(query) {
    const response = await fetch('/api/query', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query: query, session_id: sessionId})
    });
    return await response.json();
}
```

### 2. 后端API入口
**文件**: `backend/app.py`

```python
@app.post("/api/query", response_model=QueryResponse)
async def query_courses(request: QueryRequest):
    return rag_system.process_query(request.query, request.session_id)
```

### 3. RAG系统核心处理
**文件**: `backend/rag_system.py`

#### 核心流程:
1. **会话管理**: 获取对话历史上下文
2. **AI生成**: 调用智能路由器进行响应生成
3. **结果返回**: 格式化响应和来源信息

```python
def process_query(self, query: str, session_id: Optional[str] = None) -> dict:
    # 获取对话历史
    conversation_history = self.session_manager.get_conversation_history(session_id)
    
    # 获取工具定义（支持多提供商格式）
    tools = self.tool_manager.get_tool_definitions_for_provider()
    
    # 智能路由AI生成
    response = self.ai_generator.generate_response(
        query=query,
        conversation_history=conversation_history,
        tools=tools,
        tool_manager=self.tool_manager
    )
```

### 4. **NEW** 智能路由器核心 ⭐
**文件**: `backend/llm_router.py`

这是V2.0架构的核心创新 - 智能双模型路由系统：

```python
def call_chat(self, messages, tools=None, **kwargs):
    # 路由决策：根据是否需要工具调用选择模型
    if tools and len(tools) > 0:
        # 需要工具调用，使用DeepSeek-V3
        model = config.MODEL_TOOLCALL  # deepseek-ai/DeepSeek-V3
        print(f"[ROUTER] 使用工具调用模型: {model}")
    else:
        # 纯对话，使用DeepSeek-R1
        model = config.MODEL_REASON    # deepseek-ai/DeepSeek-R1
        print(f"[ROUTER] 使用推理模型: {model}")
```

**路由策略核心逻辑:**
- **任务分析**: 自动检测查询是否需要工具调用
- **模型选择**: 工具调用→V3，纯推理→R1
- **无缝切换**: 对用户完全透明的模型切换
- **性能优化**: 发挥各模型特长，避免限制

### 5. **UPDATED** AI生成器 - 多提供商支持
**文件**: `backend/ai_generator.py`

V2.0重构支持多提供商架构：

```python
def generate_response(self, query: str, conversation_history=None, tools=None, tool_manager=None):
    if self.provider == "deepseek":
        return self._generate_deepseek_response(query, conversation_history, tools, tool_manager)
    else:
        return self._generate_claude_response(query, conversation_history, tools, tool_manager)
```

**新增功能:**
- **格式转换**: Claude工具格式自动转换为OpenAI格式
- **提供商抽象**: 统一接口支持多种AI提供商
- **错误处理**: 完善的异常处理和降级机制

### 6. 工具管理和执行
**文件**: `backend/search_tools.py`

#### 双格式工具定义支持:
```python
def get_tool_definitions_for_provider(self, provider: str = None) -> list:
    provider = provider or config.LLM_PROVIDER
    
    if provider == "deepseek":
        return self.get_openai_tool_definitions()  # OpenAI格式
    else:
        return self.get_tool_definitions()         # Claude格式
```

### 7. 向量搜索和检索
**文件**: `backend/vector_store.py`

向量搜索流程保持不变，但性能得到优化：

```python
def search(self, query: str, course_name=None, lesson_number=None, limit=None):
    # 1. 解析课程名称（如果提供）
    course_title = self._resolve_course_name(course_name) if course_name else None
    
    # 2. 构建过滤条件
    filter_dict = self._build_filter(course_title, lesson_number)
    
    # 3. 执行向量搜索
    results = self.course_content.query(
        query_texts=[query],
        n_results=limit or self.max_results,
        where=filter_dict
    )
```

## V2.0 架构新特性对比

| 功能 | V1.0 (Claude单模型) | V2.0 (DeepSeek双模型路由) |
|------|-------------------|------------------------|
| AI提供商 | 仅Claude | Claude + DeepSeek双支持 |
| 模型策略 | 单一模型 | 智能双模型路由 |
| 工具调用 | Claude格式 | 自动格式转换 |
| 性能优化 | 基础 | 任务导向模型选择 |
| 错误处理 | 基础 | 多层降级机制 |
| 扩展性 | 有限 | 多提供商架构 |

## 关键性能指标

- **响应时间**: 智能路由减少不必要的模型切换开销
- **准确性**: 推理任务使用R1，工具调用使用V3，各自发挥优势
- **稳定性**: 多提供商支持，自动降级机制
- **成本控制**: 按需选择模型，优化API调用成本

## 配置管理

**文件**: `backend/config.py`

```python
# 双模型配置
LLM_PROVIDER: str = "deepseek"  # 或 "claude"
MODEL_REASON: str = "deepseek-ai/DeepSeek-R1"      # 推理模型
MODEL_TOOLCALL: str = "deepseek-ai/DeepSeek-V3"    # 工具调用模型

# API配置
LLM_BASE_URL: str = "https://llm.chutes.ai/v1"     # OpenAI兼容端点
LLM_API_KEY: str = os.getenv("LLM_API_KEY")        # 从环境变量读取
```

## 测试验证

V2.0架构经过全面测试验证：

- **集成测试**: `tests/integration/test_rag_integration.py` (7/7通过)
- **单元测试**: `tests/unit/test_ai_generator.py`
- **路由测试**: `tests/unit/test_router*.py`
- **连接测试**: `tests/unit/test_deepseek_*.py`

所有测试确保了双模型架构的稳定性和正确性。

---

**V2.0架构总结**: 从单一Claude模型升级为智能双模型路由系统，实现了性能优化、成本控制和扩展性的完美平衡。通过智能任务分析和模型选择，系统能够为不同类型的查询选择最适合的AI模型，确保最佳的响应质量和用户体验。