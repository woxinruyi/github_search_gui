#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Git Auto Push GUI - 开源项目提交图形界面

================================================================================
                              业务流程图
================================================================================

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                           启动 GUI 界面                                  │
    └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                      主界面显示                                          │
    │  ┌─────────────────────────────────────────────────────────────────┐   │
    │  │  仓库路径: [________________] [浏览]                             │   │
    │  │  远程地址: [________________]                                    │   │
    │  │  分支名称: [________________]                                    │   │
    │  │  提交信息: [________________]                                    │   │
    │  │  ☐ 强制推送                                                      │   │
    │  │                                                                  │   │
    │  │  Token 配置:                                                     │   │
    │  │  Token:    [________________] [获取Token]                        │   │
    │  │  用户名:   [________________]                                    │   │
    │  │  ☐ 保存 Token                                                    │   │
    │  │                                                                  │   │
    │  │  [提交并推送]  [仅提交]  [仅推送]                                 │   │
    │  │                                                                  │   │
    │  │  日志输出:                                                       │   │
    │  │  ┌──────────────────────────────────────────────────────────┐   │   │
    │  │  │                                                          │   │   │
    │  │  │                                                          │   │   │
    │  │  └──────────────────────────────────────────────────────────┘   │   │
    │  └─────────────────────────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────────────────────────┘

================================================================================
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys

# 添加 libs 文件夹到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIBS_DIR = os.path.join(SCRIPT_DIR, 'libs')
if os.path.exists(LIBS_DIR) and LIBS_DIR not in sys.path:
    sys.path.insert(0, LIBS_DIR)

# 导入核心功能
from git_auto_push import (
    auto_push, save_token, load_token, delete_token,
    check_git_repo, get_remote_url, git_status,
    check_remote_exists, prompt_get_token
)


