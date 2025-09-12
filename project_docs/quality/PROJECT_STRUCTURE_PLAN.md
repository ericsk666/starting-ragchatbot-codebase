# 项目结构整理方案

## 当前问题
根目录文件过多，测试文件和文档混杂，影响项目清晰度。

## 整理目标
- 清晰的目录结构
- 测试文件归类
- 文档分类管理
- 保持根目录简洁

## 整理方案

### 1. 测试文件组织
```
tests/
├── unit/                      # 单元测试
│   ├── test_meta_filtering.py
│   ├── test_simple_consistency.py
│   ├── test_consistent_tool_usage.py
│   └── test_enhanced_filtering.py
├── integration/               # 集成测试
│   └── (现有文件)
├── debug/                     # 调试测试
│   └── (现有文件)
└── html_demos/               # HTML测试演示
    ├── test_new_chat.html
    └── (test_demos/下的所有文件)
```

### 2. 文档组织
```
project_docs/
├── planning/                  # 计划文档
│   ├── NEW_CHAT_FEATURE_PLAN.md
│   ├── HTML_DEMO_IMPROVEMENT_PLAN.md
│   └── UI_OPTIMIZATION_PLAN.md
├── technical/                 # 技术文档
│   ├── LLM_MIGRATION_GUIDE.md
│   ├── RAG_SYSTEM_COMPLETE_GUIDE.md
│   ├── request_flow_analysis.md
│   ├── request_flow_analysis_v2.md
│   ├── request_flow_diagram.md
│   └── request_flow_diagram_v2.md
├── implementation/           # 实施记录
│   ├── FIX_THINKING_CONTENT.md
│   ├── FIX_V3_TOOL_CONSISTENCY.md
│   └── sources_links_implementation.md
└── quality/                  # 质量报告
    └── QUALITY_CHECK_REPORT.md
```

### 3. 根目录保留文件
```
/
├── backend/                  # 后端代码
├── frontend/                 # 前端代码
├── docs/                     # 课程材料
├── tests/                    # 测试套件
├── project_docs/             # 项目文档
├── chroma_db/               # 向量数据库
├── .venv/                   # 虚拟环境
├── README.md                # 项目说明
├── CLAUDE.md                # Claude指令
├── run.sh                   # 启动脚本
├── main.py                  # 主入口
├── pyproject.toml           # 项目配置
├── uv.lock                  # 依赖锁定
├── .env                     # 环境配置
├── .env.example             # 环境示例
├── .gitignore               # Git忽略
└── .python-version          # Python版本
```

## 执行步骤

### 步骤1：创建新目录结构
```bash
mkdir -p tests/html_demos
mkdir -p project_docs/{planning,technical,implementation,quality}
```

### 步骤2：移动Python测试文件
```bash
mv test_*.py tests/unit/
```

### 步骤3：移动HTML测试文件
```bash
mv test_new_chat.html tests/html_demos/
mv test_demos/* tests/html_demos/
rmdir test_demos
```

### 步骤4：移动文档文件
```bash
# 计划文档
mv *_PLAN.md project_docs/planning/

# 技术文档
mv *_GUIDE.md project_docs/technical/
mv request_flow*.md project_docs/technical/

# 实施文档
mv FIX_*.md project_docs/implementation/
mv sources_links_implementation.md project_docs/implementation/

# 质量报告
mv QUALITY_CHECK_REPORT.md project_docs/quality/
```

### 步骤5：更新引用
- 更新代码中的文件路径引用
- 更新文档中的相对链接
- 更新Git忽略规则（如需要）

## 预期结果

### 根目录文件数量
- 整理前：30+ 个文件
- 整理后：~15 个文件

### 优点
1. **清晰性**：一眼就能看出项目结构
2. **可维护性**：文件归类便于查找
3. **专业性**：符合标准项目结构
4. **扩展性**：便于后续添加新文件

## 风险控制
1. 移动前先备份（Git已有版本控制）
2. 逐步移动，每步验证
3. 更新所有引用路径
4. 测试确保功能正常

## 回滚方案
如果出现问题，可通过Git恢复：
```bash
git reset --hard HEAD
```

---
*创建时间：2024-12-XX*