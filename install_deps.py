#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
依赖安装脚本

将项目所需依赖下载到 libs 文件夹中，实现项目依赖的本地化管理。

使用方法:
    python install_deps.py

功能:
    1. 创建 libs 文件夹（如果不存在）
    2. 下载依赖到 libs 文件夹
    3. 安装 Playwright 浏览器（可选）
"""

import subprocess
import sys
import os

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIBS_DIR = os.path.join(SCRIPT_DIR, 'libs')
REQUIREMENTS_FILE = os.path.join(SCRIPT_DIR, 'requirements.txt')


def create_libs_dir():
    """创建 libs 文件夹"""
    if not os.path.exists(LIBS_DIR):
        os.makedirs(LIBS_DIR)
        print(f"✅ 创建 libs 文件夹: {LIBS_DIR}")
    else:
        print(f"📁 libs 文件夹已存在: {LIBS_DIR}")


def install_dependencies():
    """安装依赖到 libs 文件夹"""
    print("\n📦 正在安装依赖到 libs 文件夹...")
    
    try:
        # 使用 pip install -t 将依赖安装到指定目录
        result = subprocess.run(
            [
                sys.executable, "-m", "pip", "install",
                "-r", REQUIREMENTS_FILE,
                "-t", LIBS_DIR,
                "--upgrade"
            ],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ 依赖安装成功")
            print(result.stdout)
        else:
            print(f"⚠️ 依赖安装警告: {result.stderr}")
            
    except Exception as e:
        print(f"❌ 依赖安装失败: {e}")
        return False
    
    return True


def install_playwright_browser():
    """安装 Playwright 浏览器"""
    print("\n🌐 是否安装 Playwright 浏览器? (用于自动获取 Token)")
    user_input = input("   输入 y 安装，其他跳过: ").strip().lower()
    
    if user_input == 'y':
        print("📦 正在安装 Playwright Chromium 浏览器...")
        try:
            # 设置环境变量，让 playwright 使用 libs 目录
            env = os.environ.copy()
            env['PYTHONPATH'] = LIBS_DIR + os.pathsep + env.get('PYTHONPATH', '')
            
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                capture_output=True,
                text=True,
                env=env
            )
            
            if result.returncode == 0:
                print("✅ Playwright 浏览器安装成功")
            else:
                print(f"⚠️ Playwright 浏览器安装警告: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Playwright 浏览器安装失败: {e}")
    else:
        print("⏭️ 跳过 Playwright 浏览器安装")


def create_init_file():
    """在 libs 文件夹中创建 __init__.py"""
    init_file = os.path.join(LIBS_DIR, '__init__.py')
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write('# libs package\n')
        print(f"✅ 创建 {init_file}")


def main():
    """主函数"""
    print("=" * 60)
    print("🔧 Git Auto Push 依赖安装工具")
    print("=" * 60)
    
    # 1. 创建 libs 文件夹
    create_libs_dir()
    
    # 2. 创建 __init__.py
    create_init_file()
    
    # 3. 检查 requirements.txt 是否存在
    if not os.path.exists(REQUIREMENTS_FILE):
        print(f"❌ 未找到 requirements.txt: {REQUIREMENTS_FILE}")
        return
    
    # 4. 安装依赖
    if install_dependencies():
        # 5. 安装 Playwright 浏览器（可选）
        install_playwright_browser()
    
    print("\n" + "=" * 60)
    print("✅ 依赖安装完成!")
    print("=" * 60)
    print(f"\n依赖已安装到: {LIBS_DIR}")
    print("\n现在可以运行 git_auto_push.py 了")


if __name__ == "__main__":
    main()
