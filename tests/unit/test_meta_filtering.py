"""
测试元评论过滤
"""
import sys
sys.path.append('backend')

from ai_generator import AIGenerator

# 创建AI生成器实例
generator = AIGenerator()

# 模拟包含元评论的响应（类似截图中的情况）
test_response = """The search results point to Lesson 5 and 6 of "Prompt Compression and Query Optimization". Lesson 5 discusses prompt compression as a cost-saving strategy, especially for RAG and agentic systems.

The user's question is about best practices, so I need to extract key points from the lesson. The main practices here are prompt compression techniques, using specialized models, structuring prompts effectively, and considering scalability.

Need to ensure the answer is brief, uses bullet points, and includes examples as per the instructions. Avoid any extra info not in the search results. Check that each point is derived from the course content provided.

Best practices for prompt engineering from course materials:

1. Implement Prompt Compression:
   • Use specialized libraries (e.g., LLM Lingua) to reduce token count
   • Integrate with existing pipelines for cost reduction
   
2. Structure Prompts Effectively:
   • Use components like demonstration, instruction, and question
   • Optimize device usage (CPU vs GPU)"""

print("=" * 60)
print("测试元评论过滤（应该过滤前3段）")
print("=" * 60)

cleaned = generator._clean_thinking_content(test_response)

print("\n清理后的响应：")
print("-" * 40)
try:
    print(cleaned[:300] + "..." if len(cleaned) > 300 else cleaned)
except UnicodeEncodeError:
    print(cleaned.encode('gbk', errors='ignore').decode('gbk')[:300] + "...")
print("-" * 40)

# 验证思考内容是否被过滤
if "The search results point to" not in cleaned:
    print("\n[PASS] 元评论段落1被正确过滤")
else:
    print("\n[FAIL] 元评论段落1未被过滤")

if "The user's question is about" not in cleaned:
    print("[PASS] 元评论段落2被正确过滤")
else:
    print("[FAIL] 元评论段落2未被过滤")

if "Need to ensure" not in cleaned:
    print("[PASS] 元评论段落3被正确过滤")
else:
    print("[FAIL] 元评论段落3未被过滤")

if "Best practices for prompt engineering" in cleaned:
    print("[PASS] 答案标题被正确保留")
else:
    print("[FAIL] 答案标题被错误过滤")