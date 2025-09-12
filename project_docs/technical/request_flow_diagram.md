# 课程材料RAG系统 - 请求处理流程图

## 完整请求处理流程图

```mermaid
sequenceDiagram
    participant U as 用户界面
    participant JS as 前端JS
    participant API as FastAPI后端
    participant RAG as RAG系统
    participant SM as 会话管理器
    participant AI as AI生成器
    participant TM as 工具管理器
    participant ST as 搜索工具
    participant VDB as 向量数据库<br/>(ChromaDB)
    participant Claude as Claude API

    Note over U,Claude: 用户查询处理流程

    U->>JS: 1. 输入问题并点击发送
    activate JS
    JS->>JS: 2. 禁用输入框
    JS->>JS: 3. 显示用户消息
    JS->>JS: 4. 显示加载动画
    
    JS->>API: 5. POST /api/query<br/>{query, session_id}
    deactivate JS
    activate API
    
    API->>RAG: 6. rag_system.query()
    activate RAG
    
    RAG->>SM: 7. 获取会话历史
    activate SM
    SM-->>RAG: 返回历史对话
    deactivate SM
    
    RAG->>AI: 8. generate_response()<br/>(包含工具定义)
    activate AI
    
    AI->>AI: 9. 构建系统提示词
    AI->>Claude: 10. 第一次API调用<br/>(带工具定义)
    activate Claude
    Claude-->>AI: 11. 返回工具调用请求
    deactivate Claude
    
    AI->>TM: 12. 执行工具调用
    activate TM
    TM->>ST: 13. 调用搜索工具
    activate ST
    
    ST->>VDB: 14. 课程名解析<br/>(向量相似度搜索)
    activate VDB
    VDB-->>ST: 返回匹配的课程
    
    ST->>VDB: 15. 内容搜索<br/>(带过滤条件)
    VDB-->>ST: 返回相关文档块
    deactivate VDB
    
    ST->>ST: 16. 格式化结果
    ST-->>TM: 17. 返回搜索结果
    deactivate ST
    TM-->>AI: 18. 返回工具执行结果
    deactivate TM
    
    AI->>Claude: 19. 第二次API调用<br/>(带搜索结果)
    activate Claude
    Claude-->>AI: 20. 生成最终回答
    deactivate Claude
    
    AI-->>RAG: 21. 返回AI响应
    deactivate AI
    
    RAG->>TM: 22. 获取搜索来源
    activate TM
    TM-->>RAG: 返回来源列表
    deactivate TM
    
    RAG->>SM: 23. 更新会话历史
    activate SM
    SM-->>RAG: 保存成功
    deactivate SM
    
    RAG-->>API: 24. 返回(答案, 来源)
    deactivate RAG
    
    API-->>JS: 25. 返回JSON响应<br/>{answer, sources, session_id}
    deactivate API
    
    activate JS
    JS->>JS: 26. 移除加载动画
    JS->>JS: 27. 渲染Markdown答案
    JS->>JS: 28. 显示来源信息
    JS->>JS: 29. 启用输入框
    JS->>U: 30. 显示完整回答
    deactivate JS
```

## 简化版数据流向图

```mermaid
graph TB
    subgraph "前端层"
        A[用户输入] --> B[JavaScript处理]
        B --> C[发送AJAX请求]
    end
    
    subgraph "API层"
        C --> D[FastAPI接收]
        D --> E[请求验证]
        E --> F[调用RAG系统]
    end
    
    subgraph "业务逻辑层"
        F --> G[RAG系统协调]
        G --> H[会话管理]
        G --> I[AI生成器]
    end
    
    subgraph "AI处理层"
        I --> J[Claude API<br/>初次调用]
        J --> K{需要搜索?}
        K -->|是| L[工具调用]
        K -->|否| R[直接回答]
    end
    
    subgraph "数据层"
        L --> M[搜索工具]
        M --> N[向量数据库查询]
        N --> O[ChromaDB]
        O --> P[返回相关内容]
        P --> Q[Claude API<br/>二次调用]
    end
    
    subgraph "响应处理"
        Q --> R
        R --> S[组装响应]
        S --> T[返回前端]
        T --> U[渲染显示]
    end
    
    style A fill:#e1f5fe
    style U fill:#c8e6c9
    style O fill:#fff3e0
    style J fill:#f3e5f5
    style Q fill:#f3e5f5
```

