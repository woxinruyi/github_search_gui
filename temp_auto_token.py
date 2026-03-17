#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GitHub Token 自动获取模块

================================================================================
                              业务流程图
================================================================================

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                         检测到无可用 Token                                │
    └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                      询问用户是否自动获取 Token                           │
    └─────────────────────────────────────────────────────────────────────────┘
                                      │
                          ┌───────────┴───────────┐
                          │                       │
                          ▼                       ▼
                       [是]                    [否] ──────► 提示手动配置
                          │
                          ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                      Step 1: 启动浏览器                                   │
    │                      打开 GitHub 登录页面                                 │
    └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                      Step 2: 等待用户登录                                 │
    │                      检测登录状态                                         │
    └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                      Step 3: 跳转到 Token 创建页面                        │
    └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                      Step 4: 自动填写 Token 信息                          │
    │                      - Note: git_auto_push_token                         │
    │                      - Scopes: repo                                      │
    └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                      Step 5: 生成并获取 Token                             │
    └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                      Step 6: 保存 Token 到本地                            │
    └─────────────────────────────────────────────────────────────────────────┘

================================================================================
                              数据流程图
================================================================================

    ┌──────────────────┐
    │   用户账号密码    │
    │  (浏览器输入)     │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐     ┌──────────────────┐
    │   GitHub 登录    │────►│   登录成功       │
    │   页面           │     │   Session        │
    └──────────────────┘     └────────┬─────────┘
                                      │
                                      ▼
                             ┌──────────────────┐
                             │   Token 创建页   │
                             │   settings/      │
                             │   tokens/new     │
                             └────────┬─────────┘
                                      │
                                      ▼
                             ┌──────────────────┐
                             │   生成 Token     │
                             │   ghp_xxxx...    │
                             └────────┬─────────┘
                                      │
                                      ▼
                             ┌──────────────────┐
                             │   保存到本地     │
                             │   .git_token_    │
                             │   config.json    │
                             └──────────────────┘

================================================================================
"""

import os
import json
import time
import webbrowser
from datetime import datetime

# Token 配置文件路径
TOKEN_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.git_token_config.json')


def check_playwright_installed():
    """
    检查 Playwright 是否已安装
    
    返回:
        bool: True 表示已安装，False 表示未安装
    """
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        return False


def install_playwright():
    """
    安装 Playwright 及浏览器
    
    返回:
        bool: 安装是否成功
    """
    import subprocess
    
    print("📦 正在安装 Playwright...")
    try:
        # 安装 playwright 包
        subprocess.run(["pip", "install", "playwright"], check=True)
        # 安装浏览器
        subprocess.run(["playwright", "install", "chromium"], check=True)
        print("✅ Playwright 安装成功")
        return True
    except Exception as e:
        print(f"❌ Playwright 安装失败: {e}")
        return False


def save_token(token, username=None):
    """
    保存 Token 到本地配置文件
    
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
    从本地配置文件加载 Token
    
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


