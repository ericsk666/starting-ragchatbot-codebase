# 课程材料RAG系统 - 请求处理流程图 V2.0

## 双模型智能路由架构流程图

```mermaid
sequenceDiagram
    participant U as 用户界面
    participant JS as 前端JS
    participant API as FastAPI后端
    participant RAG as RAG系统
    participant SM as 会话管理器
    participant AI as AI生成器 ⭐
    participant LR as 智能路由器 🆕
    participant R1 as DeepSeek-R1<br/>(推理模型) 🆕
    participant V3 as DeepSeek-V3<br/>(工具调用) 🆕
    participant TM as 工具管理器
    participant ST as 搜索工具
    participant VDB as 向量数据库<br/>(ChromaDB)
    participant Claude as Claude API<br/>(后备支持) 📋

    Note over U,Claude: V2.0 双模型智能路由架构 - 完整请求处理流程

    %% 用户交互阶段
    U->>JS: 用户输入查询
    JS->>API: POST /api/query {query, session_id}
    
    %% 后端处理入口
    API->>RAG: process_query(query, session_id)
    
    %% 会话管理
    RAG->>SM: get_conversation_history(session_id)
    SM-->>RAG: conversation_history
    
    %% 工具定义准备 - 新增多格式支持
    RAG->>TM: get_tool_definitions_for_provider()
    
    Note over TM: 根据配置提供商返回<br/>OpenAI格式(DeepSeek)或<br/>Claude格式工具定义
    
    TM-->>RAG: tools (格式适配)
    
    %% AI生成 - 核心路由逻辑
    RAG->>AI: generate_response(query, history, tools, tool_manager)
    
    Note over AI: 检测当前提供商配置<br/>LLM_PROVIDER: "deepseek"
    
    AI->>AI: _generate_deepseek_response()
    
    %% 格式转换 - 新增功能
    Note over AI: 检查并转换工具格式<br/>Claude→OpenAI (如需要)
    
    %% 智能路由决策 - 核心创新
    AI->>LR: call_with_tools() 或 call_simple_chat()
    
    alt 需要工具调用
        Note over LR: 🔍 检测到工具调用需求<br/>路由至工具调用模型
        LR->>V3: 使用 DeepSeek-V3
        Note over V3: 专门处理工具调用<br/>函数执行能力强
        V3-->>LR: 工具调用响应
        
        %% 工具执行阶段
        LR->>TM: 执行检测到的工具调用
        TM->>ST: execute_tool(tool_name, **args)
        ST->>VDB: 向量搜索查询
        
        %% 向量检索流程
        Note over VDB: 1. 语义相似度计算<br/>2. 过滤条件应用<br/>3. 相关文档检索
        
        VDB-->>ST: 相关文档和元数据
        ST-->>TM: 格式化搜索结果
        TM-->>LR: 工具执行结果
        
        %% 最终推理阶段 - 智能切换
        Note over LR: 🔄 切换到推理模型<br/>进行结果整合
        LR->>R1: 使用 DeepSeek-R1 整合结果
        Note over R1: 专门处理复杂推理<br/>思考能力强，逻辑清晰
        R1-->>LR: 最终整合响应
        
    else 纯对话查询
        Note over LR: 💭 检测到纯对话需求<br/>直接路由至推理模型
        LR->>R1: 使用 DeepSeek-R1
        Note over R1: 处理一般知识问答<br/>无需工具调用
        R1-->>LR: 直接响应
    end
    
    %% 错误处理和后备机制
    alt DeepSeek 请求失败
        Note over LR: ⚠️ DeepSeek API 异常
        AI->>Claude: 降级到 Claude API
        Note over Claude: 后备支持机制<br/>确保服务可用性
        Claude-->>AI: Claude 响应
    end
    
    LR-->>AI: 最终响应
    AI-->>RAG: 生成的回答
    
    %% 会话管理和响应
    RAG->>SM: add_interaction(session_id, query, response)
    RAG-->>API: {answer, sources, session_id}
    
    API-->>JS: JSON 响应
    JS->>U: 显示回答和来源
    
    %% 状态更新
    JS->>API: GET /api/courses (可选)
    API-->>JS: 课程统计更新
```

## V2.0 架构流程对比分析

### 关键改进点标注说明:

- **⭐ AI生成器**: 重构支持多提供商
- **🆕 智能路由器**: 全新组件，核心创新
- **🆕 双模型支持**: DeepSeek-R1 + DeepSeek-V3
- **📋 Claude后备**: 保留作为降级选项

## 智能路由决策树

```mermaid
flowchart TD
    A[收到用户查询] --> B{检查工具定义}
    B -->|有工具| C[🎯 工具调用路径]
    B -->|无工具| D[💭 纯对话路径]
    
    C --> E[使用 DeepSeek-V3<br/>执行工具调用]
    E --> F[工具执行完成]
    F --> G[切换到 DeepSeek-R1<br/>整合结果推理]
    
    D --> H[直接使用 DeepSeek-R1<br/>处理对话]
    
    G --> I[返回最终响应]
    H --> I
    
    I --> J{请求成功?}
    J -->|是| K[完成响应]
    J -->|否| L[降级到 Claude API]
    L --> K
    
    style C fill:#e1f5fe
    style D fill:#f3e5f5
    style E fill:#e8f5e8
    style G fill:#fff3e0
    style H fill:#fff3e0
```

## 双模型协同工作机制

### 工具调用场景流程:
1. **V3模型接收**: 用户查询 + 工具定义
2. **工具调用决策**: V3分析并决定调用搜索工具
3. **工具执行**: 搜索相关课程内容
4. **模型切换**: 自动切换到R1模型
5. **结果整合**: R1接收工具结果进行推理整合
6. **最终响应**: 生成完整的带来源回答

### 纯对话场景流程:
1. **直接路由**: 识别为一般知识问答
2. **R1处理**: 使用推理能力直接回答
3. **快速响应**: 无需工具调用的高效处理

## 性能优化特性

### 路由智能化:
- **任务识别**: 自动判断查询类型
- **模型选择**: 为任务选择最优模型
- **资源优化**: 避免不必要的模型调用

### 格式兼容性:
- **自动转换**: Claude格式→OpenAI格式
- **透明切换**: 用户无感知的API切换
- **统一接口**: 多提供商统一调用方式

## 错误处理和降级机制

```mermaid
graph TD
    A[请求开始] --> B{DeepSeek可用?}
    B -->|是| C[智能路由处理]
    B -->|否| D[切换到Claude]
    
    C --> E{处理成功?}
    E -->|是| F[返回结果]
    E -->|否| G[错误重试]
    
    G --> H{重试成功?}
    H -->|是| F
    H -->|否| D
    
    D --> I[Claude处理]
    I --> F
    
    style D fill:#ffebee
    style I fill:#ffebee
```

## 配置驱动架构

系统通过环境变量配置实现动态切换:

```bash
# 双模型配置
LLM_PROVIDER=deepseek
MODEL_REASON=deepseek-ai/DeepSeek-R1      # 推理专用
MODEL_TOOLCALL=deepseek-ai/DeepSeek-V3    # 工具调用专用

# 后备配置  
ANTHROPIC_API_KEY=claude_key_here         # Claude后备支持
```

---

**V2.0 流程图总结**: 通过智能路由器实现双模型协同工作，根据任务类型自动选择最适合的AI模型，既保证了工具调用的准确性(V3)，又确保了推理过程的深度(R1)，同时提供Claude作为后备保障，实现了高可用、高性能的RAG系统架构。