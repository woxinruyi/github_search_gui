import subprocess
import sys
# 初始化仓库
print("===== 初始化 Git 仓库 =====")
result = subprocess.run(['git', 'init'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(result.stderr)
# 设置用户名
print("\n===== 设置用户名 =====")
subprocess.run(['git', 'config', 'user.name', 'woxinruyi'], capture_output=True, text=True)
print(f"用户名设置为: woxinruyi")
# 添加所有文件
print("\n===== 添加文件到暂存区 =====")
result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(result.stderr)
# 首次提交
print("\n===== 首次提交 =====")
commit_msg = "Initial commit: GitHub Trending Search Tool - 基于GitHub API的热门项目搜索工具"
result = subprocess.run(['git', 'commit', '-m', commit_msg], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(result.stderr)
# 查看状态
print("\n===== 当前仓库状态 =====")
result = subprocess.run(['git', 'status'], capture_output=True, text=True)
print(result.stdout)