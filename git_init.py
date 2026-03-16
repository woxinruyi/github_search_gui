import subprocess
import os
def run_git_cmd(args):
    result = subprocess.run(['git'] + args, capture_output=True, text=True)
    print(f"> git {' '.join(args)}")
    if result.stdout:
        print("stdout:\n", result.stdout)
    if result.stderr:
        print("stderr:\n", result.stderr)
    return result
# 1. 创建 .gitignore 文件
gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
# IDE
.vscode/
.idea/
*.swp
*.swo
*~
# Results
github_search_results.json
"""
with open('.gitignore', 'w', encoding='utf-8') as f:
    f.write(gitignore_content.strip() + '\n')
print(".gitignore 文件创建成功")
# 2. 检查是否已初始化
if not os.path.exists('.git'):
    run_git_cmd(['init'])
else:
    print("Git 仓库已经初始化")
# 3. 添加所有文件
run_git_cmd(['add', '.'])
# 4. 初次提交
run_git_cmd(['commit', '-m', "Initial commit: GitHub trending search tool with GUI"])
print("\n✅ 本地仓库初始化完成，文件已添加提交！")