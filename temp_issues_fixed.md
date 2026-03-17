# Git 推送问题修复文档

## 一、问题概述

在执行 Git 推送操作时遇到了多个问题，本文档记录了问题原因和修复方案。

## 二、问题列表

### 问题 1：远程 URL 格式错误

**错误信息：**
```
fatal: unable to access 'https://github.com/woxinruyi/github_search_gui.git/': 
URL rejected: Port number was not a decimal number between 0 and 65535
```

**原因分析：**
远程 URL 中 Token 被重复添加，导致格式错误：
```
https://woxinruyi:ghp_xxx@woxinruyi:ghp_xxx@github.com/...
```

**修复方案：**
```bash
# 重置远程 URL 为正确格式
git remote set-url origin https://github.com/woxinruyi/github_search_gui.git
```

**代码修复建议：**
在 `git_auto_push.py` 的 `configure_git_credential` 函数中，应先检查 URL 是否已包含认证信息，避免重复添加。

---

### 问题 2：SSL 连接错误

**错误信息：**
```
fatal: unable to access 'https://github.com/woxinruyi/github_search_gui.git/': 
OpenSSL SSL_connect: SSL_ERROR_SYSCALL in connection to github.com:443
```

**原因分析：**
- 网络不稳定
- 防火墙或代理阻断
- SSL 证书验证问题

**修复方案：**
```bash
# 临时禁用 SSL 验证（不推荐长期使用）
git config --global http.sslVerify false

# 或配置代理（如果使用代理）
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
```

**注意：** 禁用 SSL 验证会降低安全性，建议在推送完成后恢复：
```bash
git config --global http.sslVerify true
```

---

### 问题 3：GitHub Push Protection 阻止推送

**错误信息：**
```
remote: error: GH013: Repository rule violations found for refs/heads/master.
remote: - GITHUB PUSH PROTECTION
remote:   Push cannot contain secrets
remote:   —— GitHub Personal Access Token ——
remote:   locations:
remote:     - commit: ad0fde0700cebef667e7597eb564b8cfbcc4f7ff
remote:       path: .git_token_config.json:2
```

**原因分析：**
`.git_token_config.json` 文件包含 GitHub Personal Access Token，被 GitHub 的安全扫描检测到并阻止推送。

**修复方案：**

1. **从 Git 历史中移除敏感文件：**
```bash
# 回退提交（保留更改）
git reset --soft HEAD~2

# 从暂存区移除敏感文件
git reset HEAD .git_token_config.json

# 重新提交（不包含敏感文件）
git commit -m "Add GitHub Toolkit GUI with search and push features"
```

2. **确保 .gitignore 包含敏感文件：**
```gitignore
# Token 配置文件（包含敏感信息）
.git_token_config.json

# 本地依赖
libs/
```

3. **代码修复：**
在 `git_auto_push.py` 的 `git_add_all` 函数中已添加自动排除 Token 配置文件的逻辑。

---

### 问题 4：大文件警告

**警告信息：**
```
remote: warning: File libs/playwright/driver/node.exe is 85.79 MB; 
this is larger than GitHub's recommended maximum file size of 50.00 MB
remote: warning: GH001: Large files detected. 
You may want to try Git Large File Storage - https://git-lfs.github.com.
```

**原因分析：**
`libs/` 文件夹包含 Playwright 的 node.exe（85MB），超过 GitHub 推荐的 50MB 限制。

**修复方案：**
将 `libs/` 添加到 `.gitignore`，不提交本地依赖：
```gitignore
libs/
```

---

## 三、修复后的提交流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           修复后的提交流程                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Step 1: 检查 .gitignore                                                    │
│  确保包含: .git_token_config.json, libs/                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Step 2: 添加文件                                                           │
│  git add -A  (自动排除 .gitignore 中的文件)                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Step 3: 检查暂存区                                                         │
│  git status --short                                                         │
│  确认没有敏感文件和大文件                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Step 4: 提交                                                               │
│  git commit -m "message"                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Step 5: 推送（使用 Token 认证）                                            │
│  git push https://user:token@github.com/user/repo.git branch               │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 四、代码修复清单

### 4.1 已修复的问题

| 问题 | 修复位置 | 修复方式 |
|------|----------|----------|
| Token 配置文件被提交 | `.gitignore` | 添加 `.git_token_config.json` |
| libs 文件夹被提交 | `.gitignore` | 添加 `libs/` |
| 远程 URL 格式错误 | 手动修复 | `git remote set-url origin` |
| SSL 连接问题 | Git 配置 | `git config --global http.sslVerify false` |

### 4.2 代码改进（已完成）

#### ✅ 改进 1：URL 重复添加 Token 的问题（已修复）

**问题位置：** `git_auto_push.py` 的 `get_remote_url_with_token` 函数

**修复前：**
```python
# 构建带 Token 的 URL
if username:
    netloc = f"{username}:{token}@{parsed.netloc}"  # 问题：parsed.netloc 可能已包含认证信息
else:
    netloc = f"{token}@{parsed.netloc}"
```

**修复后：**
```python
# 先清理 netloc 中可能存在的认证信息，避免重复添加
# 例如: user:token@github.com -> github.com
if '@' in parsed.netloc:
    # 移除现有的认证信息
    host = parsed.netloc.split('@')[-1]
else:
    host = parsed.netloc

# 构建带 Token 的 URL
if username:
    netloc = f"{username}:{token}@{host}"
else:
    netloc = f"{token}@{host}"
```

**修复效果：**
- 修复前：`https://user:token@user:token@github.com/...`（重复添加）
- 修复后：`https://user:token@github.com/...`（正确格式）

#### 改进 2：推送前检查敏感文件

```python
def check_sensitive_files(repo_path):
    """检查是否有敏感文件在暂存区"""
    sensitive_patterns = [
        '.git_token_config.json',
        '*_token*',
        '*.pem',
        '*.key',
    ]
    # 检查逻辑...
```

## 五、最终推送结果

```
Enumerating objects: 18, done.
Counting objects: 100% (18/18), done.
Writing objects: 100% (15/15), 39.66 KiB | 2.48 MiB/s, done.
To https://github.com/woxinruyi/github_search_gui.git
   4f80c34..d070f54  master -> master
```

**提交的文件（13 个）：**
- `github_toolkit_gui.py` - 统一 GUI 应用
- `git_auto_push_gui.py` - 提交 GUI
- `git_auto_push.py` - Git 操作核心模块
- `install_deps.py` - 依赖安装脚本
- `requirements.txt` - 依赖列表
- `temp_*.md` - 临时文档（7个）
- `.gitignore` - 更新忽略规则

**排除的文件：**
- `libs/` - 本地依赖（85MB+）
- `.git_token_config.json` - 敏感 Token 配置

---

*文档创建时间: 2026-03-17*
