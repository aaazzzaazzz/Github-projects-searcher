import requests
import json

def test_search(query, sort_by, description):
    url = "http://localhost:8000/api/search"
    params = {
        "q": query,
        "sort_by": sort_by
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"\n{description}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            print(f"找到 {len(results)} 个项目")
            
            # 打印前5个项目的信息
            for i, project in enumerate(results[:5]):
                name = project.get('project_name', 'Unknown')
                health = project.get('health_score', 0)
                activity = project.get('activity_score', 0)
                print(f"{i+1}. {name}: 健康度={health}, 活跃度={activity}")
                
            # 检查排序方向
            if "health" in sort_by:
                scores = [p.get("health_score", 0) for p in results[:10]]
                direction = "升序" if "asc" in sort_by else "降序"
                is_correct = all(scores[i] <= scores[i+1] for i in range(len(scores)-1)) if "asc" in sort_by else all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
                print(f"健康度{direction}排序是否正确: {is_correct}")
                print(f"前10个项目的健康度分数: {scores}")
            elif "activity" in sort_by:
                scores = [p.get("activity_score", 0) for p in results[:10]]
                direction = "升序" if "asc" in sort_by else "降序"
                is_correct = all(scores[i] <= scores[i+1] for i in range(len(scores)-1)) if "asc" in sort_by else all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
                print(f"活跃度{direction}排序是否正确: {is_correct}")
                print(f"前10个项目的活跃度分数: {scores}")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求出错: {e}")

if __name__ == "__main__":
    # 测试低健康度搜索
    test_search("低健康度", "health_asc", "=== 低健康度搜索 ===")
    
    # 测试高健康度搜索
    test_search("高健康度", "health", "=== 高健康度搜索 ===")
    
    # 测试低活跃度搜索
    test_search("低活跃度", "activity_asc", "=== 低活跃度搜索 ===")
    
    # 测试高活跃度搜索
    test_search("高活跃度", "activity", "=== 高活跃度搜索 ===")