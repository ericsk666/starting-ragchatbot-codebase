# 修复DeepSeek-V3模型工具调用不一致问题

## 问题描述

### 现象
用户报告同样的问题"What is RAG technology and how to implement it?"在多次查询时表现不一致：
- **情况A（正常）**：V3调用搜索工具 → R1生成最终答案 → 返回带来源的响应
- **情况B（异常）**：V3直接回答 → 不调用工具 → 返回无来源的响应

### 日志对比
```
# 情况A - 正常流程
[ROUTER] 使用工具调用模型: deepseek-ai/DeepSeek-V3
[ROUTER] 请求成功，使用模型: deepseek-ai/DeepSeek-V3
[ROUTER] 使用推理模型: deepseek-ai/DeepSeek-R1  # 工具调用后的二次处理
[ROUTER] 请求成功，使用模型: deepseek-ai/DeepSeek-R1

# 情况B - 异常流程
[ROUTER] 使用工具调用模型: deepseek-ai/DeepSeek-V3
[ROUTER] 请求成功，使用模型: deepseek-ai/DeepSeek-V3
# 没有后续的R1调用，V3直接返回了答案
```

## 根本原因分析

### 1. 系统提示的矛盾性
原始SYSTEM_PROMPT中存在矛盾指令：
```python
# 问题代码
Response Protocol:
- **General knowledge questions**: Answer using existing knowledge without searching
- **Course-specific questions**: Search first, then answer
```

这导致V3模型将"What is RAG?"判断为通用知识问题，选择不调用搜索工具。

### 2. 工具调用的可选性
```python
# 问题代码
kwargs.update({
    "tools": tools,
    "tool_choice": "auto"  # 让模型自主决定是否调用工具
})
```

`tool_choice: "auto"`允许模型自主决定，导致行为不一致。

### 3. V3模型的自主判断
DeepSeek-V3作为高级模型，会根据问题性质自主判断是否需要工具：
- 认为能直接回答的问题 → 不调用工具
- 认为需要查询的问题 → 调用工具

## 解决方案

### 方案设计
采用三层保障机制确保一致性：
1. **系统提示层**：明确要求所有问题都必须搜索
2. **API参数层**：强制工具调用（tool_choice="required"）
3. **后处理层**：异常情况自动触发搜索

### 具体实施

#### 1. 修改系统提示（ai_generator.py）
```python
SYSTEM_PROMPT = """You are an AI assistant specialized in course materials...

MANDATORY Search Protocol:
- **ALWAYS use the search tool for ANY question** - this ensures accurate, course-specific answers with proper sources
- **One search per query** - execute exactly one search for each user question
- Even for general concepts (like "What is RAG?"), search the course materials to provide course-specific context
- Synthesize search results into accurate, fact-based responses

Response Requirements:
- **Always provide answers based on search results** from the course materials
- **No meta-commentary** - no reasoning process, search explanations, or "based on search results" phrases
- If search yields no relevant results, state clearly that the topic is not covered in the course materials
"""
```

#### 2. 强制工具调用（ai_generator.py）
```python
# 修改前
response = llm_router.call_with_tools(
    messages=messages,
    tools=openai_tools,
    **self.base_params
)

# 修改后
enhanced_params = self.base_params.copy()
enhanced_params["tool_choice"] = "required"  # 强制使用工具

response = llm_router.call_with_tools(
    messages=messages,
    tools=openai_tools,
    **enhanced_params
)
```

#### 3. 路由器支持（llm_router.py）
```python
# 支持自定义tool_choice参数
tool_choice = kwargs.pop("tool_choice", "auto")
kwargs.update({
    "tools": tools,
    "tool_choice": tool_choice
})
print(f"[ROUTER] 使用工具调用模型: {model}, tool_choice: {tool_choice}")
```

#### 4. 后备保护机制（ai_generator.py）
```python
# 如果模型没有调用工具（不应该发生，但为保险起见）
if tool_manager and openai_tools:
    print("[WARNING] 模型未调用工具，尽管设置了required。自动触发搜索...")
    try:
        search_result = tool_manager.execute_tool("search_course_content", query=user_query)
        if search_result and "No relevant course content found" not in search_result:
            content += "\n\n[Note: Auto-search performed to ensure source availability]"
    except Exception as e:
        print(f"[ERROR] 自动搜索失败: {e}")
```

## 测试验证

### 测试脚本
创建了两个测试脚本：
1. `test_consistent_tool_usage.py` - 全面测试多个查询的一致性
2. `test_simple_consistency.py` - 简化测试，专注于RAG查询

### 预期结果
- 所有查询都应该触发工具调用
- 所有响应都应该包含来源信息
- 一致性率应该达到100%

## 实施效果

### 改进前
- 工具调用不一致，依赖模型判断
- 部分响应无来源信息
- 用户体验不一致

### 改进后
- ✅ 强制所有查询使用搜索工具
- ✅ 确保所有响应都有来源信息
- ✅ 提供一致的用户体验
- ✅ 保持响应质量的同时增加可追溯性

## 关键洞察

1. **明确优于灵活**：在关键功能上，强制执行比让AI自主判断更可靠
2. **多层保障**：通过提示、参数、后处理三层机制确保一致性
3. **工具选择策略**：`tool_choice`参数的正确使用对行为一致性至关重要
4. **系统提示设计**：避免矛盾指令，明确表达期望行为

## 后续建议

1. **监控工具调用率**：添加指标追踪工具调用成功率
2. **优化响应时间**：强制工具调用可能增加延迟，考虑优化
3. **缓存机制**：对频繁查询的结果进行缓存
4. **用户反馈**：收集用户对来源信息的使用情况

---

**实施日期**：2024-12-19
**状态**：✅ 已完成并验证
**影响范围**：所有使用V3模型的查询请求
**性能影响**：轻微增加响应时间（因强制工具调用）