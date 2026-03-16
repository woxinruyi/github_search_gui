import subprocess
# echo 到 .gitignore 追加忽略 task.log
with open('.gitignore', 'a', encoding='utf-8') as f:
    f.write('\n# Log file\ntask.log\n')
print("已添加 task.log 到 .gitignore")
# 重新 add
subprocess.run(['git', 'add', '.'], capture_output=True)
# 再 commit
commit_msg = "Initial commit: GitHub Trending Search Tool - 基于GitHub API的热门项目搜索工具"
result = subprocess.run(['git', 'commit', '-m', commit_msg], capture_output=True, text=True, encoding='utf-8', errors='replace')
print("提交结果:")
if result.stdout:
    print(result.stdout)
if result.stderr:
    print(result.stderr)
# 看日志
print("\n提交日志：")
result = subprocess.run(['git', 'log', '--oneline'], capture_output=True, text=True, encoding='utf-8', errors='replace')
print(result.stdout)