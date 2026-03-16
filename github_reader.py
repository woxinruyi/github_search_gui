import requests
import json
# 设置请求头，模拟浏览器访问
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://github.com/'
}
def get_github_repo_info(owner, repo):
    """获取GitHub开源项目的基本信息"""
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    
    try:
        response = requests.get(api_url, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        # 提取关键信息
        repo_info = {
            "项目名称": data.get("name"),
            "所有者": data.get("owner", {}).get("login"),
            "项目描述": data.get("description"),
            "Star数量": data.get("stargazers_count"),
            "Fork数量": data.get("forks_count"),
            "Open Issues": data.get("open_issues_count"),
            "许可证": data.get("license", {}).get("name") if data.get("license") else "无",
            "项目语言": data.get("language"),
            "创建时间": data.get("created_at"),
            "最后更新": data.get("updated_at"),
            "项目地址": data.get("html_url")
        }
        
        return True, repo_info
        
    except Exception as e:
        return False, f"获取项目信息失败: {str(e)}"
# 示例：获取一个知名开源项目的信息
owner = "psf"
repo = "requests"
success, result = get_github_repo_info(owner, repo)
if success:
    print("✅ 成功获取GitHub开源项目信息：")
    print("=" * 60)
    for key, value in result.items():
        print(f"{key}: {value}")
    print("=" * 60)
    utils.set_state(success=True, result=result)
else:
    print(f"❌ {result}")
    utils.set_state(success=False, error=result)