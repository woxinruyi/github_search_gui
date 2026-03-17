#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GitHub Toolkit GUI - GitHub 工具箱

================================================================================
                              功能说明
================================================================================

整合两大功能模块：
1. GitHub 项目搜索 - 搜索热门开源项目
2. Git 项目提交 - 提交本地项目到 GitHub

================================================================================
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import json
import requests
import webbrowser

# 添加 libs 文件夹到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIBS_DIR = os.path.join(SCRIPT_DIR, 'libs')
if os.path.exists(LIBS_DIR) and LIBS_DIR not in sys.path:
    sys.path.insert(0, LIBS_DIR)

# 导入 Git 操作模块
try:
    from git_auto_push import (
        auto_push, save_token, load_token, delete_token,
        check_git_repo, get_remote_url, git_status,
        check_remote_exists, prompt_get_token,
        git_add_all, git_commit, git_push,
        configure_git_credential, restore_remote_url
    )
    GIT_MODULE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: git_auto_push module not available: {e}")
    GIT_MODULE_AVAILABLE = False


# 多语言支持
translations = {
    'zh_CN': {
        'app_title': 'GitHub 工具箱',
        'tab_search': '🔍 项目搜索',
        'tab_push': '📤 项目提交',
        # 搜索页面
        'keyword_label': '搜索关键词:',
        'sort_label': '排序方式:',
        'language_filter': '编程语言:',
        'per_page_label': '显示数量:',
        'search_button': '搜索',
        'refresh_button': '刷新',
        'clone_button': '克隆项目',
        'rank_col': '排名',
        'name_col': '项目名称',
        'stars_col': 'Star 数量',
        'forks_col': 'Fork 数量',
        'language_col': '语言',
        'status_ready': '就绪',
        'status_searching': '正在搜索...',
        'status_done': '搜索完成，共找到 {} 个项目',
        'error_empty_keyword': '请输入搜索关键词',
        'error_search_failed': '搜索失败: {}',
        'all_languages': '全部',
        # 提交页面
        'repo_path_label': '仓库路径:',
        'remote_url_label': '远程地址:',
        'branch_label': '分支名称:',
        'commit_msg_label': '提交信息:',
        'force_push': '强制推送',
        'token_label': 'Token:',
        'username_label': '用户名:',
        'save_token': '保存 Token',
        'browse_button': '浏览',
        'refresh_url_button': '刷新',
        'get_token_button': '获取',
        'show_token_button': '显示',
        'delete_token_button': '删除 Token',
        'commit_push_button': '🚀 提交并推送',
        'commit_only_button': '📝 仅提交',
        'push_only_button': '📤 仅推送',
        'check_status_button': '🔄 检查状态',
        'clear_log_button': '🧹 清空日志',
        'log_title': '日志输出',
        # 通用
        'language_switch': '切换语言',
        'about': '关于',
    },
    'en_US': {
        'app_title': 'GitHub Toolkit',
        'tab_search': '🔍 Search',
        'tab_push': '📤 Push',
        # Search page
        'keyword_label': 'Keyword:',
        'sort_label': 'Sort By:',
        'language_filter': 'Language:',
        'per_page_label': 'Results:',
        'search_button': 'Search',
        'refresh_button': 'Refresh',
        'clone_button': 'Clone',
        'rank_col': 'Rank',
        'name_col': 'Repository',
        'stars_col': 'Stars',
        'forks_col': 'Forks',
        'language_col': 'Language',
        'status_ready': 'Ready',
        'status_searching': 'Searching...',
        'status_done': 'Found {} repositories',
        'error_empty_keyword': 'Please enter a keyword',
        'error_search_failed': 'Search failed: {}',
        'all_languages': 'All',
        # Push page
        'repo_path_label': 'Repository:',
        'remote_url_label': 'Remote URL:',
        'branch_label': 'Branch:',
        'commit_msg_label': 'Message:',
        'force_push': 'Force Push',
        'token_label': 'Token:',
        'username_label': 'Username:',
        'save_token': 'Save Token',
        'browse_button': 'Browse',
        'refresh_url_button': 'Refresh',
        'get_token_button': 'Get',
        'show_token_button': 'Show',
        'delete_token_button': 'Delete Token',
        'commit_push_button': '🚀 Commit & Push',
        'commit_only_button': '📝 Commit Only',
        'push_only_button': '📤 Push Only',
        'check_status_button': '🔄 Check Status',
        'clear_log_button': '🧹 Clear Log',
        'log_title': 'Log Output',
        # Common
        'language_switch': 'Switch Language',
        'about': 'About',
    }
}

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://github.com/'
}


