import subprocess
import os
result = subprocess.run(['where', 'git'], capture_output=True, text=True)
print("Git 查找结果:", result.stdout)
print("错误信息:", result.stderr)
print("返回码:", result.returncode)
# 尝试直接调用
result2 = subprocess.run(['git', '--version'], capture_output=True, text=True)
print("Git 版本:", result2.stdout)
print("版本查询错误:", result2.stderr)