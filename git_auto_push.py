#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GitHub 自动提交脚本
自动执行 git add、commit、push 操作，将代码推送到远程仓库

================================================================================
                              业务流程图 (Business Flow)
================================================================================

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                           用户启动脚本                                    │
    │                    (命令行参数 / 直接调用函数)                             │
    └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                     Step 1: 解析命令行参数                                │
    │         -p/--path: 仓库路径    -m/--message: 提交信息                     │
    │         -b/--branch: 分支名    -f/--force: 强制推送                       │
    └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                     Step 2: 验证 Git 仓库                                 │
    │                   检查目录是否包含 .git 文件夹                             │
    └─────────────────────────────────────────────────────────────────────────┘
                                      │
                          ┌───────────┴───────────┐
                          │                       │
                          ▼                       ▼
                    [仓库有效]              [仓库无效] ──────► 返回错误并退出
                          │
                          ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                     Step 3: 检查远程仓库配置                              │
    │                   执行 git remote 检查 origin 是否存在                    │
    └─────────────────────────────────────────────────────────────────────────┘
                                      │
                          ┌───────────┴───────────┐
                          │                       │
                          ▼                       ▼
                  [已配置 origin]         [未配置] ──────► 提示配置命令并退出
                          │
                          ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                     Step 4: 检查工作区状态                                │
    │                   执行 git status --porcelain                            │
    └─────────────────────────────────────────────────────────────────────────┘
                                      │
                          ┌───────────┴───────────┐
                          │                       │
                          ▼                       ▼
                    [有更改]              [无更改] ──────► 提示无更改并退出
                          │
                          ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                     Step 5: 暂存所有更改                                  │
    │                        执行 git add -A                                   │
    └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                     Step 6: 提交更改                                      │
    │                执行 git commit -m "提交信息"                              │
    │            (若未指定提交信息，自动生成带时间戳的信息)                        │
    └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                     Step 7: 检查远程分支并推送                            │
    │         执行 git ls-remote 检查分支 → git push -u origin <branch>        │
    └─────────────────────────────────────────────────────────────────────────┘
                                      │
                          ┌───────────┴───────────┐
                          │                       │
                          ▼                       ▼
                  [分支已存在]              [分支不存在]
                          │                       │
                          ▼                       ▼
                    [推送更新]            [创建新分支并推送]
                          │                       │
                          └───────────┬───────────┘
                                      │
                                      ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                          完成并返回结果                                   │
    └─────────────────────────────────────────────────────────────────────────┘


================================================================================
                              数据流程图 (Data Flow)
================================================================================

    ┌──────────────────┐
    │   输入数据源      │
    │  (Input Data)    │
    └────────┬─────────┘
             │
             ├──► [命令行参数] ──► argparse 解析 ──► 配置字典
             │         │
             │         ├── repo_path (仓库路径)
             │         ├── commit_message (提交信息)
             │         ├── branch (分支名称)
             │         └── force (强制推送标志)
             │
             └──► [本地文件系统] ──► os.path 检查 ──► 仓库有效性
                        │
                        └── .git 目录存在性检查


    ┌──────────────────┐
    │   Git 命令执行    │
    │  (Git Commands)  │
    └────────┬─────────┘
             │
             ├──► subprocess.run() ──► 执行 Shell 命令
             │         │
             │         ├── 输入: Git 命令字符串, 工作目录
             │         │
             │         └── 输出: (成功标志, 标准输出, 错误输出)
             │
             │
    ┌────────┴─────────────────────────────────────────────────────┐
    │                                                              │
    │   Git 命令数据流:                                             │
    │                                                              │
    │   git remote get-url origin                                  │
    │        └──► 返回远程仓库 URL 字符串                            │
    │                                                              │
    │   git status --porcelain                                     │
    │        └──► 返回文件状态列表 (M/A/D/? 前缀)                    │
    │                                                              │
    │   git add -A                                                 │
    │        └──► 暂存区更新 (无返回数据)                            │
    │                                                              │
    │   git commit -m "message"                                    │
    │        └──► 返回提交哈希和统计信息                             │
    │                                                              │
    │   git push -u origin <branch>                                │
    │        └──► 返回推送结果和远程分支信息                          │
    │                                                              │
    └──────────────────────────────────────────────────────────────┘


    ┌──────────────────┐
    │   输出数据       │
    │  (Output Data)   │
    └────────┬─────────┘
             │
             ├──► [控制台输出] ──► print() ──► 状态信息和emoji提示
             │
             └──► [返回值] ──► bool ──► True(成功) / False(失败)
                        │
                        └──► sys.exit() ──► 0(成功) / 1(失败)


================================================================================
                              模块依赖关系图
