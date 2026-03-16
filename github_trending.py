import requests
import json
# 设置请求头，模拟浏览器访问
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://github.com/'
}
def search_github_repos(keyword, sort_by="stars", order="desc", per_page=30):
    """搜索GitHub项目并按热度排序"""
    api_url = f"https://api.github.com/search/repositories?q={keyword}&sort={sort_by}&order={order}&per_page={per_page}"
    
    try:
        response = requests.get(api_url, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        repos = []
        for item in data.get("items", []):
            repo_info = {
                "排名": len(repos) + 1,
                "项目名称": item.get("full_name"),
                "项目描述": item.get("description"),
                "Star数量": item.get("stargazers_count"),
                "Fork数量": item.get("forks_count"),
                "Open Issues": item.get("open_issues_count"),
                "项目语言": item.get("language"),
                "最后更新": item.get("updated_at"),
                "项目地址": item.get("html_url")
            }
            repos.append(repo_info)
        
        total_count = data.get("total_count", 0)
        return True, total_count, repos
        
    except Exception as e:
        return False, 0, f"搜索失败: {str(e)}"
# 搜索热门Python项目示例
keyword = "python"
success, total_count, results = search_github_repos(keyword)
if success:
    print(f"✅ 搜索关键词 '{keyword}' 成功，共找到 {total_count} 个项目，显示热度前20名：")
    print("=" * 120)
    print(f"{'排名':<4} {'项目名称':<30} {'Star数':<8} {'Fork数':<8} {'语言':<10}")
    print("-" * 120)
    for repo in results[:20]:
        name = repo['项目名称'] if len(repo['项目名称']) <= 27 else repo['项目名称'][:24] + "..."
        lang = repo['项目语言'] if repo['项目语言'] else "未知"
        print(f"{repo['排名']:<4} {name:<30} {repo['Star数量']:<8} {repo['Fork数量']:<8} {lang:<10}")
    print("=" * 120)
    print(f"\n📫 完整项目数据已保存到文件 github_{keyword}_search_results.json")
    # 保存完整结果到json文件
    output_file = f"github_{keyword}_search_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    utils.set_state(success=True, total_count=total_count, results=results[:20])
else:
    print(f"❌ {results}")
    utils.set_state(success=False, error=results)