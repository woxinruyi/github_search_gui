import requests
import json
import tkinter as tk
from tkinter import ttk, messagebox
import threading
# 多语言支持
translations = {
    'zh_CN': {
        'title': 'GitHub 项目热度搜索器',
        'keyword_label': '搜索关键词:',
        'sort_label': '排序方式:',
        'language_filter': '编程语言:',
        'per_page_label': '显示数量:',
        'search_button': '搜索',
        'refresh_button': '刷新',
        'language_switch': '切换语言 / Switch Language',
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
        'all_languages': '全部'
    },
    'en_US': {
        'title': 'GitHub Trending Search',
        'keyword_label': 'Keyword:',
        'sort_label': 'Sort By:',
        'language_filter': 'Programming Language:',
        'per_page_label': 'Results Count:',
        'search_button': 'Search',
        'refresh_button': 'Refresh',
        'language_switch': '切换语言 / Switch Language',
        'rank_col': 'Rank',
        'name_col': 'Repository',
        'stars_col': 'Stars',
        'forks_col': 'Forks',
        'language_col': 'Language',
        'status_ready': 'Ready',
        'status_searching': 'Searching...',
        'status_done': 'Search completed, {} repositories found',
        'error_empty_keyword': 'Please enter a keyword',
        'error_search_failed': 'Search failed: {}',
        'all_languages': 'All'
    }
}
# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://github.com/'
}
class GitHubSearchGUI:
    def __init__(self, root):
        self.root = root
        self.current_lang = 'zh_CN'
        self.sort_options = {'stars': 'Star 数量 (Stars)', 'forks': 'Fork 数量 (Forks)', 'updated': '最近更新 (Updated)'}
        self.language_options = ['All', 'Python', 'JavaScript', 'Java', 'C++', 'TypeScript', 'Go', 'Rust', 'PHP']
        self.results = []
        self.last_total_count = 0
        self.setup_ui()
        self.update_texts()
    def setup_ui(self):
        # 顶部控制区域 - 使用独立frame换行，避免挤压
        self.control_frame = ttk.Frame(self.root, padding="10")
        self.control_frame.pack(fill=tk.X)
        
        # 第一行：关键词
        self.row1 = ttk.Frame(self.control_frame)
        self.row1.pack(fill=tk.X, pady=(0, 8))
        
        self.keyword_label_var = tk.StringVar()
        self.keyword_label = ttk.Label(self.row1, textvariable=self.keyword_label_var, width=12)
        self.keyword_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.keyword_entry = ttk.Entry(self.row1, width=60)
        self.keyword_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.keyword_entry.insert(0, "python")
        
        # 第二行：排序、语言、数量
        self.row2 = ttk.Frame(self.control_frame)
        self.row2.pack(fill=tk.X, pady=(0, 8))
        
        self.sort_label_var = tk.StringVar()
        self.sort_label = ttk.Label(self.row2, textvariable=self.sort_label_var, width=12)
        self.sort_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # 获取排序选项文本
        if self.current_lang == 'zh_CN':
            sort_values = list(self.sort_options.values())
        else:
            sorted_en = {'stars': 'Stars Count', 'forks': 'Forks Count', 'updated': 'Last Updated'}
            sort_values = list(sorted_en.values())
            
        self.sort_var = tk.StringVar(value=sort_values[0])
        self.sort_combo = ttk.Combobox(self.row2, textvariable=self.sort_var, 
                                       values=sort_values, state='readonly', width=18)
        self.sort_combo.pack(side=tk.LEFT, padx=5)
        
        self.lang_label_var = tk.StringVar()
        self.lang_label = ttk.Label(self.row2, textvariable=self.lang_label_var, width=12)
        self.lang_label.pack(side=tk.LEFT, padx=(10, 5))
        
        self.lang_var = tk.StringVar(value='All')
        self.lang_combo = ttk.Combobox(self.row2, textvariable=self.lang_var, 
                                       values=self.language_options, state='readonly', width=12)
        self.lang_combo.pack(side=tk.LEFT, padx=5)
        
        self.perpage_label_var = tk.StringVar()
        self.perpage_label = ttk.Label(self.row2, textvariable=self.perpage_label_var, width=10)
        self.perpage_label.pack(side=tk.LEFT, padx=(10, 5))
        
        self.perpage_var = tk.IntVar(value=30)
        self.perpage_spin = ttk.Spinbox(self.row2, from_=10, to=100, textvariable=self.perpage_var, width=6)
        self.perpage_spin.pack(side=tk.LEFT, padx=5)
        
        # 第三行：按钮 - 单独一行显示，保证不会被挤压
        self.row3 = ttk.Frame(self.control_frame)
        self.row3.pack(fill=tk.X, pady=(5, 0))
        
        self.search_button_var = tk.StringVar()
        self.search_button = ttk.Button(self.row3, textvariable=self.search_button_var, command=self.start_search)
        self.search_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.refresh_button_var = tk.StringVar()
        self.refresh_button = ttk.Button(self.row3, textvariable=self.refresh_button_var, command=self.refresh_search)
        self.refresh_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # 填充空白空间
        spacer = ttk.Frame(self.row3)
        spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.lang_switch_button_var = tk.StringVar()
        self.lang_switch_button = ttk.Button(self.row3, textvariable=self.lang_switch_button_var, command=self.switch_language)
        self.lang_switch_button.pack(side=tk.RIGHT, padx=(0, 0))
        
        # 表格区域 - 独立区域填充剩余空间
        self.table_frame = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        self.table_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建表格
        columns = ('rank', 'name', 'stars', 'forks', 'language')
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show='headings')
        
        # 初始化表头
        t_initial = translations[self.current_lang]
        self.tree.heading('rank', text=t_initial['rank_col'])
        self.tree.heading('name', text=t_initial['name_col'])
        self.tree.heading('stars', text=t_initial['stars_col'])
        self.tree.heading('forks', text=t_initial['forks_col'])
        self.tree.heading('language', text=t_initial['language_col'])
        
        self.tree.column('rank', width=60, anchor=tk.CENTER)
        self.tree.column('name', width=320)
        self.tree.column('stars', width=100, anchor=tk.E)
        self.tree.column('forks', width=100, anchor=tk.E)
        self.tree.column('language', width=120)
        
        # 滚动条
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.statusbar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, padding=(8, 3))
        self.statusbar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 双击打开链接功能
        self.tree.bind('<Double-1>', self.open_link)
    def update_texts(self):
        t = translations[self.current_lang]
        self.root.title(t['title'])
        self.keyword_label_var.set(t['keyword_label'])
        self.sort_label_var.set(t['sort_label'])
        self.lang_label_var.set(t['language_filter'])
        self.perpage_label_var.set(t['per_page_label'])
        self.search_button_var.set(t['search_button'])
        self.refresh_button_var.set(t['refresh_button'])
        self.lang_switch_button_var.set(t['language_switch'])
        
        # 更新表头文本
        self.tree.heading('rank', text=t['rank_col'])
        self.tree.heading('name', text=t['name_col'])
        self.tree.heading('stars', text=t['stars_col'])
        self.tree.heading('forks', text=t['forks_col'])
        self.tree.heading('language', text=t['language_col'])
        
        if not self.results:
            self.status_var.set(t['status_ready'])
        # 更新排序下拉框选项
        if self.current_lang == 'zh_CN':
            self.sort_combo['values'] = list(self.sort_options.values())
        else:
            sorted_en = {'stars': 'Stars Count', 'forks': 'Forks Count', 'updated': 'Last Updated'}
            self.sort_combo['values'] = list(sorted_en.values())
    def switch_language(self):
        if self.current_lang == 'zh_CN':
            self.current_lang = 'en_US'
        else:
            self.current_lang = 'zh_CN'
        self.update_texts()
        if self.results:
            t = translations[self.current_lang]
            self.status_var.set(t['status_done'].format(self.last_total_count))
    def get_current_sort_key(self):
        # 获取当前选择的排序键
        current_text = self.sort_combo.get()
        if self.current_lang == 'zh_CN':
            sorted_values = list(self.sort_options.values())
            if current_text in sorted_values:
                idx = sorted_values.index(current_text)
                return list(self.sort_options.keys())[idx]
        else:
            sorted_en = {'stars': 'Stars Count', 'forks': 'Forks Count', 'updated': 'Last Updated'}
            sorted_values = list(sorted_en.values())
            if current_text in sorted_values:
                idx = sorted_values.index(current_text)
                return list(sorted_en.keys())[idx]
        return 'stars'  # 默认返回stars排序
    def search_github_repos(self, keyword, sort_by, order, per_page, lang_filter):
        query = keyword
        if lang_filter != 'All':
            query += f" language:{lang_filter.lower()}"
        
        api_url = f"https://api.github.com/search/repositories?q={query}&sort={sort_by}&order={order}&per_page={per_page}"
        
        response = requests.get(api_url, headers=headers, timeout=60)
        response.raise_for_status()
        return response.json()
    def start_search(self):
        keyword = self.keyword_entry.get().strip()
        t = translations[self.current_lang]
        if not keyword:
            messagebox.showerror("Error", t['error_empty_keyword'])
            return
        
        sort_by = self.get_current_sort_key()
        per_page = self.perpage_var.get()
        lang_filter = self.lang_var.get()
        
        self.status_var.set(t['status_searching'])
        self.search_button.config(state=tk.DISABLED)
        self.refresh_button.config(state=tk.DISABLED)
        
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 在后台线程搜索
        thread = threading.Thread(target=self.do_search, args=(keyword, sort_by, per_page, lang_filter))
        thread.daemon = True
        thread.start()
    def do_search(self, keyword, sort_by, per_page, lang_filter):
        try:
            data = self.search_github_repos(keyword, sort_by, "desc", per_page, lang_filter)
            self.results = []
            for idx, item in enumerate(data.get("items", []), 1):
                repo = {
                    "rank": idx,
                    "name": item.get("full_name"),
                    "description": item.get("description"),
                    "stars": item.get("stargazers_count"),
                    "forks": item.get("forks_count"),
                    "language": item.get("language") or "-",
                    "url": item.get("html_url")
                }
                self.results.append(repo)
            
            # 更新UI必须在主线程
            self.root.after(0, self.update_table)
            t = translations[self.current_lang]
            total_count = data.get("total_count", 0)
            self.last_total_count = total_count
            self.root.after(0, lambda: self.status_var.set(t['status_done'].format(total_count)))
            self.root.after(0, lambda: self.search_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.refresh_button.config(state=tk.NORMAL))
            
            # 保存结果到文件
            output_file = "github_search_results.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            error_msg = str(e)
            t = translations[self.current_lang]
            self.root.after(0, lambda: messagebox.showerror("Error", t['error_search_failed'].format(error_msg)))
            self.root.after(0, lambda: self.status_var.set(translations[self.current_lang]['status_ready']))
            self.root.after(0, lambda: self.search_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.refresh_button.config(state=tk.NORMAL))
    def update_table(self):
        for repo in self.results:
            self.tree.insert('', tk.END, values=(
                repo['rank'],
                repo['name'],
                f"{repo['stars']:,}",
                f"{repo['forks']:,}",
                repo['language']
            ))
    def refresh_search(self):
        # 刷新就是重新搜索一次，获取最新数据
        self.start_search()
    def open_link(self, event):
        import webbrowser
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item[0])
            rank = item['values'][0] - 1
            if 0 <= rank < len(self.results):
                url = self.results[rank]['url']
                webbrowser.open(url)
def main():
    root = tk.Tk()
    root.geometry("850x620")
    root.minsize(700, 450)
    app = GitHubSearchGUI(root)
    root.mainloop()
if __name__ == "__main__":
    main()