class GitAutoPushGUI:
    """Git Auto Push 图形界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Git Auto Push - 开源项目提交工具")
        self.root.geometry("700x650")
        self.root.resizable(True, True)
        
        # 设置图标（如果存在）
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # 创建主框架
        self.create_widgets()
        
        # 加载已保存的 Token
        self.load_saved_token()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """创建界面组件"""
        
        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ========== 仓库配置区域 ==========
        repo_frame = ttk.LabelFrame(main_frame, text="仓库配置", padding="10")
        repo_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 仓库路径
        ttk.Label(repo_frame, text="仓库路径:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.repo_path_var = tk.StringVar(value=SCRIPT_DIR)
        self.repo_path_entry = ttk.Entry(repo_frame, textvariable=self.repo_path_var, width=50)
        self.repo_path_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Button(repo_frame, text="浏览", command=self.browse_repo).grid(row=0, column=2, padx=5, pady=5)
        
        # 远程地址
        ttk.Label(repo_frame, text="远程地址:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.remote_url_var = tk.StringVar()
        self.remote_url_entry = ttk.Entry(repo_frame, textvariable=self.remote_url_var, width=50)
        self.remote_url_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Button(repo_frame, text="刷新", command=self.refresh_remote_url).grid(row=1, column=2, padx=5, pady=5)
        
        # 分支名称
        ttk.Label(repo_frame, text="分支名称:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.branch_var = tk.StringVar(value="master")
        self.branch_entry = ttk.Combobox(repo_frame, textvariable=self.branch_var, values=["master", "main", "develop"])
        self.branch_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 提交信息
        ttk.Label(repo_frame, text="提交信息:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.commit_msg_var = tk.StringVar()
        self.commit_msg_entry = ttk.Entry(repo_frame, textvariable=self.commit_msg_var, width=50)
        self.commit_msg_entry.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        
        # 强制推送
        self.force_push_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(repo_frame, text="强制推送 (会覆盖远程历史，请谨慎使用)", 
                       variable=self.force_push_var).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        repo_frame.columnconfigure(1, weight=1)
        
        # ========== Token 配置区域 ==========
        token_frame = ttk.LabelFrame(main_frame, text="Token 配置", padding="10")
        token_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Token
        ttk.Label(token_frame, text="Token:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.token_var = tk.StringVar()
        self.token_entry = ttk.Entry(token_frame, textvariable=self.token_var, width=40, show="*")
        self.token_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Token 按钮
        token_btn_frame = ttk.Frame(token_frame)
        token_btn_frame.grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(token_btn_frame, text="获取", command=self.get_token).pack(side=tk.LEFT, padx=2)
        ttk.Button(token_btn_frame, text="显示", command=self.toggle_token_visibility).pack(side=tk.LEFT, padx=2)
        
        # 用户名
        ttk.Label(token_frame, text="用户名:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(token_frame, textvariable=self.username_var, width=40)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 保存 Token
        self.save_token_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(token_frame, text="保存 Token 到本地", 
                       variable=self.save_token_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 删除 Token 按钮
        ttk.Button(token_frame, text="删除已保存的 Token", 
                  command=self.delete_saved_token).grid(row=2, column=2, padx=5, pady=5)
        
        token_frame.columnconfigure(1, weight=1)
        
        # ========== 操作按钮区域 ==========
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        # 主要操作按钮
        ttk.Button(btn_frame, text="🚀 提交并推送", command=self.commit_and_push, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📝 仅提交", command=self.commit_only).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📤 仅推送", command=self.push_only).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 检查状态", command=self.check_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🧹 清空日志", command=self.clear_log).pack(side=tk.RIGHT, padx=5)
        
        # ========== 日志输出区域 ==========
        log_frame = ttk.LabelFrame(main_frame, text="日志输出", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置日志文本样式
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("warning", foreground="orange")
        self.log_text.tag_configure("info", foreground="blue")
        
        # ========== 状态栏 ==========
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # 刷新远程地址
        self.refresh_remote_url()
    
    def log(self, message, tag=None):
        """输出日志"""
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
    
    def browse_repo(self):
        """浏览选择仓库路径"""
        path = filedialog.askdirectory(initialdir=self.repo_path_var.get())
        if path:
            self.repo_path_var.set(path)
            self.refresh_remote_url()
    
    def refresh_remote_url(self):
        """刷新远程仓库地址"""
        repo_path = self.repo_path_var.get()
        if repo_path and check_git_repo(repo_path):
            url = get_remote_url(repo_path)
            if url:
                self.remote_url_var.set(url)
                self.status_var.set(f"已加载仓库: {repo_path}")
            else:
                self.remote_url_var.set("")
                self.status_var.set("未配置远程仓库")
        else:
            self.remote_url_var.set("")
            self.status_var.set("无效的 Git 仓库")
    
    def load_saved_token(self):
        """加载已保存的 Token"""
        token, username = load_token()
        if token:
            self.token_var.set(token)
            if username:
                self.username_var.set(username)
            self.log("✅ 已加载保存的 Token 配置", "success")
    
    def toggle_token_visibility(self):
        """切换 Token 显示/隐藏"""
        if self.token_entry.cget("show") == "*":
            self.token_entry.config(show="")
        else:
            self.token_entry.config(show="*")
    
    def get_token(self):
        """获取 Token"""
        import webbrowser
        
        result = messagebox.askyesnocancel(
            "获取 Token",
            "选择获取 Token 的方式:\n\n"
            "是 - 打开浏览器手动获取\n"
            "否 - 使用自动化浏览器获取\n"
            "取消 - 取消操作"
        )
        
        if result is True:
            # 手动获取
            webbrowser.open("https://github.com/settings/tokens/new")
            self.log("🌐 已打开 GitHub Token 创建页面", "info")
            self.log("   请在浏览器中完成以下操作:", "info")
            self.log("   1. 登录 GitHub 账号", "info")
            self.log("   2. 填写 Token 名称", "info")
            self.log("   3. 勾选 'repo' 权限", "info")
            self.log("   4. 点击 'Generate token'", "info")
            self.log("   5. 复制 Token 并粘贴到上方输入框", "info")
        elif result is False:
            # 自动获取
            self.log("🔄 正在启动自动化浏览器...", "info")
            threading.Thread(target=self._auto_get_token, daemon=True).start()
    
    def _auto_get_token(self):
        """自动获取 Token（在后台线程中运行）"""
        try:
            success, token, username = prompt_get_token()
            if success:
                self.root.after(0, lambda: self.token_var.set(token))
                if username:
                    self.root.after(0, lambda: self.username_var.set(username))
                self.root.after(0, lambda: self.log("✅ Token 获取成功", "success"))
            else:
                self.root.after(0, lambda: self.log("❌ Token 获取失败", "error"))
        except Exception as e:
            self.root.after(0, lambda: self.log(f"❌ 错误: {e}", "error"))
    
    def delete_saved_token(self):
        """删除已保存的 Token"""
        if messagebox.askyesno("确认删除", "确定要删除已保存的 Token 配置吗?"):
            if delete_token():
                self.token_var.set("")
                self.username_var.set("")
                self.log("✅ Token 配置已删除", "success")
            else:
                self.log("⚠️ Token 配置不存在或删除失败", "warning")
    
    def check_status(self):
        """检查仓库状态"""
        repo_path = self.repo_path_var.get()
        
        if not repo_path:
            self.log("❌ 请先选择仓库路径", "error")
            return
        
        if not check_git_repo(repo_path):
            self.log("❌ 当前目录不是有效的 Git 仓库", "error")
            return
        
        self.log("=" * 50, "info")
        self.log("📁 仓库状态检查", "info")
        self.log("=" * 50, "info")
        
        # 检查远程仓库
        if check_remote_exists(repo_path):
            url = get_remote_url(repo_path)
            self.log(f"🔗 远程仓库: {url}", "success")
        else:
            self.log("⚠️ 未配置远程仓库", "warning")
        
        # 检查工作区状态
        status = git_status(repo_path)
        if status:
            self.log("📝 待提交的更改:", "info")
            for line in status.split('\n'):
                if line.strip():
                    self.log(f"   {line}", "info")
        else:
            self.log("✅ 工作区干净，没有待提交的更改", "success")
        
        self.status_var.set("状态检查完成")
    
    def commit_and_push(self):
        """提交并推送"""
        self._run_git_operation("commit_and_push")
    
    def commit_only(self):
        """仅提交"""
        self._run_git_operation("commit_only")
    
    def push_only(self):
        """仅推送"""
        self._run_git_operation("push_only")
    
    def _run_git_operation(self, operation):
        """运行 Git 操作（在后台线程中）"""
        # 获取参数
        repo_path = self.repo_path_var.get()
        commit_msg = self.commit_msg_var.get() or None
        branch = self.branch_var.get() or "master"
        force = self.force_push_var.get()
        token = self.token_var.get() or None
        username = self.username_var.get() or None
        save_token_flag = self.save_token_var.get()
        
        # 验证
        if not repo_path:
            self.log("❌ 请先选择仓库路径", "error")
            return
        
        if not check_git_repo(repo_path):
            self.log("❌ 当前目录不是有效的 Git 仓库", "error")
            return
        
        # 保存 Token
        if token and save_token_flag:
            save_token(token, username)
        
        # 禁用按钮
        self.status_var.set("正在执行...")
        
        # 在后台线程中执行
        threading.Thread(
            target=self._execute_operation,
            args=(operation, repo_path, commit_msg, branch, force, token, username),
            daemon=True
        ).start()
    
    def _execute_operation(self, operation, repo_path, commit_msg, branch, force, token, username):
        """执行 Git 操作"""
        try:
            self.root.after(0, lambda: self.log("=" * 50, "info"))
            self.root.after(0, lambda: self.log(f"🚀 开始执行: {operation}", "info"))
            self.root.after(0, lambda: self.log("=" * 50, "info"))
            
            # 重定向输出
            import io
            from contextlib import redirect_stdout
            
            output = io.StringIO()
            
            with redirect_stdout(output):
                if operation == "commit_and_push":
                    success = auto_push(
                        repo_path=repo_path,
                        commit_message=commit_msg,
                        branch=branch,
                        force=force,
                        token=token,
                        username=username,
                        use_saved_token=True
                    )
                elif operation == "commit_only":
                    from git_auto_push import git_add_all, git_commit
                    from datetime import datetime
                    
                    # 添加文件
                    success, msg = git_add_all(repo_path)
                    if success:
                        # 提交
                        if not commit_msg:
                            commit_msg = f"Auto commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        success, msg = git_commit(repo_path, commit_msg)
                        print(f"提交结果: {msg}")
                    else:
                        print(f"添加失败: {msg}")
                        success = False
                elif operation == "push_only":
                    from git_auto_push import git_push, configure_git_credential, restore_remote_url
                    
                    # 配置 Token
                    if token:
                        configure_git_credential(repo_path, token, username)
                    
                    # 推送
                    success, msg, is_new = git_push(repo_path, branch, force)
                    print(f"推送结果: {msg}")
                    
                    # 恢复 URL
                    if token:
                        restore_remote_url(repo_path)
            
            # 显示输出
            output_text = output.getvalue()
            for line in output_text.split('\n'):
                if line.strip():
                    tag = "success" if "✅" in line or "成功" in line else \
                          "error" if "❌" in line or "失败" in line else \
                          "warning" if "⚠️" in line else "info"
                    self.root.after(0, lambda l=line, t=tag: self.log(l, t))
            
            # 更新状态
            if success:
                self.root.after(0, lambda: self.status_var.set("操作成功"))
                self.root.after(0, lambda: self.log("🎉 操作完成!", "success"))
            else:
                self.root.after(0, lambda: self.status_var.set("操作失败"))
                self.root.after(0, lambda: self.log("❌ 操作失败", "error"))
                
        except Exception as e:
            self.root.after(0, lambda: self.log(f"❌ 错误: {e}", "error"))
            self.root.after(0, lambda: self.status_var.set("发生错误"))
    
    def on_closing(self):
        """关闭窗口"""
        self.root.destroy()


def main():
    """主函数"""
    root = tk.Tk()
    
    # 设置主题样式
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except:
        pass
    
    app = GitAutoPushGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
