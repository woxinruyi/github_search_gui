gitignore_content = """# Python
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
.DS_Store
# Output results
github_search_results.json
# OS
Thumbs.db
Desktop.ini
"""
with open('.gitignore', 'w', encoding='utf-8') as f:
    f.write(gitignore_content)
print(".gitignore 文件创建成功！")