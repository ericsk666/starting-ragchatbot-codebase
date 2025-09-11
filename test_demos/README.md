# 测试演示文件

此文件夹包含RAG系统的各种测试和演示HTML文件。

## 文件说明

### RAG系统演示
- `rag_system_demo.html` - RAG系统基础演示（V1）
- `rag_system_demo_v2.html` - RAG系统架构可视化演示（V2）
- `rag_system_demo_v3.html` - 深度交互式学习平台（V3）
- `rag_system_demo_v4.html` - 最新版本演示，包含所有交互功能（V4）
- `rag_system_demo_v4_backup.html` - V4版本备份

### 功能测试
- `test_sources_links.html` - Sources链接功能测试页面
- `test_debug.html` - 调试测试页面
- `test_v4_demo.html` - V4演示简化测试

## 使用方法

1. 确保后端服务已启动：
```bash
cd backend
uv run uvicorn app:app --reload --port 8000
```

2. 直接在浏览器中打开相应的HTML文件即可测试

## 注意事项
- 这些是测试和演示文件，不是生产代码
- 主要用于功能验证和展示
- 生产环境请使用 `frontend/` 文件夹中的正式前端代码