================================================================================

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                           git_auto_push.py                              │
    └─────────────────────────────────────────────────────────────────────────┘
                                      │
            ┌─────────────────────────┼─────────────────────────┐
            │                         │                         │
            ▼                         ▼                         ▼
    ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
    │   subprocess  │       │      os       │       │   datetime    │
    │  (命令执行)    │       │  (路径操作)   │       │  (时间处理)    │
    └───────────────┘       └───────────────┘       └───────────────┘
            │                         │
            ▼                         ▼
    ┌───────────────┐       ┌───────────────┐
    │   sys         │       │   argparse    │
    │  (退出码)     │       │  (参数解析)    │
    └───────────────┘       └───────────────┘


================================================================================
                              函数调用关系图
================================================================================

    main()
      │
      ├──► argparse.ArgumentParser()  # 创建参数解析器
      │
      └──► auto_push()                # 核心业务逻辑
              │
              ├──► check_git_repo()   # 验证仓库有效性
              │         └──► os.path.isdir()
              │
              ├──► get_remote_url()   # 获取远程地址
              │         └──► run_git_command()
              │
              ├──► git_status()       # 获取工作区状态
              │         └──► run_git_command()
              │
              ├──► git_add_all()      # 暂存所有更改
              │         └──► run_git_command()
              │
              ├──► git_commit()       # 提交更改
              │         └──► run_git_command()
              │
              └──► git_push()         # 推送到远程
                        └──► run_git_command()
                                  │
                                  └──► subprocess.run()  # 底层命令执行

