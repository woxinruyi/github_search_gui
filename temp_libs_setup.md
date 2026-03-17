# libs 本地依赖管理说明

## 一、目录结构

```
blocks/
├── git_auto_push.py      # 主程序
├── install_deps.py       # 依赖安装脚本
├── requirements.txt      # 依赖清单
├── libs/                 # 本地依赖文件夹
│   ├── __init__.py
│   ├── playwright/       # Playwright 库
│   ├── pyee/             # 事件发射器
│   ├── greenlet/         # 协程支持
│   └── typing_extensions/
└── .gitignore            # 排除 libs 文件夹
```

## 二、依赖管理流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           依赖管理流程                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Step 1: 检查 libs 文件夹                                │
│                      是否存在本地依赖?                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                          ┌───────────┴───────────┐
                          │                       │
                          ▼                       ▼
                    [存在]                  [不存在]
                          │                       │
                          ▼                       ▼
              [添加到 sys.path]      ┌─────────────────────────┐
                          │          │  运行 install_deps.py   │
                          │          │  或                     │
                          │          │  pip install -t libs    │
                          │          └───────────┬─────────────┘
                          │                      │
                          └──────────┬───────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Step 2: 导入依赖                                        │
│                      from playwright.sync_api import sync_playwright         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Step 3: 使用依赖                                        │
│                      自动化浏览器获取 Token                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 三、安装方式

### 方式 1: 使用安装脚本（推荐）

```bash
python install_deps.py
```

脚本会自动：
1. 创建 libs 文件夹
2. 下载依赖到 libs 文件夹
3. 可选安装 Playwright 浏览器

### 方式 2: 手动安装

```bash
# 创建 libs 文件夹
mkdir libs

# 安装依赖到 libs 文件夹
pip install -r requirements.txt -t libs
```

### 方式 3: 安装 Playwright 浏览器

```bash
# 设置 PYTHONPATH 后安装浏览器
set PYTHONPATH=libs
python -m playwright install chromium
```

## 四、代码实现

### 4.1 主程序中的路径配置

```python
# git_auto_push.py 中的配置

import sys
import os

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIBS_DIR = os.path.join(SCRIPT_DIR, 'libs')

# 如果 libs 文件夹存在，将其添加到 sys.path 的最前面
if os.path.exists(LIBS_DIR):
    if LIBS_DIR not in sys.path:
        sys.path.insert(0, LIBS_DIR)
```

### 4.2 依赖导入

```python
# 导入 Playwright（从 libs 文件夹）
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
```

## 五、优势

| 优势 | 说明 |
|------|------|
| **便携性** | 项目可以整体复制到其他机器运行 |
| **隔离性** | 不影响系统 Python 环境 |
| **版本控制** | 可以锁定依赖版本 |
| **离线运行** | 依赖已下载，无需网络 |

## 六、注意事项

### 6.1 .gitignore 配置

libs 文件夹已添加到 `.gitignore`，不会被提交到远程仓库：

```
libs/
.git_token_config.json
```

### 6.2 首次使用

首次使用时需要运行安装脚本：

```bash
# 1. 安装依赖
python install_deps.py

# 2. 运行主程序
python git_auto_push.py
```

### 6.3 依赖更新

如需更新依赖：

```bash
pip install -r requirements.txt -t libs --upgrade
```

## 七、当前已安装的依赖

| 依赖包 | 版本 | 用途 |
|--------|------|------|
| playwright | 1.58.0 | 浏览器自动化 |
| pyee | 13.0.1 | 事件发射器 |
| greenlet | 3.3.2 | 协程支持 |
| typing_extensions | 4.15.0 | 类型提示扩展 |

---

*文档创建时间: 2026-03-17*
