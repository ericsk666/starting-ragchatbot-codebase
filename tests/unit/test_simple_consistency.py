"""
简化的一致性测试 - 只测试RAG问题
"""
import requests
import json
import time

API_URL = "http://localhost:8000/api/query"

def test_rag_query():
    """测试RAG查询3次"""
    query = "What is RAG technology and how to implement it?"
    print(f"测试问题: {query}")
    print("=" * 60)
    
    for i in range(3):
        print(f"\n第{i+1}次测试:")
        try:
            response = requests.post(API_URL, json={"query": query})
            response.raise_for_status()
            data = response.json()
            
            # 检查来源
            sources = data.get("sources", [])
            sources_detail = data.get("sources_detail", [])
            
            print(f"  来源数量: {len(sources)}")
            if sources:
                print("  来源列表:")
                for s in sources[:3]:
                    print(f"    - {s}")
            else:
                print("  [WARNING] 没有返回来源！")
            
            # 显示部分答案
            answer = data.get("answer", "")
            print(f"  答案前100字符: {answer[:100]}...")
            
        except Exception as e:
            print(f"  [ERROR] {e}")
        
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("测试完成")

if __name__ == "__main__":
    test_rag_query()