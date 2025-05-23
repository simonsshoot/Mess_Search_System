import os
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLineEdit, QLabel, QPushButton, QFrame,
                             QScrollArea, QTextBrowser,QCheckBox)
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QPixmap, QBrush
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread


import argparse
import yaml
from lucene import LuceneScorer,ImageScorer
from outputs import SearchResult,ImageResult

class SearchWorker(QThread):
    finished = pyqtSignal(list)
    
    def __init__(self, scorer, query):
        super().__init__()
        self.scorer = scorer
        self.query = query
        
    def run(self):
        try:
            results = self.scorer.compute_score(self.query)
            self.finished.emit(results)
        except Exception as e:
            print(f"Search error: {e}")
            self.finished.emit([])

class MainWindow(QMainWindow):
    def __init__(self, scorer,image_scorer,image_base_path):
        super().__init__()
        self.scorer = scorer
        self.image_scorer=image_scorer
        self.image_base_path=image_base_path
        self.current_scorer = self.scorer
        self.initUI()
        self.search_worker = None
        self.image_mode = False

    def initUI(self):
        self.setWindowTitle('Search System')
        self.setGeometry(300, 300, 1000, 800)
        
        self.set_background("pictures/background.jpg")
        
        #主容器
        main_widget = QWidget()
        main_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.setCentralWidget(main_widget)
        
        #主布局
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(60, 40, 60, 60)
        main_layout.setSpacing(30)
        
        self.setup_search_area(main_layout)
        
        #结果展示区域
        self.setup_results_area(main_layout)
        
    def set_background(self, image_path):
        palette = self.palette()
        background = QPixmap(image_path).scaled(
            self.size(), 
            Qt.KeepAspectRatioByExpanding, 
            Qt.SmoothTransformation
        )
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)

    def setup_search_area(self, parent_layout):
        search_container = QHBoxLayout()
        search_container.setSpacing(15)
        
        #搜索输入框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter your search query...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid rgba(204, 204, 204, 0.8);
                border-radius: 15px;
                padding: 12px 20px;
                font-size: 16px;
                background-color: rgba(255, 255, 255, 0.9);
            }
        """)
        #按回车也能发
        self.search_input.returnPressed.connect(self.start_search)
        
        #搜索按钮
        search_btn = QPushButton()
        search_btn.setIcon(QIcon("pictures/query.png"))
        search_btn.setIconSize(QSize(40, 40))
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(119, 187, 136, 0.9);
                border-radius: 20px;
                min-width: 50px;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: rgba(85, 160, 105, 0.9);
            }
        """)
        search_btn.clicked.connect(self.start_search)

        #加入图片复选框？
        option_row = QHBoxLayout()
        option_row.setContentsMargins(10, 0, 10, 0)
        self.image_search_check = QCheckBox("Image Mode")
        self.image_search_check.setStyleSheet("""
        QCheckBox {
            color: #2c3e50;
            font-size: 14px;
            background: transparent;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        QCheckBox::indicator:checked {
            background-color: #27ae60;
        }
        QCheckBox:hover {
            background: rgba(255, 255, 255, 0.2);
        }
    """)
        
        search_container.addWidget(self.search_input)
        search_container.addWidget(search_btn)
        option_row.addWidget(self.image_search_check)
        # option_row.addStretch()
        search_container.addLayout(option_row)
        parent_layout.addLayout(search_container)

        self.image_search_check.stateChanged.connect(self.change_search_mode)

    def change_search_mode(self,state):
        self.image_mode = state == Qt.Checked
        self.current_scorer = self.image_scorer if self.image_mode else self.scorer

    def setup_results_area(self, parent_layout):
        #滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        self.results_container = QWidget()
        self.results_container.setStyleSheet("background: rgba(255, 255, 255, 0.9);")
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setContentsMargins(20, 20, 20, 20)
        self.results_layout.setSpacing(25)
        
        placeholder = QLabel("Your search results will appear here...")
        placeholder.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 18px;
                font-style: italic;
            }
        """)
        placeholder.setAlignment(Qt.AlignCenter)
        self.results_layout.addWidget(placeholder)
        
        self.scroll_area.setWidget(self.results_container)
        parent_layout.addWidget(self.scroll_area)

    def start_search(self):
        query = self.search_input.text().strip()
        print(f"Searching for: {query}")
        if not query:
            return
        
        #清空之前的结果
        self.clear_results()
        
        #显示加载状态
        self.show_loading()
        
        #启动搜索线程
        self.search_worker = SearchWorker(self.current_scorer, query)
        self.search_worker.finished.connect(self.display_results)
        self.search_worker.start()

    def clear_results(self):
        #移除所有结果部件
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def show_loading(self):
        loading = QLabel("Searching...")
        loading.setStyleSheet("""
            QLabel {
                color: #444444;
                font-size: 16px;
            }
        """)
        loading.setAlignment(Qt.AlignCenter)
        self.results_layout.addWidget(loading)

    def display_results(self, results):
        self.clear_results()
        print(f"Found {len(results)} results.")
        print(results)
        query = self.search_input.text().strip()
        if not results:
            no_results = QLabel("No matching documents found.")
            no_results.setStyleSheet("color: #666666; font-size: 16px;")
            no_results.setAlignment(Qt.AlignCenter)
            self.results_layout.addWidget(no_results)
            return
        for rank, (doc_id, score) in enumerate(results, 1):
            if self.image_mode:
                meta = self.image_scorer.images_meta.get(doc_id, {})
                print(meta)
                print(doc_id)
                result = ImageResult(
                    image_id=doc_id,
                    score=score,
                    meta_data=meta,
                    using_stem=self.image_scorer.using_stem
                )
            else:
                meta = self.scorer.docs_meta.get(doc_id, {})
                result = SearchResult(
                    doc_id=doc_id,
                    score=score,
                    meta_data=meta,
                    using_stem=self.scorer.using_stem
                )
            result.set_query_terms(query)
            card = self.create_result_card(rank, result,query)
            self.results_layout.addWidget(card)

    def create_result_card(self, rank, result,query):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
                border: 1px solid #eeeeee;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        #标题行
        title_row = QHBoxLayout()
        if self.image_mode:
            content=QTextBrowser()
            html_text=result.get_title(query)
            content.setHtml(html_text)
            content.setStyleSheet("""
                QTextBrowser {
                    border: 1px solid #f0f0f0;
                    border-radius: 6px;
                    padding: 10px;
                    background: #f9f9f9;
                    font-size: 16px;
                    max-height: 100px;
                }
            """)
            title_row.addWidget(content)
        else:
            print(result)
            title_label = QLabel(f"{rank}. {result.get_title()}")
            title_label.setStyleSheet("""
                QLabel {
                    color: #2c3e50;
                    font-size: 18px;
                    font-weight: 500;
                    text-decoration: none;
                }
            """)
            title_row.addWidget(title_label)
        
        #评分标签
        score_label = QLabel(f"Score: {result.score:.4f}")
        score_label.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-size: 14px;
                padding: 4px 8px;
                border-radius: 4px;
                background: rgba(39, 174, 96, 0.1);
            }
        """)
        title_row.addWidget(score_label)
        layout.addLayout(title_row)
        
        #url和时间标签
        meta_row = QHBoxLayout()
        meta_row.addWidget(QLabel(f"Date: {result.get_time()}"))
        meta_row.addStretch()
        url_label = QLabel(f"<a href='{result.get_url()}'>{result.get_url()}</a>")
        url_label.setOpenExternalLinks(True)
        url_label.setStyleSheet("color: #2980b9;")
        meta_row.addWidget(url_label)
        layout.addLayout(meta_row)

        if self.image_mode:
            img_path=os.path.join(self.image_base_path,result.meta_data.get('relative_path',''))
            img_path = os.path.normpath(img_path)
            print(img_path)
            pixmap = QPixmap(img_path)
            if pixmap.isNull():
                print("图片不存在")
                not_path=os.path.join(self.image_base_path,'not.png')
                not_path = os.path.normpath(not_path)
                print(not_path)
                pixmap = QPixmap(not_path)
            image_label = QLabel()
            pixmap = pixmap.scaledToWidth(500, Qt.SmoothTransformation)
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setStyleSheet("margin-top: 10px;")
            layout.addWidget(image_label)
        
        else:
            content = QTextBrowser()
            html_text = result.get_article(query).replace("+++", "<br><br>")
            print(html_text)
            content.setHtml(html_text)
            content.setStyleSheet("""
                QTextBrowser {
                    border: 1px solid #f0f0f0;
                    border-radius: 6px;
                    padding: 10px;
                    background: #f9f9f9;
                    font-size: 16px;
                }
            """)
            content.setMaximumHeight(100)
            layout.addWidget(content)
        
        return card

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search Engine')
    parser.add_argument('--config', type=str, help='path to the config file', default='config.yaml')
    args = parser.parse_args()
    with open(args.config, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

    scorer = LuceneScorer(
        index_path=config['index_path'],
        idf_path=config['idf_path'],
        docs_path=config['docs_path'],
        using_stem=config['using_stem'],
        top_K=config['top_k']
    )

    image_scorer = ImageScorer(
        index_path=config['image_index'],
        idf_path=config['image_idf'],
        images_path=config['image_docs'],
        using_stem=config['image_stem'],
        top_K=config['image_topk']
    )
    
    #原神启动！
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial", 10))
    window = MainWindow(
        scorer=scorer,
        image_scorer=image_scorer,
        image_base_path=config['image_base']
    )
    window.show()
    sys.exit(app.exec_())