class GitHubToolkitGUI:
    """GitHub 工具箱 GUI"""
    
    def __init__(self, root):
        self.root = root
        self.current_lang = 'zh_CN'
        self.search_results = []
        self.last_total_count = 0
        
        # 排序选项
        self.sort_options_zh = {'stars': 'Star 数量', 'forks': 'Fork 数量', 'updated': '最近更新'}
        self.sort_options_en = {'stars': 'Stars', 'forks': 'Forks', 'updated': 'Updated'}
        self.language_options = ['All', 'Python', 'JavaScript', 'Java', 'C++', 'TypeScript', 'Go', 'Rust', 'PHP', 'C#']
        
        # 设置窗口
        self.root.title(translations[self.current_lang]['app_title'])
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # 创建界面
        self.create_widgets()
        self.update_texts()
        
        # 加载已保存的 Token
        if GIT_MODULE_AVAILABLE:
            self.load_saved_token()
    
    def create_widgets(self):
        """创建界面组件"""
        
        # 创建 Notebook（标签页）
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建搜索页面
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text=translations[self.current_lang]['tab_search'])
        self.create_search_page()
        
        # 创建提交页面
        self.push_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.push_frame, text=translations[self.current_lang]['tab_push'])
        self.create_push_page()
        
        # 底部工具栏
        self.create_toolbar()
    
    def create_search_page(self):
        """创建搜索页面"""
        
        # 控制区域
        control_frame = ttk.LabelFrame(self.search_frame, text="搜索条件", padding="10")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 第一行：关键词
        row1 = ttk.Frame(control_frame)
        row1.pack(fill=tk.X, pady=3)
        
        self.search_keyword_label = ttk.Label(row1, width=12)
        self.search_keyword_label.pack(side=tk.LEFT)
        
        self.keyword_entry = ttk.Entry(row1, width=50)
        self.keyword_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.keyword_entry.insert(0, "python")
        self.keyword_entry.bind('<Return>', lambda e: self.start_search())
        
        # 第二行：排序、语言、数量
        row2 = ttk.Frame(control_frame)
        row2.pack(fill=tk.X, pady=3)
        
        self.search_sort_label = ttk.Label(row2, width=12)
        self.search_sort_label.pack(side=tk.LEFT)
        
        self.sort_var = tk.StringVar(value=list(self.sort_options_zh.values())[0])
        self.sort_combo = ttk.Combobox(row2, textvariable=self.sort_var, 
                                       values=list(self.sort_options_zh.values()), 
                                       state='readonly', width=12)
        self.sort_combo.pack(side=tk.LEFT, padx=5)
        
        self.search_lang_label = ttk.Label(row2, width=12)
        self.search_lang_label.pack(side=tk.LEFT, padx=(10, 0))
        
        self.search_lang_var = tk.StringVar(value='All')
        self.search_lang_combo = ttk.Combobox(row2, textvariable=self.search_lang_var, 
                                              values=self.language_options, 
                                              state='readonly', width=12)
        self.search_lang_combo.pack(side=tk.LEFT, padx=5)
        
        self.search_perpage_label = ttk.Label(row2, width=12)
        self.search_perpage_label.pack(side=tk.LEFT, padx=(10, 0))
        
        self.perpage_var = tk.IntVar(value=30)
        self.perpage_spin = ttk.Spinbox(row2, from_=10, to=100, 
                                        textvariable=self.perpage_var, width=6)
        self.perpage_spin.pack(side=tk.LEFT, padx=5)
        
        # 第三行：按钮
        row3 = ttk.Frame(control_frame)
        row3.pack(fill=tk.X, pady=5)
        
        self.search_button = ttk.Button(row3, command=self.start_search)
        self.search_button.pack(side=tk.LEFT, padx=5)
        
        self.refresh_search_button = ttk.Button(row3, command=self.start_search)
        self.refresh_search_button.pack(side=tk.LEFT, padx=5)
        
        self.clone_button = ttk.Button(row3, command=self.clone_selected)
        self.clone_button.pack(side=tk.LEFT, padx=5)
        
        # 表格区域
        table_frame = ttk.Frame(self.search_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ('rank', 'name', 'stars', 'forks', 'language')
        self.search_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        self.search_tree.column('rank', width=50, anchor=tk.CENTER)
        self.search_tree.column('name', width=300)
        self.search_tree.column('stars', width=100, anchor=tk.E)
        self.search_tree.column('forks', width=100, anchor=tk.E)
        self.search_tree.column('language', width=100)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.search_tree.yview)
        self.search_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.search_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 双击打开链接
        self.search_tree.bind('<Double-1>', self.open_repo_link)
        
        # 状态栏
        self.search_status_var = tk.StringVar(value="就绪")
        self.search_status = ttk.Label(self.search_frame, textvariable=self.search_status_var, 
                                       relief=tk.SUNKEN, padding=(8, 3))
        self.search_status.pack(fill=tk.X, padx=10, pady=5)
    
    def create_push_page(self):
        """创建提交页面"""
        
        # 仓库配置区域
        repo_frame = ttk.LabelFrame(self.push_frame, text="仓库配置", padding="10")
        repo_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 仓库路径
        row1 = ttk.Frame(repo_frame)
        row1.pack(fill=tk.X, pady=3)
        
        self.push_repo_label = ttk.Label(row1, width=12)
        self.push_repo_label.pack(side=tk.LEFT)
        
        self.repo_path_var = tk.StringVar(value=SCRIPT_DIR)
        self.repo_path_entry = ttk.Entry(row1, textvariable=self.repo_path_var, width=50)
        self.repo_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.browse_button = ttk.Button(row1, command=self.browse_repo)
        self.browse_button.pack(side=tk.LEFT, padx=5)
        
        # 远程地址
        row2 = ttk.Frame(repo_frame)
        row2.pack(fill=tk.X, pady=3)
        
        self.push_remote_label = ttk.Label(row2, width=12)
        self.push_remote_label.pack(side=tk.LEFT)
        
        self.remote_url_var = tk.StringVar()
        self.remote_url_entry = ttk.Entry(row2, textvariable=self.remote_url_var, width=50)
        self.remote_url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.refresh_url_button = ttk.Button(row2, command=self.refresh_remote_url)
        self.refresh_url_button.pack(side=tk.LEFT, padx=5)
        
        # 分支和提交信息
        row3 = ttk.Frame(repo_frame)
        row3.pack(fill=tk.X, pady=3)
        
        self.push_branch_label = ttk.Label(row3, width=12)
        self.push_branch_label.pack(side=tk.LEFT)
        
        self.branch_var = tk.StringVar(value="master")
        self.branch_combo = ttk.Combobox(row3, textvariable=self.branch_var, 
                                         values=["master", "main", "develop"], width=15)
        self.branch_combo.pack(side=tk.LEFT, padx=5)
        
        self.push_msg_label = ttk.Label(row3, width=12)
        self.push_msg_label.pack(side=tk.LEFT, padx=(20, 0))
        
        self.commit_msg_var = tk.StringVar()
        self.commit_msg_entry = ttk.Entry(row3, textvariable=self.commit_msg_var, width=30)
        self.commit_msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 强制推送
        row4 = ttk.Frame(repo_frame)
        row4.pack(fill=tk.X, pady=3)
        
        self.force_push_var = tk.BooleanVar(value=False)
        self.force_push_check = ttk.Checkbutton(row4, variable=self.force_push_var)
        self.force_push_check.pack(side=tk.LEFT)
        
        # 文件列表区域
        files_frame = ttk.LabelFrame(self.push_frame, text="📁 文件列表", padding="5")
        files_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 文件列表工具栏
        files_toolbar = ttk.Frame(files_frame)
        files_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        self.refresh_files_button = ttk.Button(files_toolbar, text="🔄 刷新文件", 
                                               command=self.refresh_file_list)
        self.refresh_files_button.pack(side=tk.LEFT, padx=2)
        
        self.select_all_button = ttk.Button(files_toolbar, text="☑ 全选", 
                                            command=self.select_all_files)
        self.select_all_button.pack(side=tk.LEFT, padx=2)
        
        self.deselect_all_button = ttk.Button(files_toolbar, text="☐ 取消全选", 
                                              command=self.deselect_all_files)
        self.deselect_all_button.pack(side=tk.LEFT, padx=2)
        
        self.file_count_var = tk.StringVar(value="共 0 个文件")
        ttk.Label(files_toolbar, textvariable=self.file_count_var).pack(side=tk.RIGHT, padx=5)
        
        # 文件列表 Treeview（带勾选框）
        files_list_frame = ttk.Frame(files_frame)
        files_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建带勾选的文件列表
        columns = ('selected', 'name', 'type', 'size')
        self.files_tree = ttk.Treeview(files_list_frame, columns=columns, show='headings', height=8)
        
        self.files_tree.heading('selected', text='☑')
        self.files_tree.heading('name', text='文件名')
        self.files_tree.heading('type', text='类型')
        self.files_tree.heading('size', text='大小')
        
        self.files_tree.column('selected', width=40, anchor=tk.CENTER)
        self.files_tree.column('name', width=300)
        self.files_tree.column('type', width=80, anchor=tk.CENTER)
        self.files_tree.column('size', width=80, anchor=tk.E)
        
        files_scrollbar = ttk.Scrollbar(files_list_frame, orient=tk.VERTICAL, 
                                        command=self.files_tree.yview)
        self.files_tree.configure(yscroll=files_scrollbar.set)
        files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.files_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 点击切换勾选状态
        self.files_tree.bind('<ButtonRelease-1>', self.toggle_file_selection)
        
        # 存储文件选择状态
        self.file_selections = {}
        
        # Token 配置区域
        token_frame = ttk.LabelFrame(self.push_frame, text="Token 配置", padding="10")
        token_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Token
        row5 = ttk.Frame(token_frame)
        row5.pack(fill=tk.X, pady=3)
        
        self.push_token_label = ttk.Label(row5, width=12)
        self.push_token_label.pack(side=tk.LEFT)
        
        self.token_var = tk.StringVar()
        self.token_entry = ttk.Entry(row5, textvariable=self.token_var, width=40, show="*")
        self.token_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.get_token_button = ttk.Button(row5, command=self.get_token)
        self.get_token_button.pack(side=tk.LEFT, padx=2)
        
        self.show_token_button = ttk.Button(row5, command=self.toggle_token_visibility)
        self.show_token_button.pack(side=tk.LEFT, padx=2)
        
        # 用户名
        row6 = ttk.Frame(token_frame)
        row6.pack(fill=tk.X, pady=3)
        
        self.push_username_label = ttk.Label(row6, width=12)
        self.push_username_label.pack(side=tk.LEFT)
        
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(row6, textvariable=self.username_var, width=40)
        self.username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 保存 Token
        row7 = ttk.Frame(token_frame)
        row7.pack(fill=tk.X, pady=3)
        
        self.save_token_var = tk.BooleanVar(value=True)
        self.save_token_check = ttk.Checkbutton(row7, variable=self.save_token_var)
        self.save_token_check.pack(side=tk.LEFT)
        
        self.delete_token_button = ttk.Button(row7, command=self.delete_saved_token)
        self.delete_token_button.pack(side=tk.RIGHT, padx=5)
        
        # 操作按钮区域
        btn_frame = ttk.Frame(self.push_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.commit_push_button = ttk.Button(btn_frame, command=self.commit_and_push)
        self.commit_push_button.pack(side=tk.LEFT, padx=5)
        
        self.commit_only_button = ttk.Button(btn_frame, command=self.commit_only)
        self.commit_only_button.pack(side=tk.LEFT, padx=5)
        
        self.push_only_button = ttk.Button(btn_frame, command=self.push_only)
        self.push_only_button.pack(side=tk.LEFT, padx=5)
        
        self.check_status_button = ttk.Button(btn_frame, command=self.check_status)
        self.check_status_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_log_button = ttk.Button(btn_frame, command=self.clear_log)
        self.clear_log_button.pack(side=tk.RIGHT, padx=5)
        
        # 日志输出区域
        log_frame = ttk.LabelFrame(self.push_frame, text="日志输出", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置日志样式
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("warning", foreground="orange")
        self.log_text.tag_configure("info", foreground="blue")
        
        # 状态栏
        self.push_status_var = tk.StringVar(value="就绪")
        self.push_status = ttk.Label(self.push_frame, textvariable=self.push_status_var, 
                                     relief=tk.SUNKEN, padding=(8, 3))
        self.push_status.pack(fill=tk.X, padx=10, pady=5)
        
        # 刷新远程地址和文件列表
        self.refresh_remote_url()
        self.refresh_file_list()
    
    def create_toolbar(self):
        """创建底部工具栏"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        self.lang_switch_button = ttk.Button(toolbar, command=self.switch_language)
        self.lang_switch_button.pack(side=tk.LEFT, padx=5)
        
        self.about_button = ttk.Button(toolbar, command=self.show_about)
        self.about_button.pack(side=tk.RIGHT, padx=5)
    
    def update_texts(self):
        """更新所有文本"""
        t = translations[self.current_lang]
        
        # 窗口标题
        self.root.title(t['app_title'])
        
        # 标签页
        self.notebook.tab(0, text=t['tab_search'])
        self.notebook.tab(1, text=t['tab_push'])
        
        # 搜索页面
        self.search_keyword_label.config(text=t['keyword_label'])
        self.search_sort_label.config(text=t['sort_label'])
        self.search_lang_label.config(text=t['language_filter'])
        self.search_perpage_label.config(text=t['per_page_label'])
        self.search_button.config(text=t['search_button'])
        self.refresh_search_button.config(text=t['refresh_button'])
        self.clone_button.config(text=t['clone_button'])
        
        # 更新排序选项
        if self.current_lang == 'zh_CN':
            self.sort_combo['values'] = list(self.sort_options_zh.values())
        else:
            self.sort_combo['values'] = list(self.sort_options_en.values())
        
        # 表格表头
        self.search_tree.heading('rank', text=t['rank_col'])
        self.search_tree.heading('name', text=t['name_col'])
        self.search_tree.heading('stars', text=t['stars_col'])
        self.search_tree.heading('forks', text=t['forks_col'])
        self.search_tree.heading('language', text=t['language_col'])
        
        # 提交页面
        self.push_repo_label.config(text=t['repo_path_label'])
        self.push_remote_label.config(text=t['remote_url_label'])
        self.push_branch_label.config(text=t['branch_label'])
        self.push_msg_label.config(text=t['commit_msg_label'])
        self.force_push_check.config(text=t['force_push'])
        self.push_token_label.config(text=t['token_label'])
        self.push_username_label.config(text=t['username_label'])
        self.save_token_check.config(text=t['save_token'])
        
        self.browse_button.config(text=t['browse_button'])
        self.refresh_url_button.config(text=t['refresh_url_button'])
        self.get_token_button.config(text=t['get_token_button'])
        self.show_token_button.config(text=t['show_token_button'])
        self.delete_token_button.config(text=t['delete_token_button'])
        
        self.commit_push_button.config(text=t['commit_push_button'])
        self.commit_only_button.config(text=t['commit_only_button'])
        self.push_only_button.config(text=t['push_only_button'])
        self.check_status_button.config(text=t['check_status_button'])
        self.clear_log_button.config(text=t['clear_log_button'])
        
        # 工具栏
        self.lang_switch_button.config(text=t['language_switch'])
        self.about_button.config(text=t['about'])
        
        # 状态栏
        if not self.search_results:
            self.search_status_var.set(t['status_ready'])
    
    def switch_language(self):
        """切换语言"""
        self.current_lang = 'en_US' if self.current_lang == 'zh_CN' else 'zh_CN'
        self.update_texts()
    
    # ==================== 搜索功能 ====================
    
    def get_current_sort_key(self):
        """获取当前排序键"""
        current_text = self.sort_combo.get()
        options = self.sort_options_zh if self.current_lang == 'zh_CN' else self.sort_options_en
        for key, value in options.items():
            if value == current_text:
                return key
        return 'stars'
    
    def start_search(self):
        """开始搜索"""
        keyword = self.keyword_entry.get().strip()
        t = translations[self.current_lang]
        
        if not keyword:
            messagebox.showerror("Error", t['error_empty_keyword'])
            return
        
        sort_by = self.get_current_sort_key()
        per_page = self.perpage_var.get()
        lang_filter = self.search_lang_var.get()
        
        self.search_status_var.set(t['status_searching'])
        self.search_button.config(state=tk.DISABLED)
        
        # 清空表格
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        # 后台搜索
        threading.Thread(target=self.do_search, 
                        args=(keyword, sort_by, per_page, lang_filter),
                        daemon=True).start()
    
    def do_search(self, keyword, sort_by, per_page, lang_filter):
        """执行搜索"""
        try:
            query = keyword
            if lang_filter != 'All':
                query += f" language:{lang_filter.lower()}"
            
            api_url = f"https://api.github.com/search/repositories?q={query}&sort={sort_by}&order=desc&per_page={per_page}"
            response = requests.get(api_url, headers=headers, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            self.search_results = []
            for idx, item in enumerate(data.get("items", []), 1):
                repo = {
                    "rank": idx,
                    "name": item.get("full_name"),
                    "description": item.get("description"),
                    "stars": item.get("stargazers_count"),
                    "forks": item.get("forks_count"),
                    "language": item.get("language") or "-",
                    "url": item.get("html_url"),
                    "clone_url": item.get("clone_url")
                }
                self.search_results.append(repo)
            
            self.last_total_count = data.get("total_count", 0)
            
            # 更新 UI
            self.root.after(0, self.update_search_table)
            t = translations[self.current_lang]
            self.root.after(0, lambda: self.search_status_var.set(
                t['status_done'].format(self.last_total_count)))
            self.root.after(0, lambda: self.search_button.config(state=tk.NORMAL))
            
        except Exception as e:
            t = translations[self.current_lang]
            self.root.after(0, lambda: messagebox.showerror("Error", 
                t['error_search_failed'].format(str(e))))
            self.root.after(0, lambda: self.search_status_var.set(t['status_ready']))
            self.root.after(0, lambda: self.search_button.config(state=tk.NORMAL))
    
    def update_search_table(self):
        """更新搜索结果表格"""
        for repo in self.search_results:
            self.search_tree.insert('', tk.END, values=(
                repo['rank'],
                repo['name'],
                f"{repo['stars']:,}",
                f"{repo['forks']:,}",
                repo['language']
            ))
    
    def open_repo_link(self, event):
        """双击打开仓库链接"""
        selected = self.search_tree.selection()
        if selected:
            item = self.search_tree.item(selected[0])
            rank = item['values'][0] - 1
            if 0 <= rank < len(self.search_results):
                webbrowser.open(self.search_results[rank]['url'])
    
    def clone_selected(self):
        """克隆选中的项目"""
        selected = self.search_tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择一个项目")
            return
        
        item = self.search_tree.item(selected[0])
        rank = item['values'][0] - 1
        if 0 <= rank < len(self.search_results):
            clone_url = self.search_results[rank]['clone_url']
            
            # 选择保存目录
            save_dir = filedialog.askdirectory(title="选择保存目录")
            if save_dir:
                # 执行克隆
                self.notebook.select(1)  # 切换到提交页面显示日志
                self.log(f"🔄 正在克隆: {clone_url}", "info")
                threading.Thread(target=self._do_clone, 
                               args=(clone_url, save_dir),
                               daemon=True).start()
    
    def _do_clone(self, clone_url, save_dir):
        """执行克隆操作"""
        import subprocess
        try:
            result = subprocess.run(
                f'git clone {clone_url}',
                cwd=save_dir,
                capture_output=True,
                text=True,
                shell=True
            )
            if result.returncode == 0:
                self.root.after(0, lambda: self.log("✅ 克隆成功!", "success"))
            else:
                self.root.after(0, lambda: self.log(f"❌ 克隆失败: {result.stderr}", "error"))
        except Exception as e:
            self.root.after(0, lambda: self.log(f"❌ 克隆错误: {e}", "error"))
    
    # ==================== 提交功能 ====================
    
    def log(self, message, tag=None):
        """输出日志"""
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
    
    def browse_repo(self):
        """浏览选择仓库"""
        path = filedialog.askdirectory(initialdir=self.repo_path_var.get())
        if path:
            self.repo_path_var.set(path)
            self.refresh_remote_url()
            self.refresh_file_list()
    
    def refresh_file_list(self):
        """刷新文件列表"""
        import subprocess
        
        # 清空现有列表
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
        self.file_selections.clear()
        
        repo_path = self.repo_path_var.get()
        if not repo_path or not os.path.exists(repo_path):
            self.file_count_var.set("路径无效")
            return
        
        # 获取被 .gitignore 忽略的文件列表
        ignored_files = set()
        if check_git_repo(repo_path):
            try:
                result = subprocess.run(
                    'git status --ignored --porcelain',
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    shell=True
                )
                for line in result.stdout.split('\n'):
                    if line.startswith('!!'):
                        ignored_files.add(line[3:].strip().rstrip('/'))
            except:
                pass
        
        # 获取文件列表
        files = []
        ignored_count = 0
        try:
            for item in os.listdir(repo_path):
                item_path = os.path.join(repo_path, item)
                
                # 跳过 .git 目录
                if item == '.git':
                    continue
                
                # 检查是否被忽略
                is_ignored = item in ignored_files
                if is_ignored:
                    ignored_count += 1
                
                # 获取文件信息
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                    size_str = self._format_size(size)
                    file_type = os.path.splitext(item)[1] or "文件"
                    if is_ignored:
                        file_type = "🚫 " + file_type
                    files.append((item, file_type, size_str, not is_ignored, is_ignored))
                elif os.path.isdir(item_path):
                    # 计算目录中的文件数
                    try:
                        count = len(os.listdir(item_path))
                        size_str = f"{count} 项"
                    except:
                        size_str = "-"
                    file_type = "🚫 📁" if is_ignored else "📁 文件夹"
                    files.append((item, file_type, size_str, not is_ignored, is_ignored))
            
            # 排序：文件夹在前，文件在后，忽略的在最后
            files.sort(key=lambda x: (x[4], 0 if "📁" in x[1] else 1, x[0].lower()))
            
            # 添加到列表
            for name, file_type, size, selected, is_ignored in files:
                item_id = self.files_tree.insert('', tk.END, values=(
                    '☑' if selected else '☐',
                    name,
                    file_type,
                    size
                ))
                self.file_selections[item_id] = selected
            
            self.file_count_var.set(f"共 {len(files)} 个 (🚫{ignored_count} 个被忽略)")
            
        except Exception as e:
            self.file_count_var.set(f"读取失败: {e}")
    
    def _format_size(self, size):
        """格式化文件大小"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"
    
    def toggle_file_selection(self, event):
        """切换文件勾选状态"""
        region = self.files_tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.files_tree.identify_column(event.x)
            item = self.files_tree.identify_row(event.y)
            
            if item and column == '#1':  # 点击勾选列
                current = self.file_selections.get(item, False)
                new_state = not current
                self.file_selections[item] = new_state
                
                # 更新显示
                values = list(self.files_tree.item(item, 'values'))
                values[0] = '☑' if new_state else '☐'
                self.files_tree.item(item, values=values)
    
    def select_all_files(self):
        """全选所有文件"""
        for item in self.files_tree.get_children():
            self.file_selections[item] = True
            values = list(self.files_tree.item(item, 'values'))
            values[0] = '☑'
            self.files_tree.item(item, values=values)
    
    def deselect_all_files(self):
        """取消全选"""
        for item in self.files_tree.get_children():
            self.file_selections[item] = False
            values = list(self.files_tree.item(item, 'values'))
            values[0] = '☐'
            self.files_tree.item(item, values=values)
    
    def get_selected_files(self):
        """获取选中的文件列表"""
        selected = []
        for item, is_selected in self.file_selections.items():
            if is_selected:
                values = self.files_tree.item(item, 'values')
                selected.append(values[1])  # 文件名
        return selected
    
    def _commit_selected_files(self, repo_path, commit_msg, branch, force, token, username, selected_files, push=True):
        """
        提交勾选的文件
        
        规则：
        1. 只添加用户勾选的文件
        2. 仍然遵守 .gitignore（被忽略的文件不会被添加）
        3. 如果勾选的文件在 .gitignore 中，会被跳过
        """
        import subprocess
        from datetime import datetime
        
        try:
            # 显示勾选的文件
            self.root.after(0, lambda: self.log(f"📋 勾选了 {len(selected_files)} 个文件/文件夹", "info"))
            
            # 逐个添加勾选的文件
            added_count = 0
            ignored_count = 0
            
            for file_name in selected_files:
                file_path = os.path.join(repo_path, file_name)
                
                # 检查文件是否被 .gitignore 忽略
                check_result = subprocess.run(
                    f'git check-ignore -q "{file_name}"',
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    shell=True
                )
                
                if check_result.returncode == 0:
                    # 文件被 .gitignore 忽略
                    self.root.after(0, lambda f=file_name: self.log(f"   ⏭️ {f} (被 .gitignore 忽略)", "warning"))
                    ignored_count += 1
                    continue
                
                # 添加文件到暂存区
                add_result = subprocess.run(
                    f'git add "{file_name}"',
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    shell=True
                )
                
                if add_result.returncode == 0:
                    self.root.after(0, lambda f=file_name: self.log(f"   ✅ {f}", "success"))
                    added_count += 1
                else:
                    self.root.after(0, lambda f=file_name, e=add_result.stderr: 
                                   self.log(f"   ❌ {f}: {e}", "error"))
            
            self.root.after(0, lambda: self.log(f"📊 添加 {added_count} 个, 忽略 {ignored_count} 个", "info"))
            
            if added_count == 0:
                self.root.after(0, lambda: self.log("⚠️ 没有文件被添加到暂存区", "warning"))
                return False
            
            # 生成提交信息
            if not commit_msg:
                commit_msg = f"Auto commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # 提交
            commit_msg_escaped = commit_msg.replace('"', '\\"')
            commit_result = subprocess.run(
                f'git commit -m "{commit_msg_escaped}"',
                cwd=repo_path,
                capture_output=True,
                text=True,
                shell=True
            )
            
            if commit_result.returncode == 0:
                self.root.after(0, lambda: self.log(f"📝 提交成功: {commit_msg}", "success"))
            else:
                if "nothing to commit" in commit_result.stdout or "nothing to commit" in commit_result.stderr:
                    self.root.after(0, lambda: self.log("ℹ️ 没有需要提交的更改", "info"))
                else:
                    self.root.after(0, lambda: self.log(f"❌ 提交失败: {commit_result.stderr}", "error"))
                    return False
            
            # 如果需要推送
            if push:
                # 配置 Token
                if token:
                    configure_git_credential(repo_path, token, username)
                    self.root.after(0, lambda: self.log("🔐 Token 认证已配置", "info"))
                
                # 推送
                self.root.after(0, lambda: self.log(f"🚀 正在推送到 {branch} 分支...", "info"))
                push_result = subprocess.run(
                    f'git push -u origin {branch}' + (' --force' if force else ''),
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    shell=True
                )
                
                if push_result.returncode == 0:
                    self.root.after(0, lambda: self.log("✅ 推送成功!", "success"))
                else:
                    self.root.after(0, lambda: self.log(f"❌ 推送失败: {push_result.stderr}", "error"))
                    return False
                
                # 恢复远程 URL（移除 Token）
                if token:
                    restore_remote_url(repo_path)
                    self.root.after(0, lambda: self.log("🔒 已移除 URL 中的 Token", "info"))
            
            return True
            
        except Exception as e:
            self.root.after(0, lambda: self.log(f"❌ 错误: {e}", "error"))
            return False
    
    def refresh_remote_url(self):
        """刷新远程地址"""
        if not GIT_MODULE_AVAILABLE:
            return
        
        repo_path = self.repo_path_var.get()
        if repo_path and check_git_repo(repo_path):
            url = get_remote_url(repo_path)
            if url:
                self.remote_url_var.set(url)
                self.push_status_var.set(f"已加载仓库")
            else:
                self.remote_url_var.set("")
                self.push_status_var.set("未配置远程仓库")
        else:
            self.remote_url_var.set("")
            self.push_status_var.set("无效的 Git 仓库")
    
    def load_saved_token(self):
        """加载已保存的 Token"""
        if not GIT_MODULE_AVAILABLE:
            return
        
        token, username = load_token()
        if token:
            self.token_var.set(token)
            if username:
                self.username_var.set(username)
            self.log("✅ 已加载保存的 Token 配置", "success")
    
    def toggle_token_visibility(self):
        """切换 Token 可见性"""
        if self.token_entry.cget("show") == "*":
            self.token_entry.config(show="")
        else:
            self.token_entry.config(show="*")
    
    def get_token(self):
        """获取 Token"""
        result = messagebox.askyesnocancel(
            "获取 Token",
            "选择获取方式:\n\n"
            "是 - 打开浏览器手动获取\n"
            "否 - 使用自动化浏览器\n"
            "取消 - 取消"
        )
        
        if result is True:
            webbrowser.open("https://github.com/settings/tokens/new")
            self.log("🌐 已打开 GitHub Token 创建页面", "info")
        elif result is False and GIT_MODULE_AVAILABLE:
            self.log("🔄 正在启动自动化浏览器...", "info")
            threading.Thread(target=self._auto_get_token, daemon=True).start()
    
    def _auto_get_token(self):
        """自动获取 Token"""
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
        if not GIT_MODULE_AVAILABLE:
            return
        
        if messagebox.askyesno("确认", "确定删除已保存的 Token?"):
            if delete_token():
                self.token_var.set("")
                self.username_var.set("")
                self.log("✅ Token 已删除", "success")
    
    def check_status(self):
        """检查仓库状态"""
        if not GIT_MODULE_AVAILABLE:
            self.log("❌ Git 模块不可用", "error")
            return
        
        repo_path = self.repo_path_var.get()
        if not repo_path or not check_git_repo(repo_path):
            self.log("❌ 无效的 Git 仓库", "error")
            return
        
        self.log("=" * 50, "info")
        self.log("📁 仓库状态", "info")
        
        if check_remote_exists(repo_path):
            self.log(f"🔗 远程: {get_remote_url(repo_path)}", "success")
        else:
            self.log("⚠️ 未配置远程仓库", "warning")
        
        status = git_status(repo_path)
        if status:
            self.log("📝 待提交:", "info")
            for line in status.split('\n')[:10]:
                if line.strip():
                    self.log(f"   {line}", "info")
        else:
            self.log("✅ 工作区干净", "success")
    
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
        """执行 Git 操作"""
        if not GIT_MODULE_AVAILABLE:
            self.log("❌ Git 模块不可用", "error")
            return
        
        repo_path = self.repo_path_var.get()
        if not repo_path or not check_git_repo(repo_path):
            self.log("❌ 无效的 Git 仓库", "error")
            return
        
        # 获取勾选的文件列表
        selected_files = self.get_selected_files()
        if operation in ["commit_and_push", "commit_only"] and not selected_files:
            self.log("⚠️ 请至少勾选一个文件", "warning")
            return
        
        commit_msg = self.commit_msg_var.get() or None
        branch = self.branch_var.get() or "master"
        force = self.force_push_var.get()
        token = self.token_var.get() or None
        username = self.username_var.get() or None
        
        if token and self.save_token_var.get():
            save_token(token, username)
        
        self.push_status_var.set("执行中...")
        
        threading.Thread(
            target=self._execute_operation,
            args=(operation, repo_path, commit_msg, branch, force, token, username, selected_files),
            daemon=True
        ).start()
    
    def _execute_operation(self, operation, repo_path, commit_msg, branch, force, token, username, selected_files=None):
        """执行操作"""
        try:
            self.root.after(0, lambda: self.log("=" * 50, "info"))
            self.root.after(0, lambda: self.log(f"🚀 执行: {operation}", "info"))
            
            if operation == "commit_and_push":
                # 使用勾选的文件进行提交
                success = self._commit_selected_files(repo_path, commit_msg, branch, force, 
                                                      token, username, selected_files, push=True)
            elif operation == "commit_only":
                # 使用勾选的文件进行提交（不推送）
                success = self._commit_selected_files(repo_path, commit_msg, branch, force,
                                                      token, username, selected_files, push=False)
            elif operation == "push_only":
                if token:
                    configure_git_credential(repo_path, token, username)
                success, msg, _ = git_push(repo_path, branch, force)
                self.root.after(0, lambda: self.log(f"📤 {msg}", "info"))
                if token:
                    restore_remote_url(repo_path)
            
            if success:
                self.root.after(0, lambda: self.push_status_var.set("操作成功"))
                self.root.after(0, lambda: self.log("🎉 完成!", "success"))
            else:
                self.root.after(0, lambda: self.push_status_var.set("操作失败"))
                self.root.after(0, lambda: self.log("❌ 失败", "error"))
                
        except Exception as e:
            self.root.after(0, lambda: self.log(f"❌ 错误: {e}", "error"))
            self.root.after(0, lambda: self.push_status_var.set("发生错误"))
    
    def show_about(self):
        """显示关于信息"""
        messagebox.showinfo(
            "关于 GitHub Toolkit",
            "GitHub 工具箱 v1.0\n\n"
            "功能:\n"
            "• 搜索 GitHub 热门项目\n"
            "• 提交本地项目到 GitHub\n"
            "• 自动获取 Token\n\n"
            "© 2026"
        )


def main():
    """主函数"""
    root = tk.Tk()
    
    # 设置主题
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except:
        pass
    
    app = GitHubToolkitGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
