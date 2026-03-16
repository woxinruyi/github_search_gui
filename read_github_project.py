import requests
import base64
# 直接测试经典开源项目 flask
OWNER = "pallets"
REPO = "flask"
# 如果有token就加上
GITHUB_TOKEN = None
token_from_env = utils.get_env("github_token")
if token_from_env:
    GITHUB_TOKEN = token_from_env.strip()
headers = {}
if GITHUB_TOKEN:
    headers["Authorization"] = f"token {GITHUB_TOKEN}"
# 获取项目基本信息
api_url = f"https://api.github.com/repos/{OWNER}/{REPO}"
response = requests.get(api_url, headers=headers)
if response.status_code != 200:
    print(f"❌ 获取信息失败：{response.status_code} {response.text}")
    exit(1)
data = response.json()
# 输出基本信息
print("\n📦 项目基本信息：")
print(f"项目名称：{data.get('full_name')}")
print(f"项目描述：{data.get('description')}")
print(f"星标数量：{data.get('stargazers_count')}")
print(f"Fork数量：{data.get('forks_count')}")
print(f"开放许可证：{data.get('license', {}).get('name', '未指定')}")
print(f"默认分支：{data.get('default_branch')}")
print(f"项目地址：{data.get('html_url')}")
print(f"最后更新：{data.get('updated_at')}")
# 获取README内容
readme_url = f"https://api.github.com/repos/{OWNER}/{REPO}/readme"
readme_resp = requests.get(readme_url, headers=headers)
if readme_resp.status_code == 200:
    readme_data = readme_resp.json()
    readme_content = base64.b64decode(readme_data['content']).decode('utf-8', errors='replace')
    # 保存README到本地
    with open("github_project_readme.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("\n✅ README.md 已保存到当前目录：github_project_readme.md")
    # 输出开头预览
    preview = readme_content[:1200]
    print(f"\n📖 README预览：\n{preview}...")
else:
    print("\n⚠️  未找到README文件")
utils.set_state(success=True, result=f"成功读取 {OWNER}/{REPO} 项目信息，README已保存")