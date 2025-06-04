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
        """设置背景图片 - 修复版本"""
        try:
            # 加载背景图片
            bg_image_path = "background.jpg"
            if os.path.exists(bg_image_path):
                # 打开并调整图片大小以适应窗口
                pil_image = Image.open(bg_image_path)
                pil_image = pil_image.resize((900, 800), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(pil_image)
                
                # 方案1: 直接设置root的背景（推荐）
                # 创建背景Canvas
                self.bg_canvas = tk.Canvas(self.root, width=900, height=800, highlightthickness=0)
                self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
                self.bg_canvas.create_image(450, 400, image=self.bg_photo)
                
                print("背景图片加载成功")
            else:
                print(f"背景图片文件不存在: {bg_image_path}")
                # 设置纯色背景作为备选
                self.root.configure(bg='lightblue')
        except Exception as e:
            print(f"加载背景图片出错: {e}")
            # 设置纯色背景作为备选
            self.root.configure(bg='lightgray')
        
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
        """创建界面组件 - 修复版本"""
        # 配置样式，使ttk组件具有透明效果
        style = ttk.Style()
        
        # 尝试设置透明样式（某些系统可能不支持）
        try:
            style.theme_use('clam')  # 使用支持自定义的主题
            style.configure('Transparent.TFrame', background='', relief='flat')
            style.configure('Transparent.TLabelFrame', background='', relief='flat')
        except:
            pass
        
        # 主框架 - 使用透明背景
        main_frame = tk.Frame(self.root, bg='', bd=0, highlightthickness=0)
        main_frame.place(x=10, y=10, relwidth=1, relheight=1, width=-20, height=-20)
        
        # 配置网格权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 模式切换区域 - 添加半透明背景
        mode_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=1)
        mode_frame.grid(row=0, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10), padx=5, ipady=5)
        
        # Image Mode 按钮
        self.image_mode_btn = tk.Checkbutton(mode_frame, text="Image Mode", 
                                           variable=self.image_mode,
                                           command=self.on_mode_change,
                                           bg='white', font=('Arial', 10))
        self.image_mode_btn.pack(side='left', padx=10)
        
        # 查询控制区域 - 添加半透明背景
        query_frame = tk.LabelFrame(main_frame, text="查询控制", bg='white', 
                                   relief='raised', bd=2, font=('Arial', 10, 'bold'))
        query_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10), padx=5)
        query_frame.columnconfigure(1, weight=1)
        query_frame.columnconfigure(3, weight=1)
        
        # 第一个选项表 - 信息点类型
        tk.Label(query_frame, text="信息点类型:", bg='white', font=('Arial', 9)).grid(
            row=0, column=0, sticky=tk.W, padx=(10, 5), pady=10)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(query_frame, textvariable=self.category_var, 
                                          values=self.get_categories(), state="readonly", width=20)
        self.category_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20), pady=10)
        self.category_combo.bind('<<ComboboxSelected>>', self.on_category_change)
        
        # 第二个选项表 - 具体信息点
        tk.Label(query_frame, text="具体信息点:", bg='white', font=('Arial', 9)).grid(
            row=0, column=2, sticky=tk.W, padx=(0, 5), pady=10)
        self.item_var = tk.StringVar()
        self.item_combo = ttk.Combobox(query_frame, textvariable=self.item_var, 
                                      state="disabled", width=30)
        self.item_combo.grid(row=0, column=3, sticky=tk.W, padx=(0, 20), pady=10)
        
        # 查询按钮
        self.query_btn = tk.Button(query_frame, text="查询", command=self.perform_query,
                                  bg='lightblue', font=('Arial', 9, 'bold'), 
                                  relief='raised', bd=2, cursor='hand2')
        self.query_btn.grid(row=0, column=4, sticky=tk.W, padx=(0, 10), pady=10)
        
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
        # 结果框架 - 添加背景色
        results_frame = tk.LabelFrame(parent, text="查询结果", bg='white', 
                                     relief='raised', bd=2, font=('Arial', 10, 'bold'))
        results_frame.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, 
                          pady=(10, 0), padx=(5, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # 创建滚动区域
        canvas = tk.Canvas(results_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='white')
        
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
        stats_label = tk.Label(self.scrollable_frame, 
                              text=f"查询结果: {category} - {item} (共{len(article_ids)}个{mode_text})",
                              font=('Arial', 12, 'bold'), bg='white', fg='blue')
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
        # 文章框架 - 添加背景色
        article_frame = tk.LabelFrame(parent, text=f"文章 {index + 1} (ID: {article['id']})", 
                                     bg="#ffffff", relief='raised', bd=2,
                                     font=('Arial', 10, 'bold'))
        
        # 完全填充父容器，不设置左右边距
        article_frame.pack(fill=tk.X, pady=15, padx=0)
        
        # Title部分
        title_label = tk.Label(article_frame, text="Title:", font=('Arial', 10, 'bold'), 
                              bg="#9cc7a7")
        title_label.pack(anchor='w', padx=10, pady=(5, 0))
        
        title_text = tk.Text(article_frame, height=2, wrap=tk.WORD, font=('Arial', 9))
        title_content = article.get('title', '')
        title_text.insert('1.0', title_content)
        title_text.config(state='disabled')
        title_text.pack(fill=tk.X, pady=(0, 5), padx=10)
        
        # 高亮标题中的关键词
        self.highlight_text_in_widget(title_text, title_content, self.current_keyword)
        
        # Article部分
        article_label = tk.Label(article_frame, text="Article:", font=('Arial', 10, 'bold'),
                                bg="#b1f1b5")
        article_label.pack(anchor='w', padx=10)
        
        article_text = scrolledtext.ScrolledText(article_frame, height=6, wrap=tk.WORD, 
                                               font=('Arial', 9))
        article_content = article.get('article', '')
        article_text.insert('1.0', article_content)
        article_text.config(state='disabled')
        article_text.pack(fill=tk.X, pady=(0, 5), padx=10)
        
        # 高亮文章内容中的关键词
        self.highlight_text_in_widget(article_text, article_content, self.current_keyword)
        
        # Good/Bad部分
        rating_frame = tk.Frame(article_frame, bg="#f0f0f088")
        rating_frame.pack(fill=tk.X, pady=(5, 10), padx=10)
        
        # 显示当前Good/Bad数值
        good_count = article.get('Good', 0)
        bad_count = article.get('Bad', 0)
        
        good_label = tk.Label(rating_frame, text=f"Good: {good_count}", 
                             font=('Arial', 10, 'bold'), foreground='green', bg='#f0f0f0')
        good_label.pack(side='left', padx=(0, 20))
        
        bad_label = tk.Label(rating_frame, text=f"Bad: {bad_count}", 
                            font=('Arial', 10, 'bold'), foreground='red', bg='#f0f0f0')
        bad_label.pack(side='left', padx=(0, 20))
        
        # 按钮
        good_btn = tk.Button(rating_frame, text="👍 赞", 
                            command=lambda: self.update_article_rating(article['id'], 'Good', good_label),
                            bg='lightgreen', relief='raised', bd=2, cursor='hand2')
        good_btn.pack(side='left', padx=(0, 10))
        
        bad_btn = tk.Button(rating_frame, text="👎 踩", 
                           command=lambda: self.update_article_rating(article['id'], 'Bad', bad_label),
                           bg='lightcoral', relief='raised', bd=2, cursor='hand2')
        bad_btn.pack(side='left')
    
    def create_image_widget(self, parent, image_item, index):
        """创建单个图片显示组件"""
        # 图片框架 - 添加背景色
        image_frame = tk.LabelFrame(parent, text=f"图片 {index + 1} (ID: {image_item['id']})", 
                                   bg='#f0f0f0', relief='raised', bd=2,
                                   font=('Arial', 10, 'bold'))
        
        # 完全填充父容器
        image_frame.pack(fill=tk.X, pady=15, padx=0)
        
        # Title部分
        title_label = tk.Label(image_frame, text="Title:", font=('Arial', 10, 'bold'),
                              bg='#f0f0f0')
        title_label.pack(anchor='w', padx=10, pady=(5, 0))
        
        title_text = tk.Text(image_frame, height=2, wrap=tk.WORD, font=('Arial', 9))
        title_content = image_item.get('title', '')
        title_text.insert('1.0', title_content)
        title_text.config(state='disabled')
        title_text.pack(fill=tk.X, pady=(0, 5), padx=10)
        
        # 高亮标题中的关键词
        self.highlight_text_in_widget(title_text, title_content, self.current_keyword)
        
        # Image部分
        image_label = tk.Label(image_frame, text="Image:", font=('Arial', 10, 'bold'),
                              bg='#f0f0f0')
        image_label.pack(anchor='w', padx=10)
        
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
                img_label = tk.Label(image_frame, image=photo, bg='#f0f0f0')
                img_label.image = photo  # 保持引用，防止被垃圾回收
                img_label.pack(pady=(0, 5), padx=10)
            else:
                # 如果图片不存在，显示错误信息
                error_label = tk.Label(image_frame, text=f"图片文件不存在: {image_path}", 
                                      foreground='red', bg='#f0f0f0')
                error_label.pack(pady=(0, 5), padx=10)
        except Exception as e:
            # 如果加载图片出错，显示错误信息
            error_label = tk.Label(image_frame, text=f"加载图片出错: {str(e)}", 
                                  foreground='red', bg='#f0f0f0')
            error_label.pack(pady=(0, 5), padx=10)
        
        # Good/Bad部分
        rating_frame = tk.Frame(image_frame, bg='#f0f0f0')
        rating_frame.pack(fill=tk.X, pady=(5, 10), padx=10)
        
        # 显示当前Good/Bad数值
        good_count = image_item.get('Good', 0)
        bad_count = image_item.get('Bad', 0)
        
        good_label = tk.Label(rating_frame, text=f"Good: {good_count}", 
                             font=('Arial', 10, 'bold'), foreground='green', bg='#f0f0f0')
        good_label.pack(side='left', padx=(0, 20))
        
        bad_label = tk.Label(rating_frame, text=f"Bad: {bad_count}", 
                            font=('Arial', 10, 'bold'), foreground='red', bg='#f0f0f0')
        bad_label.pack(side='left', padx=(0, 20))
        
        # 按钮
        good_btn = tk.Button(rating_frame, text="👍 赞", 
                            command=lambda: self.update_image_rating(image_item['id'], 'Good', good_label),
                            bg='lightgreen', relief='raised', bd=2, cursor='hand2')
        good_btn.pack(side='left', padx=(0, 10))
        
        bad_btn = tk.Button(rating_frame, text="👎 踩", 
                           command=lambda: self.update_image_rating(image_item['id'], 'Bad', bad_label),
                           bg='lightcoral', relief='raised', bd=2, cursor='hand2')
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