## 关键组件职责图

```mermaid
graph LR
    subgraph "前端 Frontend"
        FE[index.html<br/>script.js<br/>style.css]
        FE --> FE1[用户交互]
        FE --> FE2[请求发送]
        FE --> FE3[响应渲染]
    end
    
    subgraph "后端 Backend"
        BE[app.py]
        BE --> BE1[路由处理]
        BE --> BE2[CORS配置]
        BE --> BE3[静态文件服务]
    end
    
    subgraph "RAG核心 Core"
        RAG[rag_system.py]
        RAG --> RAG1[流程协调]
        RAG --> RAG2[组件管理]
        RAG --> RAG3[结果组装]
    end
    
    subgraph "AI层 AI Layer"
        AI[ai_generator.py]
        AI --> AI1[提示词构建]
        AI --> AI2[API调用]
        AI --> AI3[工具执行]
    end
    
    subgraph "搜索层 Search"
        ST[search_tools.py]
        ST --> ST1[工具定义]
        ST --> ST2[搜索执行]
        ST --> ST3[结果格式化]
    end
    
    subgraph "存储层 Storage"
        VS[vector_store.py]
        VS --> VS1[向量索引]
        VS --> VS2[相似度搜索]
        VS --> VS3[元数据管理]
    end
    
    subgraph "会话层 Session"
        SM[session_manager.py]
        SM --> SM1[会话创建]
        SM --> SM2[历史管理]
        SM --> SM3[上下文维护]
    end
```

## 数据结构流转

```mermaid
graph TB
    subgraph "请求数据"
        REQ[QueryRequest<br/>- query: str<br/>- session_id: str]
    end
    
    subgraph "搜索参数"
        SEARCH[SearchParams<br/>- query: str<br/>- course_name: str<br/>- lesson_number: int]
    end
    
    subgraph "向量查询"
        VECTOR[VectorQuery<br/>- embeddings<br/>- filters<br/>- limit]
    end
    
    subgraph "搜索结果"
        RESULT[SearchResults<br/>- documents: List<br/>- metadata: List<br/>- distances: List]
    end
    
    subgraph "工具结果"
        TOOL[ToolResult<br/>- formatted_text<br/>- sources: List]
    end
    
    subgraph "AI响应"
        AI_RESP[AIResponse<br/>- answer: str<br/>- tool_calls: List]
    end
    
    subgraph "最终响应"
        RESP[QueryResponse<br/>- answer: str<br/>- sources: List<br/>- session_id: str]
    end
    
    REQ --> SEARCH
    SEARCH --> VECTOR
    VECTOR --> RESULT
    RESULT --> TOOL
    TOOL --> AI_RESP
    AI_RESP --> RESP
```

## 时序关键点说明

| 步骤 | 组件 | 操作 | 说明 |
|------|------|------|------|
| 1-4 | 前端 | 用户交互处理 | 输入验证、UI更新 |
| 5 | 网络 | HTTP请求 | POST到/api/query |
| 6-8 | RAG系统 | 请求预处理 | 会话管理、历史获取 |
| 9-11 | Claude API | 初次调用 | 判断是否需要搜索 |
| 12-17 | 搜索工具 | 数据库查询 | 向量搜索、过滤 |
| 18-20 | Claude API | 二次调用 | 基于搜索结果生成 |
| 21-24 | RAG系统 | 响应后处理 | 来源提取、会话更新 |
| 25-30 | 前端 | 响应渲染 | Markdown解析、UI更新 |

## 性能关键路径

```mermaid
graph LR
    Start[开始] --> Input[用户输入]
    Input --> API[API调用]
    API --> Claude1[Claude首次调用]
    Claude1 --> Search{需要搜索?}
    Search -->|是| VectorDB[向量数据库查询]
    VectorDB --> Claude2[Claude二次调用]
    Claude2 --> Response[生成响应]
    Search -->|否| Response
    Response --> Render[前端渲染]
    Render --> End[结束]
    
    style Claude1 fill:#ffcccc
    style VectorDB fill:#ffcccc
    style Claude2 fill:#ffcccc
```

**性能瓶颈点（红色标注）**：
1. Claude API调用（网络延迟）
2. 向量数据库查询（嵌入计算）
3. 二次Claude调用（额外延迟）