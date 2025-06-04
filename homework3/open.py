import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from collections import defaultdict
from PIL import Image, ImageTk
import re


class InfoExtractionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("信息抽取系统查询界面")
        self.root.geometry("900x800")
        
        # 设置背景图片
        self.set_background()

        self.set_styles()
        
        # 数据存储
        self.statistics_data = []
        self.articles_data = {}
        self.image_statistics_data = []
        self.image_data = {}
        self.current_results = []
        
        # 模式标志
        self.image_mode = tk.BooleanVar()
        
        # 当前查询的关键词
        self.current_keyword = ""
        
        # 加载数据
        self.load_data()
        
        # 创建界面
        self.create_widgets()
        
    def set_background(self):
        """设置背景图片"""
        try:
            # 加载背景图片
            bg_image_path = "background.jpg"
            if os.path.exists(bg_image_path):
                # 打开并调整图片大小以适应窗口
                pil_image = Image.open(bg_image_path)
                pil_image = pil_image.resize((900, 800), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(pil_image)
                
                # 创建背景标签
                bg_label = tk.Label(self.root, image=self.bg_photo)
                bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            else:
                print(f"背景图片文件不存在: {bg_image_path}")
        except Exception as e:
            print(f"加载背景图片出错: {e}")

    def set_styles(self):
        """设置清新风格的样式"""
        style = ttk.Style()
        
        # 配置主框架样式
        style.configure('TFrame', background="#f0fff0")
        
        # 配置标签框架样式
        style.configure('TLabelframe', background="#f0fff0", bordercolor="#000000", 
                        relief="solid", borderwidth=2)
        
        style.configure('TLabelframe.Label', background="#f0fff0",foreground="#000000")
        
        # 配置标签样式
        style.configure('TLabel', background="#f0fff0", foreground="#000000")
        style.configure('Title.TLabel', font=('微软雅黑', 14, 'bold'), 
                        background="#eeff00", foreground="#020003")
        
        # 配置按钮样式
        style.configure('TButton', background="#f0fff0", foreground="#000000", 
                        font=('微软雅黑', 10), borderwidth=1, relief="solid")
        style.map('TButton', 
                  background=[('active', '#f0fff0'), ('pressed', "#006400")],
                  foreground=[('active', '#000000'), ('pressed', "#000000")])
        
        # 配置复选框样式
        style.configure('TCheckbutton', background="#f0fff0", foreground="#000000")
        
        # 配置组合框样式
        style.configure('TCombobox', fieldbackground="#ffffff", background="#000000", 
                        foreground="#000000", selectbackground="#000000")
        
        # 配置滚动文本区域样式
        style.configure('TScrolledtext', background="#ffffff", foreground="#000000")
        
        # 配置文本区域样式
        style.configure('TText', background="#edffc6", foreground="#000000")
        
       
    def load_data(self):
        """加载统计报告和文章数据"""
        try:
            # 加载文章统计报告
            with open('keyword/statistics_report.jsonl', 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.statistics_data.append(json.loads(line.strip()))
            
            # 加载文章数据
            with open('keyword/keyword_output.jsonl', 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        article = json.loads(line.strip())
                        self.articles_data[article['id']] = article
            
            # 加载图片统计报告
            with open('image_large/title_statistics_report.jsonl', 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.image_statistics_data.append(json.loads(line.strip()))
            
            # 加载图片数据
            with open('image_large/title_keyword.jsonl', 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        image_item = json.loads(line.strip())
                        self.image_data[image_item['id']] = image_item
                        
        except FileNotFoundError as e:
            messagebox.showerror("错误", f"文件未找到: {e}")
        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"JSON解析错误: {e}")
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架 - 修改边距设置，添加背景色和透明度
        main_frame = ttk.Frame(self.root, padding="10 10 5 0")
        main_frame.grid(row=0, column=0, sticky=tk.NSEW)
        
        # 设置样式，使界面元素有轻微透明背景
        style = ttk.Style()
        style.configure('Transparent.TLabelFrame', background='white', alpha=0.9)
        
        # 配置网格权重 - 确保结果区域可以扩展
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)  # 结果区域所在行
        
        # 模式切换区域
        mode_frame = ttk.Frame(main_frame)
        mode_frame.grid(row=0, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        
        # Image Mode 按钮
        self.image_mode_btn = ttk.Checkbutton(mode_frame, text="Image Mode", 
                                             variable=self.image_mode,
                                             command=self.on_mode_change)
        self.image_mode_btn.pack(side='left')
        
        # 查询控制区域
        query_frame = ttk.LabelFrame(main_frame, text="查询控制", padding="10")
        query_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        
        # 第一个选项表 - 信息点类型
        ttk.Label(query_frame, text="信息点类型:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(query_frame, textvariable=self.category_var, 
                                          values=self.get_categories(), state="readonly", width=20)
        self.category_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        self.category_combo.bind('<<ComboboxSelected>>', self.on_category_change)
        
        # 第二个选项表 - 具体信息点
        ttk.Label(query_frame, text="具体信息点:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.item_var = tk.StringVar()
        self.item_combo = ttk.Combobox(query_frame, textvariable=self.item_var, 
                                      state="disabled", width=30)
        self.item_combo.grid(row=0, column=3, sticky=tk.W, padx=(0, 20))
        
        # 查询按钮
        self.query_btn = ttk.Button(query_frame, text="查询", command=self.perform_query)
        self.query_btn.grid(row=0, column=4, sticky=tk.W)
        
        # 结果显示区域
        self.create_results_area(main_frame)
        
    def on_mode_change(self):
        """当模式改变时重新加载选项"""
        # 清空当前选择
        self.category_var.set('')
        self.item_var.set('')
        
        # 更新类别选项
        self.category_combo['values'] = self.get_categories()
        self.item_combo['values'] = []
        self.item_combo['state'] = 'disabled'
        
        # 清空结果显示
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
    def get_categories(self):
        """获取所有信息点类型"""
        categories = set()
        data_source = self.image_statistics_data if self.image_mode.get() else self.statistics_data
        for item in data_source:
            categories.add(item['信息点类名'])
        return sorted(list(categories))
    
    def get_items_for_category(self, category):
        """根据类型获取具体信息点，按具体数目排序"""
        items = []
        data_source = self.image_statistics_data if self.image_mode.get() else self.statistics_data
        for item in data_source:
            if item['信息点类名'] == category:
                # 获取具体数目，如果不存在则默认为0
                count = item.get('具体数目', 0)
                items.append((item['信息点具体名称'], count))
        
        # 按具体数目降序排序
        items.sort(key=lambda x: x[1], reverse=True)
        
        # 只返回名称列表
        return [item[0] for item in items]
    
    def on_category_change(self, event=None):
        """当信息点类型改变时更新具体信息点列表"""
        category = self.category_var.get()
        if category:
            items = self.get_items_for_category(category)
            self.item_combo['values'] = items
            self.item_combo['state'] = 'readonly'
            self.item_var.set('')  # 清空当前选择
        else:
            self.item_combo['values'] = []
            self.item_combo['state'] = 'disabled'
            self.item_var.set('')
    
    def create_results_area(self, parent):
        """创建结果显示区域"""
        # 结果框架 - 修改右边距为5像素
        results_frame = ttk.LabelFrame(parent, text="查询结果", padding="10")
        results_frame.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, pady=(10, 0), padx=(0, 5))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # 创建滚动区域
        canvas = tk.Canvas(results_frame, bg='white')
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        # 绑定滚动区域大小变化事件
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            
        def configure_canvas_width(event):
            # 设置scrollable_frame的宽度等于canvas的宽度
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        self.scrollable_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_canvas_width)
        
        # 创建canvas窗口并保存引用
        canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas_window = canvas_window
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 使用 grid 布局并设置权重，确保 Canvas 填满整个结果框架
        canvas.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        
        # 配置网格权重 - 确保 Canvas 可以扩展
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # 绑定鼠标滚轮
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        self.canvas = canvas
    
    def highlight_text_in_widget(self, text_widget, text, keyword):
        """在文本组件中高亮显示关键词"""
        if not keyword:
            return
            
        # 配置高亮标签
        text_widget.tag_configure("highlight", background="yellow", foreground="red")
        
        # 清除之前的高亮
        text_widget.tag_remove("highlight", "1.0", tk.END)
        
        # 查找并高亮所有关键词出现位置（不区分大小写）
        start_pos = "1.0"
        while True:
            # 使用不区分大小写的搜索
            pos = text_widget.search(keyword, start_pos, tk.END, nocase=True)
            if not pos:
                break
            
            # 计算结束位置
            end_pos = f"{pos}+{len(keyword)}c"
            
            # 添加高亮标签
            text_widget.tag_add("highlight", pos, end_pos)
            
            # 更新搜索起始位置
            start_pos = end_pos
    
    def perform_query(self):
        """执行查询"""
        category = self.category_var.get()
        item = self.item_var.get()
        
        if not category or not item:
            messagebox.showwarning("警告", "请选择信息点类型和具体信息点")
            return
        
        # 保存当前查询的关键词用于高亮
        self.current_keyword = item
        
        # 根据模式选择数据源
        data_source = self.image_statistics_data if self.image_mode.get() else self.statistics_data
        
        # 查找对应的统计数据
        target_stat = None
        for stat in data_source:
            if stat['信息点类名'] == category and stat['信息点具体名称'] == item:
                target_stat = stat
                break
        
        if not target_stat:
            messagebox.showinfo("信息", "未找到匹配的数据")
            return
        
        # 获取文章ID列表
        article_ids = target_stat.get('包含文章ID列表', [])
        
        # 清空之前的结果
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # 显示查询结果统计
        mode_text = "图片" if self.image_mode.get() else "文章"
        stats_label = ttk.Label(self.scrollable_frame, 
                               text=f"查询结果: {category} - {item} (共{len(article_ids)}个{mode_text})",
                               font=('Arial', 12, 'bold'))
        stats_label.pack(pady=(0, 10), anchor='w')
        
        # 根据模式显示不同内容
        if self.image_mode.get():
            # 显示图片模式
            for i, item_id in enumerate(article_ids):
                if item_id in self.image_data:
                    self.create_image_widget(self.scrollable_frame, self.image_data[item_id], i)
        else:
            # 显示文章模式
            for i, article_id in enumerate(article_ids):
                if article_id in self.articles_data:
                    self.create_article_widget(self.scrollable_frame, self.articles_data[article_id], i)
        
        # 更新滚动区域
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def create_article_widget(self, parent, article, index):
        """创建单个文章显示组件"""
        # 文章框架 - 移除左右边距，让它完全填充父容器
        article_frame = ttk.LabelFrame(parent, text=f"文章 {index + 1} (ID: {article['id']})", 
                                      padding="10")
        article_frame.columnconfigure(0, weight=1)
        
        # 完全填充父容器，不设置左右边距
        article_frame.pack(fill=tk.X, pady=15, padx=0)
        
        # Title部分
        title_label = ttk.Label(article_frame, text="Title:", font=('Arial', 10, 'bold'))
        title_label.pack(anchor='w')
        
        title_text = tk.Text(article_frame, height=2, wrap=tk.WORD, font=('Arial', 9))
        title_content = article.get('title', '')
        title_text.insert('1.0', title_content)
        title_text.config(state='disabled')
        title_text.pack(fill=tk.X, pady=(0, 5))
        
        # 高亮标题中的关键词
        self.highlight_text_in_widget(title_text, title_content, self.current_keyword)
        
        # Article部分
        article_label = ttk.Label(article_frame, text="Article:", font=('Arial', 10, 'bold'))
        article_label.pack(anchor='w')
        
        article_text = scrolledtext.ScrolledText(article_frame, height=6, wrap=tk.WORD, 
                                               font=('Arial', 9))
        article_content = article.get('article', '')
        article_text.insert('1.0', article_content)
        article_text.config(state='disabled')
        article_text.pack(fill=tk.X, pady=(0, 5))
        
        # 高亮文章内容中的关键词
        self.highlight_text_in_widget(article_text, article_content, self.current_keyword)
        
        # Good/Bad部分
        rating_frame = ttk.Frame(article_frame)
        rating_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 显示当前Good/Bad数值
        good_count = article.get('Good', 0)
        bad_count = article.get('Bad', 0)
        
        good_label = ttk.Label(rating_frame, text=f"Good: {good_count}", 
                              font=('Arial', 10, 'bold'), foreground='green')
        good_label.pack(side='left', padx=(0, 20))
        
        bad_label = ttk.Label(rating_frame, text=f"Bad: {bad_count}", 
                             font=('Arial', 10, 'bold'), foreground='red')
        bad_label.pack(side='left', padx=(0, 20))
        
        # 按钮
        good_btn = ttk.Button(rating_frame, text="👍 赞", 
                             command=lambda: self.update_article_rating(article['id'], 'Good', good_label))
        good_btn.pack(side='left', padx=(0, 10))
        
        bad_btn = ttk.Button(rating_frame, text="👎 踩", 
                            command=lambda: self.update_article_rating(article['id'], 'Bad', bad_label))
        bad_btn.pack(side='left')
    
    def create_image_widget(self, parent, image_item, index):
        """创建单个图片显示组件"""
        # 图片框架
        image_frame = ttk.LabelFrame(parent, text=f"图片 {index + 1} (ID: {image_item['id']})", 
                                    padding="10")
        image_frame.columnconfigure(0, weight=1)
        
        # 完全填充父容器
        image_frame.pack(fill=tk.X, pady=15, padx=0)
        
        # Title部分
        title_label = ttk.Label(image_frame, text="Title:", font=('Arial', 10, 'bold'))
        title_label.pack(anchor='w')
        
        title_text = tk.Text(image_frame, height=2, wrap=tk.WORD, font=('Arial', 9))
        title_content = image_item.get('title', '')
        title_text.insert('1.0', title_content)
        title_text.config(state='disabled')
        title_text.pack(fill=tk.X, pady=(0, 5))
        
        # 高亮标题中的关键词
        self.highlight_text_in_widget(title_text, title_content, self.current_keyword)
        
        # Image部分
        image_label = ttk.Label(image_frame, text="Image:", font=('Arial', 10, 'bold'))
        image_label.pack(anchor='w')
        
        # 加载并显示图片
        try:
            image_path = os.path.join("image_large", image_item.get('relative_path', ''))
            if os.path.exists(image_path):
                # 加载图片
                pil_image = Image.open(image_path)
                
                # 调整图片大小，保持比例
                max_width = 600
                max_height = 400
                pil_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # 转换为tkinter可用的格式
                photo = ImageTk.PhotoImage(pil_image)
                
                # 创建标签显示图片
                img_label = ttk.Label(image_frame, image=photo)
                img_label.image = photo  # 保持引用，防止被垃圾回收
                img_label.pack(pady=(0, 5))
            else:
                # 如果图片不存在，显示错误信息
                error_label = ttk.Label(image_frame, text=f"图片文件不存在: {image_path}", 
                                       foreground='red')
                error_label.pack(pady=(0, 5))
        except Exception as e:
            # 如果加载图片出错，显示错误信息
            error_label = ttk.Label(image_frame, text=f"加载图片出错: {str(e)}", 
                                   foreground='red')
            error_label.pack(pady=(0, 5))
        
        # Good/Bad部分
        rating_frame = ttk.Frame(image_frame)
        rating_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 显示当前Good/Bad数值
        good_count = image_item.get('Good', 0)
        bad_count = image_item.get('Bad', 0)
        
        good_label = ttk.Label(rating_frame, text=f"Good: {good_count}", 
                              font=('Arial', 10, 'bold'), foreground='green')
        good_label.pack(side='left', padx=(0, 20))
        
        bad_label = ttk.Label(rating_frame, text=f"Bad: {bad_count}", 
                             font=('Arial', 10, 'bold'), foreground='red')
        bad_label.pack(side='left', padx=(0, 20))
        
        # 按钮
        good_btn = ttk.Button(rating_frame, text="👍 赞", 
                             command=lambda: self.update_image_rating(image_item['id'], 'Good', good_label))
        good_btn.pack(side='left', padx=(0, 10))
        
        bad_btn = ttk.Button(rating_frame, text="👎 踩", 
                            command=lambda: self.update_image_rating(image_item['id'], 'Bad', bad_label))
        bad_btn.pack(side='left')
    
    def update_article_rating(self, article_id, rating_type, label_widget):
        """更新文章评分"""
        try:
            # 更新内存中的数据
            if article_id in self.articles_data:
                self.articles_data[article_id][rating_type] += 1
                
                # 更新标签显示
                new_count = self.articles_data[article_id][rating_type]
                label_widget.config(text=f"{rating_type}: {new_count}")
                
                # 保存到文件
                self.save_articles_data()
                
        except Exception as e:
            messagebox.showerror("错误", f"更新评分时出错: {e}")
    
    def update_image_rating(self, image_id, rating_type, label_widget):
        """更新图片评分"""
        try:
            # 更新内存中的数据
            if image_id in self.image_data:
                self.image_data[image_id][rating_type] += 1
                
                # 更新标签显示
                new_count = self.image_data[image_id][rating_type]
                label_widget.config(text=f"{rating_type}: {new_count}")
                
                # 保存到文件
                self.save_image_data()
                
        except Exception as e:
            messagebox.showerror("错误", f"更新评分时出错: {e}")
    
    def save_articles_data(self):
        """保存文章数据到文件"""
        try:
            with open('keyword/keyword_output.jsonl', 'w', encoding='utf-8') as f:
                for article in self.articles_data.values():
                    f.write(json.dumps(article, ensure_ascii=False) + '\n')
        except Exception as e:
            messagebox.showerror("错误", f"保存文章文件时出错: {e}")
    
    def save_image_data(self):
        """保存图片数据到文件"""
        try:
            with open('image_large/title_keyword.jsonl', 'w', encoding='utf-8') as f:
                for image_item in self.image_data.values():
                    f.write(json.dumps(image_item, ensure_ascii=False) + '\n')
        except Exception as e:
            messagebox.showerror("错误", f"保存图片文件时出错: {e}")


def main():
    """主函数"""
    # 检查必要的文件是否存在
    required_files = [
        'keyword/statistics_report.jsonl', 
        'keyword/keyword_output.jsonl',
        'image_large/title_statistics_report.jsonl',
        'image_large/title_keyword.jsonl'
    ]
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"错误: 以下文件不存在: {', '.join(missing_files)}")
        print("请确保所有必要的数据文件都存在")
        return
    
    # 创建GUI
    root = tk.Tk()
    app = InfoExtractionGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()