================================================================================
"""

# ==============================================================================
# 标准库导入
# ==============================================================================
import subprocess  # 用于执行外部 Shell 命令（Git 命令）
import sys         # 用于系统退出码控制
import os          # 用于文件路径操作和目录检查
import re          # 用于正则表达式匹配
import json        # 用于配置文件读写
from datetime import datetime  # 用于生成时间戳
from urllib.parse import urlparse, urlunparse  # 用于 URL 解析和构建

# ==============================================================================
# 本地依赖路径配置
# ==============================================================================
# 将 libs 文件夹添加到 Python 模块搜索路径
# 这样可以优先使用本地安装的依赖，实现项目依赖的本地化管理
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIBS_DIR = os.path.join(SCRIPT_DIR, 'libs')

# 如果 libs 文件夹存在，将其添加到 sys.path 的最前面
if os.path.exists(LIBS_DIR):
    if LIBS_DIR not in sys.path:
        sys.path.insert(0, LIBS_DIR)


# ==============================================================================
# Token 配置文件路径
# ==============================================================================
TOKEN_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.git_token_config.json')


# ==============================================================================
# Token 管理函数
# ==============================================================================

def save_token(token, username=None):
    """
    保存 GitHub Token 到本地配置文件
    
    参数:
        token (str): GitHub Personal Access Token
        username (str, optional): GitHub 用户名
    
    返回:
        bool: 保存是否成功
    """
    try:
        config = {
            'token': token,
            'username': username,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(TOKEN_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✅ Token 已保存到: {TOKEN_CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"❌ 保存 Token 失败: {e}")
        return False


def load_token():
    """
    从本地配置文件加载 GitHub Token
    
    返回:
        tuple: (token, username) 如果配置存在，否则返回 (None, None)
    """
    try:
        if os.path.exists(TOKEN_CONFIG_FILE):
            with open(TOKEN_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config.get('token'), config.get('username')
    except Exception as e:
        print(f"⚠️ 加载 Token 配置失败: {e}")
    return None, None


def delete_token():
    """
    删除本地保存的 Token 配置
    
    返回:
        bool: 删除是否成功
    """
    try:
        if os.path.exists(TOKEN_CONFIG_FILE):
            os.remove(TOKEN_CONFIG_FILE)
            print("✅ Token 配置已删除")
            return True
        else:
            print("⚠️ Token 配置文件不存在")
            return False
    except Exception as e:
        print(f"❌ 删除 Token 配置失败: {e}")
        return False


def get_remote_url_with_token(repo_path, token, username=None):
    """
    获取带有 Token 认证的远程仓库 URL
    
    将远程仓库 URL 转换为带 Token 认证的格式:
    https://github.com/user/repo.git -> https://<token>@github.com/user/repo.git
    或
    https://github.com/user/repo.git -> https://<username>:<token>@github.com/user/repo.git
    
    参数:
        repo_path (str): Git 仓库的本地路径
        token (str): GitHub Personal Access Token
        username (str, optional): GitHub 用户名
    
    返回:
        str or None: 带 Token 的 URL，如果获取失败返回 None
    """
    # 获取当前远程仓库 URL
    success, stdout, _ = run_git_command("git remote get-url origin", cwd=repo_path)
    if not success or not stdout:
        return None
    
    original_url = stdout.strip()
    
    # 解析 URL
    # 支持格式: https://github.com/user/repo.git
    #          git@github.com:user/repo.git (SSH 格式需要转换)
    
    if original_url.startswith('git@'):
        # SSH 格式转换为 HTTPS 格式
        # git@github.com:user/repo.git -> https://github.com/user/repo.git
        match = re.match(r'git@([^:]+):(.+)', original_url)
        if match:
            host = match.group(1)
            path = match.group(2)
            original_url = f"https://{host}/{path}"
    
    # 解析 HTTPS URL
    parsed = urlparse(original_url)
    
    if parsed.scheme != 'https':
        print(f"⚠️ 不支持的 URL 格式: {original_url}")
        return None
    
    # 先清理 netloc 中可能存在的认证信息，避免重复添加
    # 例如: user:token@github.com -> github.com
    if '@' in parsed.netloc:
        # 移除现有的认证信息
        host = parsed.netloc.split('@')[-1]
    else:
        host = parsed.netloc
    
    # 构建带 Token 的 URL
    if username:
        # 格式: https://username:token@github.com/user/repo.git
        netloc = f"{username}:{token}@{host}"
    else:
        # 格式: https://token@github.com/user/repo.git
        netloc = f"{token}@{host}"
    
    # 重新构建 URL
    new_url = urlunparse((
        parsed.scheme,
        netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        parsed.fragment
    ))
    
    return new_url


def configure_git_credential(repo_path, token, username=None):
    """
    配置 Git 使用 Token 进行认证
    
    通过设置远程 URL 包含 Token 的方式实现认证。
    
    参数:
        repo_path (str): Git 仓库的本地路径
        token (str): GitHub Personal Access Token
        username (str, optional): GitHub 用户名
    
    返回:
        bool: 配置是否成功
    """
    # 获取带 Token 的 URL
    token_url = get_remote_url_with_token(repo_path, token, username)
    if not token_url:
        return False
    
    # 更新远程仓库 URL
    success, _, stderr = run_git_command(f'git remote set-url origin "{token_url}"', cwd=repo_path)
    if not success:
        print(f"❌ 配置 Token 认证失败: {stderr}")
        return False
    
    return True


def restore_remote_url(repo_path):
    """
    恢复远程仓库 URL（移除 Token）
    
    将带 Token 的 URL 恢复为普通 URL，保护 Token 安全。
    
    参数:
        repo_path (str): Git 仓库的本地路径
    
    返回:
        bool: 恢复是否成功
    """
    success, stdout, _ = run_git_command("git remote get-url origin", cwd=repo_path)
    if not success or not stdout:
        return False
    
    current_url = stdout.strip()
    
    # 检查 URL 是否包含认证信息
    parsed = urlparse(current_url)
    if '@' in parsed.netloc:
        # 移除认证信息
        # username:token@github.com -> github.com
        netloc = parsed.netloc.split('@')[-1]
        clean_url = urlunparse((
            parsed.scheme,
            netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment
        ))
        
        # 更新远程 URL
        success, _, _ = run_git_command(f'git remote set-url origin "{clean_url}"', cwd=repo_path)
        return success
    
    return True


# ==============================================================================
# Token 自动获取函数
# ==============================================================================

def prompt_get_token():
    """
    提示用户获取 GitHub Token
    
    提供两种获取方式：
        1. 自动获取（使用 Playwright 自动化浏览器）
        2. 手动获取（打开浏览器，用户手动操作）
    
    返回:
        tuple: (success, token, username)
            - success (bool): 是否成功获取 Token
            - token (str): GitHub Personal Access Token
            - username (str): GitHub 用户名
    """
    import webbrowser
    
    print("\n" + "=" * 60)
    print("🔑 GitHub Token 获取向导")
    print("=" * 60)
    print("\n请选择获取 Token 的方式：")
    print("  1. 自动获取 (使用浏览器自动化，需要 Playwright)")
    print("  2. 手动获取 (打开浏览器，手动操作后粘贴 Token)")
    print("  3. 跳过 (稍后手动配置)")
    print()
    
    choice = input("请输入选项 (1/2/3): ").strip()
    
    if choice == '1':
        return auto_get_token_with_browser()
    elif choice == '2':
        return manual_get_token()
    else:
        print("\n💡 您可以稍后使用以下命令配置 Token：")
        print("   python git_auto_push.py -t <your_token> -u <username> --save-token")
        return False, None, None


def auto_get_token_with_browser():
    """
    使用 Playwright 自动化浏览器获取 Token
    
    流程:
        1. 检查并安装 Playwright
        2. 打开浏览器到 GitHub 登录页
        3. 等待用户登录
        4. 跳转到 Token 创建页面
        5. 自动填写信息并生成 Token
        6. 获取并保存 Token
    
    返回:
        tuple: (success, token, username)
    """
    # 检查 Playwright 是否安装
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("\n⚠️ Playwright 未安装")
        user_input = input("是否自动安装 Playwright? (y/n): ").strip().lower()
        if user_input == 'y':
            print("📦 正在安装 Playwright...")
            try:
                import subprocess as sp
                sp.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
                sp.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
                print("✅ Playwright 安装成功")
                from playwright.sync_api import sync_playwright
            except Exception as e:
                print(f"❌ 安装失败: {e}")
                print("   请尝试手动获取方式")
                return manual_get_token()
        else:
            return manual_get_token()
    
    import time
    
    print("\n🌐 正在启动浏览器...")
    print("📝 请在浏览器中完成 GitHub 登录")
    print("   登录后将自动跳转到 Token 创建页面\n")
    
    token = None
    username = None
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            # 跳转到 GitHub 登录页
            print("🔗 正在打开 GitHub 登录页面...")
            page.goto("https://github.com/login")
            
            # 等待用户登录
            print("⏳ 等待用户登录... (最多等待 5 分钟)")
            
            max_wait = 300
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                current_url = page.url
                if "github.com/login" not in current_url and "github.com" in current_url:
                    try:
                        page.wait_for_load_state("networkidle", timeout=5000)
                        user_menu = page.locator('[data-login]')
                        if user_menu.count() > 0:
                            username = user_menu.first.get_attribute('data-login')
                            print(f"✅ 登录成功! 用户: {username}")
                            break
                    except:
                        pass
                    if "github.com/login" not in current_url:
                        print("✅ 检测到登录成功")
                        break
                time.sleep(1)
            else:
                print("❌ 登录超时")
                browser.close()
                return False, None, None
            
            # 跳转到 Token 创建页面
            print("\n🔗 正在跳转到 Token 创建页面...")
            page.goto("https://github.com/settings/tokens/new")
            page.wait_for_load_state("networkidle")
            
            # 填写 Token 信息
            print("📝 正在填写 Token 信息...")
            try:
                page.fill('input[name="note"], #token_description', "git_auto_push_token")
            except:
                pass
            
            # 勾选 repo 权限
            print("🔐 正在设置权限 (repo)...")
            try:
                repo_checkbox = page.locator('input[type="checkbox"][value="repo"]')
                if repo_checkbox.count() > 0 and not repo_checkbox.first.is_checked():
                    repo_checkbox.first.click()
            except:
                pass
            
            # 生成 Token
            print("🔄 正在生成 Token...")
            try:
                page.click('button:has-text("Generate token")')
                page.wait_for_load_state("networkidle")
                time.sleep(2)
            except:
                pass
            
            # 获取 Token
            print("🔍 正在获取 Token...")
            try:
                token_element = page.locator('code')
                for i in range(token_element.count()):
                    text = token_element.nth(i).inner_text()
                    if text.startswith('ghp_') or text.startswith('github_pat_'):
                        token = text.strip()
                        print(f"✅ Token 获取成功: {token[:15]}...")
                        break
            except:
                pass
            
            browser.close()
            
            if token:
                save_token(token, username)
                return True, token, username
            else:
                print("❌ 未能自动获取 Token")
                return manual_get_token()
                
    except Exception as e:
        print(f"❌ 自动获取失败: {e}")
        return manual_get_token()


def manual_get_token():
    """
    手动获取 Token：打开浏览器让用户手动操作
    
    返回:
        tuple: (success, token, username)
    """
    import webbrowser
    
    print("\n🌐 正在打开 GitHub Token 创建页面...")
    print("   请在浏览器中完成以下操作：")
    print("   1. 登录 GitHub 账号")
    print("   2. 填写 Token 名称 (如: git_auto_push)")
    print("   3. 选择过期时间")
    print("   4. 勾选 'repo' 权限")
    print("   5. 点击 'Generate token'")
    print("   6. 复制生成的 Token\n")
    
    webbrowser.open("https://github.com/settings/tokens/new")
    
    print("=" * 60)
    token = input("请粘贴您的 GitHub Token (ghp_xxx...): ").strip()
    username = input("请输入您的 GitHub 用户名 (可选，直接回车跳过): ").strip()
    print("=" * 60)
    
    if token and (token.startswith('ghp_') or token.startswith('github_pat_')):
        save_token(token, username if username else None)
        return True, token, username
    else:
        print("❌ Token 格式无效")
        return False, None, None


# ==============================================================================
# 底层工具函数
# ==============================================================================

def run_git_command(command, cwd=None):
    """
    执行 Git 命令并返回结果
    
    这是所有 Git 操作的底层封装函数，通过 subprocess 模块执行 Shell 命令。
    
    参数:
        command (str): 要执行的 Git 命令字符串，如 "git status"
        cwd (str, optional): 命令执行的工作目录路径，默认为 None（使用当前目录）
    
    返回:
        tuple: 包含三个元素的元组
            - success (bool): 命令是否执行成功（返回码为 0）
            - stdout (str): 命令的标准输出内容
            - stderr (str): 命令的错误输出内容
    
    异常处理:
        捕获所有异常，返回 (False, "", 错误信息)
    
    示例:
        >>> success, output, error = run_git_command("git status", cwd="/path/to/repo")
        >>> if success:
        ...     print(output)
    """
    try:
        # 使用 subprocess.run 执行命令
        # capture_output=True: 捕获标准输出和错误输出
        # text=True: 以文本模式返回输出（而非字节）
        # encoding='utf-8': 指定编码格式，支持中文
        # shell=True: 通过 Shell 执行命令，支持命令字符串
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            shell=True
        )
        # 返回执行结果：成功标志、标准输出、错误输出
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        # 异常情况下返回失败状态和错误信息
        return False, "", str(e)


# ==============================================================================
# Git 仓库检查函数
# ==============================================================================

def check_git_repo(repo_path):
    """
    检查指定路径是否是有效的 Git 仓库
    
    通过检查目录下是否存在 .git 文件夹来判断是否为 Git 仓库。
    
    参数:
        repo_path (str): 要检查的目录路径
    
    返回:
        bool: True 表示是有效的 Git 仓库，False 表示不是
    
    示例:
        >>> if check_git_repo("/path/to/project"):
        ...     print("这是一个 Git 仓库")
    """
    # 构建 .git 目录的完整路径
    git_dir = os.path.join(repo_path, '.git')
    # 检查 .git 目录是否存在
    return os.path.isdir(git_dir)


def get_remote_url(repo_path):
    """
    获取远程仓库 origin 的 URL 地址
    
    执行 git remote get-url origin 命令获取远程仓库地址。
    
    参数:
        repo_path (str): Git 仓库的本地路径
    
    返回:
        str or None: 远程仓库 URL，如果未配置则返回 None
    
    示例:
        >>> url = get_remote_url("/path/to/repo")
        >>> print(url)  # 输出: https://github.com/user/repo.git
    """
    success, stdout, _ = run_git_command("git remote get-url origin", cwd=repo_path)
    return stdout if success else None


# ==============================================================================
# Git 状态查询函数
# ==============================================================================

def git_status(repo_path):
    """
    获取 Git 工作区的状态信息
    
    执行 git status --porcelain 命令获取简洁格式的状态输出。
    porcelain 格式输出每行以两个字符开头表示文件状态：
        - M: 已修改 (Modified)
        - A: 已添加 (Added)
        - D: 已删除 (Deleted)
        - ?: 未跟踪 (Untracked)
        - R: 已重命名 (Renamed)
    
    参数:
        repo_path (str): Git 仓库的本地路径
    
    返回:
        str: 状态信息字符串，如果没有更改则返回空字符串
    
    示例:
        >>> status = git_status("/path/to/repo")
        >>> if status:
        ...     print("有未提交的更改")
    """
    success, stdout, _ = run_git_command("git status --porcelain", cwd=repo_path)
    return stdout if success else ""


# ==============================================================================
# Git 操作函数
# ==============================================================================

def git_add_all(repo_path, exclude_token_config=True):
    """
    将所有更改添加到 Git 暂存区
    
    执行 git add -A 命令，添加所有新文件、修改和删除到暂存区。
    -A 参数等同于 --all，会处理所有类型的更改。
    
    参数:
        repo_path (str): Git 仓库的本地路径
        exclude_token_config (bool): 是否排除 Token 配置文件，默认为 True
    
    返回:
        tuple: (success, message)
            - success (bool): 操作是否成功
            - message (str): 输出信息或错误信息
    
    示例:
        >>> success, msg = git_add_all("/path/to/repo")
        >>> if success:
        ...     print("所有更改已添加到暂存区")
    """
    # 先添加所有文件
    success, stdout, stderr = run_git_command("git add -A", cwd=repo_path)
    
    # 如果需要排除 Token 配置文件，从暂存区移除
    if success and exclude_token_config:
        # 检查 Token 配置文件是否在暂存区
        run_git_command("git reset HEAD -- .git_token_config.json", cwd=repo_path)
    
    return success, stdout or stderr


def git_commit(repo_path, message):
    """
    提交暂存区的更改到本地仓库
    
    执行 git commit -m "message" 命令创建一个新的提交。
    
    参数:
        repo_path (str): Git 仓库的本地路径
        message (str): 提交信息，描述本次更改的内容
    
    返回:
        tuple: (success, message)
            - success (bool): 提交是否成功
            - message (str): 提交结果信息或错误信息
    
    注意:
        - 提交信息中的双引号会被自动转义
        - 如果暂存区没有更改，提交会失败
    
    示例:
        >>> success, msg = git_commit("/path/to/repo", "修复了登录bug")
        >>> if success:
        ...     print("提交成功")
    """
    # 转义提交信息中的双引号，防止命令解析错误
    message = message.replace('"', '\\"')
    success, stdout, stderr = run_git_command(f'git commit -m "{message}"', cwd=repo_path)
    return success, stdout or stderr


def check_remote_exists(repo_path):
    """
    检查是否已配置远程仓库 origin
    
    参数:
        repo_path (str): Git 仓库的本地路径
    
    返回:
        bool: True 表示已配置远程仓库，False 表示未配置
    """
    success, stdout, _ = run_git_command("git remote", cwd=repo_path)
    return success and "origin" in stdout


def check_remote_branch_exists(repo_path, branch):
    """
    检查远程分支是否存在
    
    通过 git ls-remote 命令检查远程仓库中是否存在指定分支。
    
    参数:
        repo_path (str): Git 仓库的本地路径
        branch (str): 要检查的分支名称
    
    返回:
        bool: True 表示远程分支存在，False 表示不存在
    """
    success, stdout, _ = run_git_command(f"git ls-remote --heads origin {branch}", cwd=repo_path)
    # 如果命令成功且输出不为空，说明远程分支存在
    return success and len(stdout.strip()) > 0


def init_remote_repo(repo_path, remote_url):
    """
    初始化远程仓库配置
    
    如果尚未配置远程仓库，添加 origin 远程地址。
    
    参数:
        repo_path (str): Git 仓库的本地路径
        remote_url (str): 远程仓库 URL，如 https://github.com/user/repo.git
    
    返回:
        tuple: (success, message)
            - success (bool): 操作是否成功
            - message (str): 输出信息或错误信息
    """
    success, stdout, stderr = run_git_command(f"git remote add origin {remote_url}", cwd=repo_path)
    return success, stdout or stderr


def git_push(repo_path, branch="master", force=False):
    """
    将本地提交推送到远程仓库
    
    执行 git push -u origin <branch> 命令将本地分支推送到远程。
    -u 参数会设置上游跟踪关系，方便后续的 pull/push 操作。
    
    **特别处理**：
    - 如果远程分支不存在，会自动创建新分支
    - 使用 --set-upstream 确保建立跟踪关系
    
    参数:
        repo_path (str): Git 仓库的本地路径
        branch (str): 要推送的分支名称，默认为 "master"
        force (bool): 是否强制推送，默认为 False
                      强制推送会覆盖远程分支的历史，请谨慎使用！
    
    返回:
        tuple: (success, message, is_new_branch)
            - success (bool): 推送是否成功
            - message (str): 推送结果信息或错误信息
            - is_new_branch (bool): 是否是新创建的远程分支
    
    警告:
        force=True 会强制覆盖远程分支，可能导致其他人的工作丢失！
    
    示例:
        >>> success, msg, is_new = git_push("/path/to/repo", branch="main")
        >>> if success:
        ...     if is_new:
        ...         print("新分支创建并推送成功")
        ...     else:
        ...         print("推送成功")
    """
    # 检查远程分支是否存在
    is_new_branch = not check_remote_branch_exists(repo_path, branch)
    
    # 根据 force 参数决定是否添加 --force 标志
    force_flag = "--force" if force else ""
    
    # 使用 -u 参数设置上游跟踪，这样即使远程分支不存在也会自动创建
    success, stdout, stderr = run_git_command(
        f"git push -u origin {branch} {force_flag}", 
        cwd=repo_path
    )
    
    return success, stdout or stderr, is_new_branch


# ==============================================================================
# 核心业务函数
# ==============================================================================

def auto_push(repo_path=None, commit_message=None, branch="master", force=False, 
               token=None, username=None, use_saved_token=True):
    """
    自动提交并推送代码到远程仓库（核心业务函数）
    
    这是脚本的核心函数，按顺序执行以下操作：
    1. 验证 Git 仓库有效性
    2. 获取并显示远程仓库信息
    3. 配置 Token 认证（如果提供）
    4. 检查工作区是否有更改
    5. 暂存所有更改 (git add -A)
    6. 提交更改 (git commit)
    7. 推送到远程仓库 (git push)
    8. 恢复远程 URL（移除 Token，保护安全）
    
    参数:
        repo_path (str, optional): Git 仓库的本地路径
            - 默认为 None，表示使用当前脚本所在目录
            - 可以指定任意有效的 Git 仓库路径
        
        commit_message (str, optional): 提交信息
            - 默认为 None，将自动生成带时间戳的信息
            - 格式: "Auto commit: YYYY-MM-DD HH:MM:SS"
        
        branch (str): 要推送的目标分支名称
            - 默认为 "master"
            - 常用值: "master", "main", "develop"
        
        force (bool): 是否强制推送
            - 默认为 False
            - 设为 True 时会使用 --force 参数覆盖远程历史
        
        token (str, optional): GitHub Personal Access Token
            - 用于私有仓库或需要认证的推送
            - 如果提供，会临时配置到远程 URL 中
        
        username (str, optional): GitHub 用户名
            - 与 token 配合使用
        
        use_saved_token (bool): 是否使用已保存的 Token
            - 默认为 True
            - 如果没有提供 token 参数，会尝试加载已保存的 Token
    
    返回:
        bool: 操作是否成功
            - True: 所有操作成功完成
            - False: 任一步骤失败
    
    使用示例:
        # 示例1: 使用默认设置提交当前目录
        >>> auto_push()
        
        # 示例2: 使用 Token 认证推送
        >>> auto_push(token="ghp_xxxx", username="your_username")
        
        # 示例3: 推送到 main 分支并强制覆盖
        >>> auto_push(branch="main", force=True)
    
    注意事项:
        - 如果没有任何更改，函数会提示并返回 True
        - 强制推送 (force=True) 会覆盖远程历史，请谨慎使用
        - Token 会在推送后自动从远程 URL 中移除，保护安全
        - 确保已配置 Git 用户信息和远程仓库访问权限
    """
    
    # ========== Step 1: 确定仓库路径 ==========
    # 如果未指定路径，使用脚本所在目录作为默认仓库路径
    if repo_path is None:
        repo_path = os.path.dirname(os.path.abspath(__file__))
    
    # 输出当前操作的仓库路径
    print(f"📁 仓库路径: {repo_path}")
    
    # ========== Step 2: 验证 Git 仓库 ==========
    # 检查目录是否包含 .git 文件夹
    if not check_git_repo(repo_path):
        print("❌ 错误: 当前目录不是有效的 Git 仓库")
        return False
    
    # ========== Step 3: 检查并配置远程仓库 ==========
    # 检查是否已配置远程仓库 origin
    if not check_remote_exists(repo_path):
        print("⚠️ 未配置远程仓库 origin")
        print("❌ 错误: 请先配置远程仓库，使用命令:")
        print("   git remote add origin <远程仓库URL>")
        print("   例如: git remote add origin https://github.com/user/repo.git")
        return False
    
    # 获取并显示远程仓库 URL
    remote_url = get_remote_url(repo_path)
    if remote_url:
        print(f"🔗 远程仓库: {remote_url}")
    
    # ========== Step 3.5: 配置 Token 认证 ==========
    # 标记是否使用了 Token（用于后续恢复 URL）
    token_configured = False
    
    # 如果没有提供 token，尝试加载已保存的 token
    if token is None and use_saved_token:
        saved_token, saved_username = load_token()
        if saved_token:
            token = saved_token
            if username is None:
                username = saved_username
            print("🔑 使用已保存的 Token 进行认证")
    
    # 如果仍然没有 token，提示用户获取
    if token is None:
        print("\n⚠️ 未检测到 Token 配置")
        print("   私有仓库或需要认证的推送可能会失败")
        user_input = input("   是否现在获取 Token? (y/n): ").strip().lower()
        if user_input == 'y':
            # 尝试自动获取 Token
            success, new_token, new_username = prompt_get_token()
            if success:
                token = new_token
                username = new_username
    
    # 如果有 token，配置认证
    if token:
        print("🔐 正在配置 Token 认证...")
        if configure_git_credential(repo_path, token, username):
            token_configured = True
            print("✅ Token 认证配置成功")
        else:
            print("⚠️ Token 认证配置失败，将尝试无认证推送")
    
    # ========== Step 4: 检查工作区状态 ==========
    # 获取当前工作区的更改状态
    status = git_status(repo_path)
    if not status:
        # 没有任何更改，直接返回成功
        print("✅ 没有需要提交的更改")
        return True
    
    # 显示检测到的更改列表
    print(f"📝 检测到以下更改:\n{status}")
    
    # ========== Step 5: 暂存所有更改 ==========
    print("\n🔄 正在添加更改...")
    success, output = git_add_all(repo_path)
    if not success:
        # 添加失败，输出错误信息并返回
        print(f"❌ 添加失败: {output}")
        return False
    print("✅ 添加成功")
    
    # ========== Step 6: 生成提交信息 ==========
    # 如果未指定提交信息，自动生成带时间戳的默认信息
    if commit_message is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"Auto commit: {timestamp}"
    
    # ========== Step 7: 提交更改 ==========
    print(f"\n📤 正在提交: {commit_message}")
    success, output = git_commit(repo_path, commit_message)
    if not success:
        # 检查是否是因为没有更改导致的失败
        if "nothing to commit" in output:
            print("✅ 没有需要提交的更改")
        else:
            # 其他原因导致的提交失败
            print(f"❌ 提交失败: {output}")
            return False
    else:
        print(f"✅ 提交成功")
    
    # ========== Step 8: 推送到远程仓库 ==========
    print(f"\n🚀 正在推送到 {branch} 分支...")
    success, output, is_new_branch = git_push(repo_path, branch, force)
    
    # ========== Step 9: 恢复远程 URL（移除 Token）==========
    # 无论推送成功与否，都要恢复 URL 以保护 Token 安全
    if token_configured:
        print("🔒 正在恢复远程 URL（移除 Token）...")
        if restore_remote_url(repo_path):
            print("✅ 远程 URL 已恢复")
        else:
            print("⚠️ 恢复远程 URL 失败，请手动检查")
    
    if not success:
        # 推送失败，输出错误信息和可能的解决方案
        print(f"❌ 推送失败: {output}")
        # 提供常见问题的解决建议
        if "rejected" in output.lower():
            print("\n💡 提示: 远程分支有更新，请先执行 git pull 合并远程更改")
            print("   或使用 -f 参数强制推送（会覆盖远程历史）")
        elif "does not exist" in output.lower() or "not found" in output.lower():
            print("\n💡 提示: 远程仓库可能不存在，请检查仓库 URL 是否正确")
        elif "authentication" in output.lower() or "403" in output or "401" in output:
            print("\n💡 提示: 认证失败，请检查 Token 是否有效或是否有仓库写入权限")
            print("   使用 --token 参数提供有效的 GitHub Personal Access Token")
        return False
    
    # ========== 完成 ==========
    if is_new_branch:
        print(f"✅ 推送成功! (已在远程创建新分支 '{branch}')")
    else:
        print("✅ 推送成功!")
    print(f"\n🎉 代码已成功提交到远程仓库")
    return True


# ==============================================================================
# 程序入口函数
# ==============================================================================

def main():
    """
    主函数 - 程序命令行入口
    
    解析命令行参数并调用 auto_push 函数执行自动提交推送操作。
    
    支持的命令行参数:
        -p, --path        指定 Git 仓库路径（默认为脚本所在目录）
        -m, --message     指定提交信息（默认为带时间戳的自动信息）
        -b, --branch      指定目标分支（默认为 master）
        -f, --force       启用强制推送模式
        -t, --token       GitHub Personal Access Token
        -u, --username    GitHub 用户名
        --save-token      保存 Token 到本地配置
        --delete-token    删除已保存的 Token
        --no-saved-token  不使用已保存的 Token
    
    退出码:
        0: 操作成功
        1: 操作失败
    
    使用示例:
        # 使用默认设置
        $ python git_auto_push.py
        
        # 指定提交信息
        $ python git_auto_push.py -m "修复了一个重要bug"
        
        # 使用 Token 认证推送
        $ python git_auto_push.py -t ghp_xxxx -u username
        
        # 保存 Token 以便后续使用
        $ python git_auto_push.py -t ghp_xxxx -u username --save-token
        
        # 删除已保存的 Token
        $ python git_auto_push.py --delete-token
        
        # 组合使用所有参数
        $ python git_auto_push.py -p /path/to/repo -m "更新功能" -b main -f
    """
    # 导入命令行参数解析模块（延迟导入，仅在需要时加载）
    import argparse
    
    # 创建参数解析器，设置程序描述信息
    parser = argparse.ArgumentParser(
        description="GitHub 自动提交脚本 - 一键完成 add、commit、push 操作，支持 Token 认证"
    )
    
    # 添加命令行参数定义
    # -p/--path: 仓库路径参数
    parser.add_argument(
        "-p", "--path",
        help="仓库路径，默认为脚本所在目录",
        default=None
    )
    
    # -m/--message: 提交信息参数
    parser.add_argument(
        "-m", "--message",
        help="提交信息，默认为带时间戳的信息",
        default=None
    )
    
    # -b/--branch: 分支名称参数
    parser.add_argument(
        "-b", "--branch",
        help="分支名称，默认为 master",
        default="master"
    )
    
    # -f/--force: 强制推送开关
    parser.add_argument(
        "-f", "--force",
        help="强制推送（会覆盖远程历史，请谨慎使用）",
        action="store_true"
    )
    
    # -t/--token: GitHub Token 参数
    parser.add_argument(
        "-t", "--token",
        help="GitHub Personal Access Token，用于认证推送",
        default=None
    )
    
    # -u/--username: GitHub 用户名参数
    parser.add_argument(
        "-u", "--username",
        help="GitHub 用户名，与 Token 配合使用",
        default=None
    )
    
    # --save-token: 保存 Token 开关
    parser.add_argument(
        "--save-token",
        help="保存 Token 到本地配置文件，下次可自动使用",
        action="store_true"
    )
    
    # --delete-token: 删除 Token 开关
    parser.add_argument(
        "--delete-token",
        help="删除已保存的 Token 配置",
        action="store_true"
    )
    
    # --no-saved-token: 不使用已保存的 Token
    parser.add_argument(
        "--no-saved-token",
        help="不使用已保存的 Token，即使存在",
        action="store_true"
    )
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 处理删除 Token 的请求
    if args.delete_token:
        delete_token()
        sys.exit(0)
    
    # 如果提供了 Token 并且要求保存
    if args.token and args.save_token:
        save_token(args.token, args.username)
    
    # 调用核心业务函数执行自动提交推送
    success = auto_push(
        repo_path=args.path,
        commit_message=args.message,
        branch=args.branch,
        force=args.force,
        token=args.token,
        username=args.username,
        use_saved_token=not args.no_saved_token
    )
    
    # 根据执行结果设置退出码
    # 成功返回 0，失败返回 1（符合 Unix 惯例）
    sys.exit(0 if success else 1)


# ==============================================================================
# 脚本入口点
# ==============================================================================
# 当脚本被直接运行时（而非被导入时），执行 main 函数
if __name__ == "__main__":
    main()
