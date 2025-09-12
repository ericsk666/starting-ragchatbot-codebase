"""
测试V3模型工具调用的一致性
验证相同问题是否总是触发工具调用并返回来源
"""
import requests
import json
import time

# API端点
API_URL = "http://localhost:8000/api/query"

# 测试问题集 - 包括通用概念和具体课程问题
TEST_QUERIES = [
    "What is RAG technology and how to implement it?",
    "What is RAG?",
    "Explain RAG implementation steps",
    "How does retrieval augmented generation work?",
    "What are the best practices for prompt engineering?",
    "Tell me about MCP protocol",
    "What is machine learning?",
    "Explain vector databases"
]

def test_query(query: str, session_id: str = None) -> dict:
    """测试单个查询"""
    payload = {
        "query": query,
        "session_id": session_id
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def analyze_consistency(results: list) -> dict:
    """分析结果一致性"""
    stats = {
        "total": len(results),
        "with_sources": 0,
        "without_sources": 0,
        "errors": 0,
        "queries_without_sources": []
    }
    
    for result in results:
        if "error" in result:
            stats["errors"] += 1
        elif result.get("sources") and len(result["sources"]) > 0:
            stats["with_sources"] += 1
        else:
            stats["without_sources"] += 1
            stats["queries_without_sources"].append(result.get("query", "Unknown"))
    
    stats["consistency_rate"] = (stats["with_sources"] / stats["total"] * 100) if stats["total"] > 0 else 0
    
    return stats

def main():
    print("=" * 60)
    print("测试V3模型工具调用一致性")
    print("=" * 60)
    
    results = []
    
    # 测试每个查询3次，验证一致性
    for query in TEST_QUERIES:
        print(f"\n测试查询: {query}")
        print("-" * 40)
        
        for attempt in range(3):
            print(f"  尝试 {attempt + 1}/3...", end=" ")
            result = test_query(query)
            
            # 记录查询和结果
            result["query"] = query
            result["attempt"] = attempt + 1
            results.append(result)
            
            # 检查是否有来源
            has_sources = bool(result.get("sources") and len(result["sources"]) > 0)
            sources_count = len(result.get("sources", []))
            
            if has_sources:
                print(f"[PASS] 有{sources_count}个来源")
                # 显示来源详情
                if result.get("sources_detail"):
                    for source in result["sources_detail"][:2]:  # 只显示前2个
                        print(f"     - {source.get('title', 'Unknown')}")
            else:
                print("[FAIL] 无来源")
            
            # 避免频繁请求
            time.sleep(0.5)
    
    # 分析结果
    print("\n" + "=" * 60)
    print("结果分析")
    print("=" * 60)
    
    stats = analyze_consistency(results)
    
    print(f"总测试次数: {stats['total']}")
    print(f"有来源的响应: {stats['with_sources']} ({stats['with_sources']/stats['total']*100:.1f}%)")
    print(f"无来源的响应: {stats['without_sources']} ({stats['without_sources']/stats['total']*100:.1f}%)")
    print(f"错误响应: {stats['errors']}")
    print(f"一致性率: {stats['consistency_rate']:.1f}%")
    
    if stats["queries_without_sources"]:
        print("\n没有返回来源的查询:")
        for q in set(stats["queries_without_sources"]):
            count = stats["queries_without_sources"].count(q)
            print(f"  - {q} (发生{count}次)")
    
    # 判断测试结果
    print("\n" + "=" * 60)
    if stats["consistency_rate"] >= 95:
        print("[SUCCESS] 测试通过！工具调用高度一致")
    elif stats["consistency_rate"] >= 80:
        print("[WARNING] 测试部分通过，一致性需要改进")
    else:
        print("[FAILED] 测试失败，工具调用不一致")
    print("=" * 60)

if __name__ == "__main__":
    main()