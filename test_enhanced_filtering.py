"""
测试增强的思考内容过滤器
验证对嵌入式思考内容的识别和过滤效果
"""
import sys
sys.path.append('backend')

from ai_generator import AIGenerator

# 创建AI生成器实例
generator = AIGenerator()

# 测试用例：包含各种嵌入式思考内容
test_cases = [
    {
        "name": "用户报告的实际案例",
        "input": """First, looking at Lesson 5, it mentions prompt compression as a cost-saving strategy, especially useful for RAG and agentic systems. The key points here are about reducing the number of tokens in prompts. The lesson talks about using a smaller LLM fine-tuned for compression, which suggests that one best practice is to utilize specialized models for compressing prompts. Also, structuring the input with components like demonstration, instruction, and question is highlighted. That seems like a structural best practice to ensure the compressed prompt is effective.

Operational advantages are mentioned, such as scalability and preventing bottlenecks. So, thinking ahead about scalability and integrating compression into existing pipelines (like RAG) is another best practice. The lesson also emphasizes the ease of implementing compression alongside RAG, suggesting that integration with existing workflows is a good practice.

Putting this all together, the best practices would include using prompt compression techniques with specialized models, structuring prompts into components, employing existing libraries/tools, integrating compression into pipelines, and planning for scalability.

The course materials outline these key prompt engineering best practices:

1. Implement Prompt Compression:
   • Use specialized libraries (e.g., LLM Lingua) to reduce token count
   • Integrate with existing pipelines for cost reduction
   
2. Structure Prompts Effectively:
   • Use components like demonstration, instruction, and question
   • Optimize device usage (CPU vs GPU)""",
        "should_filter": [
            "First, looking at Lesson 5",
            "The lesson talks about",
            "That seems like",
            "So, thinking ahead about",
            "Putting this all together"
        ]
    },
    {
        "name": "叙述性思考模式",
        "input": """Now, examining the search results, we can see important patterns.

Looking at Lesson 3, it discusses advanced techniques.

Starting with the basics, the course covers fundamental concepts.

Best practices for implementation include:
1. Use version control
2. Write tests
3. Document your code""",
        "should_filter": [
            "Now, examining",
            "Looking at Lesson",
            "Starting with"
        ]
    },
    {
        "name": "主观判断模式",
        "input": """This approach seems like the most effective solution.

It appears to be a common pattern in the industry.

The results suggest that optimization is necessary.

This might be the best approach for scalability.

Key technical specifications:
• Processing speed: 100ms
• Memory usage: 512MB
• Throughput: 1000 req/s""",
        "should_filter": [
            "seems like",
            "It appears to",
            "suggest that",
            "This might be"
        ]
    },
    {
        "name": "技术定义（不应过滤）",
        "input": """RAG (Retrieval-Augmented Generation) technology combines retrieval and generation models.

The TCP/IP (Transmission Control Protocol/Internet Protocol) is fundamental to networking.

Machine Learning (ML) algorithms can be classified into supervised and unsupervised categories.

REST (Representational State Transfer) is an architectural style for web services.""",
        "should_filter": []  # 这些技术定义不应该被过滤
    }
]

def test_filtering(test_case):
    """测试单个案例的过滤效果"""
    print("\n" + "=" * 60)
    print(f"测试: {test_case['name']}")
    print("=" * 60)
    
    # 执行过滤
    cleaned = generator._clean_thinking_content(test_case['input'])
    
    # 检查应该被过滤的内容
    print("\n检查过滤效果:")
    for pattern in test_case['should_filter']:
        if pattern.lower() not in cleaned.lower():
            print(f"  [PASS] 成功过滤: '{pattern}'")
        else:
            print(f"  [FAIL] 未能过滤: '{pattern}'")
    
    # 检查技术内容是否被保留
    if not test_case['should_filter']:
        print("  检查技术定义保留...")
        technical_terms = ['RAG', 'TCP/IP', 'Machine Learning', 'REST']
        for term in technical_terms:
            if term in test_case['input'] and term in cleaned:
                print(f"  [OK] 保留技术术语: {term}")
    
    # 显示清理后的内容预览
    print("\n清理后内容预览:")
    print("-" * 40)
    preview = cleaned[:300] + "..." if len(cleaned) > 300 else cleaned
    # 处理特殊字符，避免编码错误
    preview = preview.replace('•', '*').replace('–', '-').replace('"', '"').replace('"', '"')
    try:
        print(preview)
    except UnicodeEncodeError:
        print(preview.encode('gbk', errors='ignore').decode('gbk'))
    print("-" * 40)
    
    # 统计过滤效果
    original_len = len(test_case['input'])
    cleaned_len = len(cleaned)
    reduction = (original_len - cleaned_len) / original_len * 100 if original_len > 0 else 0
    print(f"\n统计: 原始{original_len}字符 → 清理后{cleaned_len}字符 (减少{reduction:.1f}%)")

def main():
    print("=" * 60)
    print("增强过滤器测试")
    print("=" * 60)
    
    # 运行所有测试用例
    for test_case in test_cases:
        test_filtering(test_case)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()