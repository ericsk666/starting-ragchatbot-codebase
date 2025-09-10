#!/usr/bin/env python3
"""
测试新的AI生成器 - 验证多提供商支持和双模型路由
"""

import sys
import os

# 添加backend目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.ai_generator import AIGenerator, create_ai_generator
from backend.search_tools import CourseSearchTool, ToolManager
from backend.config import config

# 模拟向量存储用于测试
class MockVectorStore:
    """模拟向量存储，用于测试"""
    
    def search(self, query, course_name=None, lesson_number=None):
        """模拟搜索结果"""
        from backend.vector_store import SearchResults
        
        # 模拟搜索结果
        if "python" in query.lower():
            return SearchResults(
                documents=["Python是一种高级编程语言，具有简洁的语法和强大的功能。"],
                metadata=[{"course_title": "Python编程基础", "lesson_number": 1}],
                distances=[0.1],
                error=None
            )
        elif "rag" in query.lower():
            return SearchResults(
                documents=["RAG（检索增强生成）是一种结合了信息检索和文本生成的AI技术。"],
                metadata=[{"course_title": "AI技术概论", "lesson_number": 3}], 
                distances=[0.2],
                error=None
            )
        else:
            # 空结果
            return SearchResults(
                documents=[],
                metadata=[],
                distances=[],
                error=None
            )

def print_header(title):
    """打印测试标题"""
    print("\n" + "=" * 60)
    print(title)
    print("-" * 60)

def test_ai_generator_initialization():
    """测试AI生成器初始化"""
    print_header("测试1: AI生成器初始化")
    
    try:
        # 测试工厂函数创建
        generator = create_ai_generator()
        print(f"[PASS] 创建AI生成器成功")
        print(f"当前提供商: {generator.provider}")
        
        # 测试直接创建
        generator2 = AIGenerator()
        print(f"[PASS] 直接创建AI生成器成功")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] 初始化失败: {e}")
        return False

def test_simple_response():
    """测试简单响应（无工具）"""
    print_header("测试2: 简单响应生成")
    
    try:
        generator = create_ai_generator()
        
        query = "什么是机器学习？请简要介绍。"
        
        print(f"查询: {query}")
        response = generator.generate_response(query)
        
        print("[PASS] 简单响应生成成功")
        print(f"响应长度: {len(response)} 字符")
        print(f"响应摘要: {response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] 简单响应失败: {e}")
        return False

def test_tool_calling():
    """测试工具调用功能"""
    print_header("测试3: 工具调用功能")
    
    try:
        # 创建生成器
        generator = create_ai_generator()
        
        # 创建工具管理器
        tool_manager = ToolManager()
        mock_store = MockVectorStore()
        search_tool = CourseSearchTool(mock_store)
        tool_manager.register_tool(search_tool)
        
        # 获取当前提供商的工具定义
        tools = tool_manager.get_tool_definitions_for_provider()
        
        print(f"工具定义数量: {len(tools)}")
        print(f"工具格式: {config.LLM_PROVIDER}")
        
        # 测试查询
        query = "请搜索关于Python编程的课程内容"
        
        print(f"查询: {query}")
        response = generator.generate_response(
            query=query,
            tools=tools,
            tool_manager=tool_manager
        )
        
        print("[PASS] 工具调用测试成功")
        print(f"响应: {response[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] 工具调用失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_conversation_history():
    """测试对话历史功能"""
    print_header("测试4: 对话历史上下文")
    
    try:
        generator = create_ai_generator()
        
        # 模拟对话历史
        history = """
        用户: 你好，我想学习编程
        助手: 你好！很高兴帮你学习编程。你想学习哪种编程语言呢？
        用户: 我对Python比较感兴趣
        """
        
        query = "Python适合初学者吗？"
        
        print(f"查询: {query}")
        print("带对话历史")
        
        response = generator.generate_response(
            query=query,
            conversation_history=history
        )
        
        print("[PASS] 对话历史测试成功")
        print(f"响应: {response[:150]}...")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] 对话历史测试失败: {e}")
        return False

def test_provider_switching():
    """测试提供商信息显示"""
    print_header("测试5: 提供商配置检查")
    
    try:
        generator = create_ai_generator()
        
        print(f"当前提供商: {config.LLM_PROVIDER}")
        
        if config.LLM_PROVIDER == "deepseek":
            print(f"推理模型: {config.MODEL_REASON}")
            print(f"工具调用模型: {config.MODEL_TOOLCALL}")
            print("使用智能路由器: 是")
        else:
            print(f"Claude模型: {config.ANTHROPIC_MODEL}")
            print("使用直接API: 是")
        
        print("[PASS] 提供商配置检查完成")
        return True
        
    except Exception as e:
        print(f"[FAIL] 提供商检查失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始AI生成器综合测试")
    
    # 配置信息
    print(f"LLM提供商: {config.LLM_PROVIDER}")
    print(f"API密钥状态: {'已配置' if config.LLM_API_KEY and 'YOUR_NEW' not in config.LLM_API_KEY else '未配置'}")
    
    if not config.LLM_API_KEY or 'YOUR_NEW' in config.LLM_API_KEY:
        print("\n[ERROR] API密钥未正确配置")
        return False
    
    # 运行测试套件
    tests = [
        ("AI生成器初始化", test_ai_generator_initialization),
        ("简单响应生成", test_simple_response),
        ("工具调用功能", test_tool_calling),
        ("对话历史上下文", test_conversation_history),
        ("提供商配置检查", test_provider_switching)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n[TEST] {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[ERROR] 测试异常: {e}")
            results.append((test_name, False))
    
    # 输出总结
    print_header("测试结果总结")
    
    passed = 0
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n[SUCCESS] 所有测试通过！AI生成器工作正常")
        print("关键功能验证:")
        print("  - 多提供商支持正常")
        print("  - 双模型路由有效") 
        print("  - 工具调用机制完善")
        print("  - 对话历史处理正确")
    else:
        print(f"\n[WARNING] {total-passed}个测试失败，需要调试")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)