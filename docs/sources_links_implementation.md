# Sources链接功能实现文档

## 概述
本次优化将RAG系统中的Sources显示从纯文本改为可点击的链接，用户可以直接点击跳转到对应的课程视频页面。

## 实施日期
2025-01-11

## 需求背景
- 原始显示：Sources以纯文本形式显示，如"MCP: Build Rich-Context AI Apps with Anthropic - Lesson 4"
- 用户需求：保留语义化的课程名称显示，同时让其变成可点击的链接，点击后跳转到课程视频页面

## 技术方案

### 1. 数据流程
```
文档 → 提取链接(Course Link/Lesson Link) → 存储到向量数据库 → 查询时返回 → 前端渲染为链接
```

### 2. 实现优势
- 系统已经在提取和存储课程链接（course_link）和课程链接（lesson_link）
- 最小化改动，风险可控
- 保持向后兼容性

## 具体实现

### 后端改进

#### 1. search_tools.py
- 新增`last_sources_detail`属性存储详细的sources信息
- 在`_format_results`方法中收集链接信息
- 为每个source获取对应的course_link和lesson_link

```python
# 新增的数据结构
sources_detail = [
    {
        "title": "MCP: Build Rich-Context AI Apps - Lesson 4",
        "course_link": "https://www.deeplearning.ai/...",
        "lesson_link": "https://learn.deeplearning.ai/..."
    }
]
```

#### 2. rag_system.py
- 修改`query`方法返回值，新增sources_detail
- 返回格式：`(response, sources, sources_detail)`

#### 3. app.py
- 新增`SourceDetail`模型定义
- `QueryResponse`模型新增可选的`sources_detail`字段
- API响应包含详细的链接信息

### 前端改进

#### 1. script.js
- 修改`addMessage`函数，支持sources_detail参数
- 实现智能链接选择逻辑：
  - 优先使用lesson_link（更精确）
  - 其次使用course_link
  - 无链接时降级为纯文本
- 渲染格式：
```html
<a href="lesson_link" target="_blank" class="source-link">
    MCP: Build Rich-Context AI Apps - Lesson 4
    <span class="external-icon">↗</span>
</a>
```

#### 2. style.css
- 新增`.source-link`样式：蓝色、hover效果
- 新增`.external-icon`外链图标样式
- 新增`.source-separator`分隔符样式
- 新增`.source-plain`纯文本样式（无链接时使用）

## 测试结果

### API响应示例
```json
{
  "answer": "...",
  "sources": ["title1", "title2"],  // 保持向后兼容
  "sources_detail": [
    {
      "title": "MCP: Build Rich-Context AI Apps - Lesson 4",
      "course_link": "https://www.deeplearning.ai/short-courses/mcp-build-rich-context-ai-apps-with-anthropic/",
      "lesson_link": "https://learn.deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic/lesson/dbabg/creating-an-mcp-server"
    }
  ]
}
```

### 功能验证
✅ 后端正确返回sources_detail
✅ 前端正确渲染可点击链接
✅ 链接能够正确跳转到课程页面
✅ 保持向后兼容性
✅ 无链接时正确降级显示

## 用户体验改进

### 视觉效果
- 链接显示为蓝色，带有hover效果
- 外链图标(↗)提示用户将跳转到外部页面
- 保持与现有UI设计的一致性

### 交互优化
- 链接在新标签页打开（target="_blank"）
- hover时有视觉反馈
- 点击区域适中，易于操作

## 后续优化建议

1. **智能去重**：同一课程的多个Lessons合并显示
2. **链接有效性检查**：定期验证外部链接是否有效
3. **点击统计**：记录用户点击行为，优化推荐
4. **链接预览**：hover时显示课程简介
5. **快捷键支持**：支持键盘导航

## 文件变更列表

### 修改的文件
- `backend/search_tools.py` - 收集链接信息
- `backend/rag_system.py` - 返回详细sources
- `backend/app.py` - API响应模型
- `frontend/script.js` - 渲染逻辑
- `frontend/style.css` - 链接样式

### 新增的文件
- `test_sources_links.html` - 测试页面
- `docs/sources_links_implementation.md` - 本文档

## 总结
本次优化成功实现了Sources的可点击链接功能，提升了用户体验，让用户能够快速访问相关的课程视频资源。实现过程充分利用了系统已有的链接提取功能，改动最小，风险可控。