def auto_get_token_with_playwright():
    """
    使用 Playwright 自动获取 GitHub Token
    
    流程:
        1. 打开浏览器，跳转到 GitHub 登录页
        2. 等待用户登录
        3. 跳转到 Token 创建页面
        4. 自动填写 Token 信息
        5. 生成并获取 Token
        6. 保存到本地
    
    返回:
        tuple: (success, token, username)
    """
    if not check_playwright_installed():
        print("⚠️ Playwright 未安装")
        user_input = input("是否自动安装 Playwright? (y/n): ").strip().lower()
        if user_input == 'y':
            if not install_playwright():
                return False, None, None
        else:
            return False, None, None
    
    from playwright.sync_api import sync_playwright
    
    print("\n🌐 正在启动浏览器...")
    print("📝 请在浏览器中完成 GitHub 登录")
    print("   登录后将自动跳转到 Token 创建页面\n")
    
    token = None
    username = None
    
    try:
        with sync_playwright() as p:
            # 启动浏览器（非无头模式，让用户可以看到并操作）
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            # Step 1: 跳转到 GitHub 登录页
            print("🔗 正在打开 GitHub 登录页面...")
            page.goto("https://github.com/login")
            
            # Step 2: 等待用户登录
            print("⏳ 等待用户登录...")
            print("   请在浏览器中输入您的 GitHub 账号密码")
            
            # 等待登录成功（检测 URL 变化或特定元素出现）
            # 最多等待 5 分钟
            max_wait = 300  # 秒
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                current_url = page.url
                # 检查是否已登录（不在登录页面）
                if "github.com/login" not in current_url and "github.com" in current_url:
                    # 尝试获取用户名
                    try:
                        # 等待页面加载
                        page.wait_for_load_state("networkidle", timeout=5000)
                        # 尝试从页面获取用户名
                        user_menu = page.locator('[data-login]')
                        if user_menu.count() > 0:
                            username = user_menu.first.get_attribute('data-login')
                            print(f"✅ 登录成功! 用户: {username}")
                            break
                    except:
                        pass
                    
                    # 如果无法获取用户名，但已离开登录页，也认为登录成功
                    if "github.com/login" not in current_url:
                        print("✅ 检测到登录成功")
                        break
                
                time.sleep(1)
            else:
                print("❌ 登录超时")
                browser.close()
                return False, None, None
            
            # Step 3: 跳转到 Token 创建页面
            print("\n🔗 正在跳转到 Token 创建页面...")
            page.goto("https://github.com/settings/tokens/new")
            page.wait_for_load_state("networkidle")
            
            # 检查是否需要重新登录（有时访问设置页需要确认密码）
            if "password" in page.url.lower() or "confirm" in page.url.lower():
                print("⚠️ GitHub 需要确认密码，请在浏览器中输入密码")
                # 等待用户确认密码
                page.wait_for_url("**/settings/tokens/new", timeout=120000)
            
            # Step 4: 填写 Token 信息
            print("📝 正在填写 Token 信息...")
            
            # 填写 Note
            note_input = page.locator('input[name="note"], #token_description, [placeholder*="Note"]')
            if note_input.count() > 0:
                note_input.first.fill("git_auto_push_token")
            else:
                # 尝试其他选择器
                page.fill('input[type="text"]', "git_auto_push_token")
            
            # 勾选 repo 权限
            print("🔐 正在设置权限 (repo)...")
            repo_checkbox = page.locator('input[type="checkbox"][value="repo"], input#scope_repo')
            if repo_checkbox.count() > 0:
                if not repo_checkbox.first.is_checked():
                    repo_checkbox.first.click()
            else:
                # 尝试通过文本查找
                page.locator('text=repo').first.click()
            
            # Step 5: 生成 Token
            print("🔄 正在生成 Token...")
            generate_btn = page.locator('button:has-text("Generate token")')
            if generate_btn.count() > 0:
                generate_btn.first.click()
            else:
                page.click('button[type="submit"]')
            
            # 等待页面跳转
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            # Step 6: 获取生成的 Token
            print("🔍 正在获取 Token...")
            
            # Token 通常显示在 code 元素中
            token_element = page.locator('code, [class*="token"], [id*="token"]')
            
            for i in range(token_element.count()):
                text = token_element.nth(i).inner_text()
                if text.startswith('ghp_') or text.startswith('github_pat_'):
                    token = text.strip()
                    print(f"✅ Token 获取成功: {token[:10]}...")
                    break
            
            if not token:
                # 尝试从页面中查找 ghp_ 开头的文本
                page_content = page.content()
                import re
                match = re.search(r'(ghp_[a-zA-Z0-9]{36})', page_content)
                if match:
                    token = match.group(1)
                    print(f"✅ Token 获取成功: {token[:10]}...")
            
            # 关闭浏览器
            print("\n🔒 正在关闭浏览器...")
            browser.close()
            
            if token:
                # 保存 Token
                save_token(token, username)
                return True, token, username
            else:
                print("❌ 未能获取 Token，请手动复制")
                return False, None, None
                
    except Exception as e:
        print(f"❌ 自动获取 Token 失败: {e}")
        return False, None, None


def auto_get_token_simple():
    """
    简单模式：打开浏览器让用户手动获取 Token
    
    流程:
        1. 打开浏览器到 Token 创建页面
        2. 提示用户手动操作
        3. 等待用户输入 Token
    
    返回:
        tuple: (success, token, username)
    """
    print("\n🌐 正在打开 GitHub Token 创建页面...")
    print("   请在浏览器中完成以下操作：")
    print("   1. 登录 GitHub 账号")
    print("   2. 填写 Token 名称 (如: git_auto_push)")
    print("   3. 选择过期时间")
    print("   4. 勾选 'repo' 权限")
    print("   5. 点击 'Generate token'")
    print("   6. 复制生成的 Token\n")
    
    # 打开浏览器
    webbrowser.open("https://github.com/settings/tokens/new")
    
    # 等待用户输入
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


def prompt_get_token():
    """
    提示用户获取 Token 的入口函数
    
    询问用户选择获取方式：
        1. 自动获取（使用 Playwright）
        2. 手动获取（打开浏览器）
        3. 跳过
    
    返回:
        tuple: (success, token, username)
    """
    print("\n" + "=" * 60)
    print("🔑 未检测到 GitHub Token 配置")
    print("=" * 60)
    print("\n请选择获取 Token 的方式：")
    print("  1. 自动获取 (使用 Playwright 自动化浏览器)")
    print("  2. 手动获取 (打开浏览器，手动操作)")
    print("  3. 跳过 (稍后手动配置)")
    print()
    
    choice = input("请输入选项 (1/2/3): ").strip()
    
    if choice == '1':
        return auto_get_token_with_playwright()
    elif choice == '2':
        return auto_get_token_simple()
    else:
        print("\n💡 您可以稍后使用以下命令配置 Token：")
        print("   python git_auto_push.py -t <your_token> -u <username> --save-token")
        print("\n   或手动创建配置文件 .git_token_config.json：")
        print('   {"token": "ghp_xxx...", "username": "your_username"}')
        return False, None, None


def main():
    """
    主函数 - 测试 Token 获取功能
    """
    # 检查是否已有 Token
    token, username = load_token()
    
    if token:
        print(f"✅ 已存在 Token 配置")
        print(f"   Token: {token[:10]}...")
        if username:
            print(f"   用户名: {username}")
        
        user_input = input("\n是否重新获取 Token? (y/n): ").strip().lower()
        if user_input != 'y':
            return
    
    # 获取新 Token
    success, new_token, new_username = prompt_get_token()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 Token 配置完成!")
        print("=" * 60)
        print(f"   Token: {new_token[:10]}...")
        if new_username:
            print(f"   用户名: {new_username}")
        print("\n现在可以使用 git_auto_push.py 进行自动推送了")
    else:
        print("\n⚠️ Token 获取未完成")


if __name__ == "__main__":
    main()
