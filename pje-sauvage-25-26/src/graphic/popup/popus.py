from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QStackedWidget, QWidget, QVBoxLayout, QLabel, QAction, QCheckBox, QHBoxLayout, QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem, QHeaderView, QTextEdit, QSlider, QMessageBox, QDialog, QSpinBox, QRadioButton, QButtonGroup, QScrollArea
from PyQt5.QtCore import Qt, pyqtSignal
from tools.csv_tools import fetch_csv_files, check_if_all_cleaned, fetch_csv_filenames, iter_csv, fetch_csv_cleaned_filenames 
from tools.gui_tools import get_screen_size, create_populate_db_tree
from tools.distance import knn, test_distance, print_matrix_graph, print_confusion_matrix, get_correctness, test_database, get_matrix_pixmap, get_correctness_pourcent, get_graph_pixmap
from tools.baysienne_tools import compare_bayes_configs, get_bayes_confusion_matrix, print_bayes_graph
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import csv
import os
from pathlib import Path
import numpy as np

def display_db_popup(clean,callback,parent): 
    popup = DATABASE_POPUP(clean,parent)
    popup.db_signal.connect(callback)
    popup.exec_()


class DATABASE_POPUP(QDialog):

    """POPUP 
    used to open a popup to choose a database 
    takes 2 arguments : 
    parent : trivial 
    cleaned : If True fetchs cleaned filenames, else fetchs all
    """

    db_signal = pyqtSignal(str)

    def __init__(self,cleaned,parent): 
        super().__init__(parent) 

        def return_db(item): 
            selected_db = item.text(0) 
            self.db_signal.emit(selected_db)
            self.accept()

        self.setWindowTitle("Database list") 

        (self.width,self.height) = get_screen_size()

        self.layout = QVBoxLayout() 

        label = QLabel("Here's all the databases")
        self.layout.addWidget(label) 

        db_tree = create_populate_db_tree(fetch_csv_cleaned_filenames() if cleaned else fetch_csv_filenames(),self.width)
        db_tree.itemDoubleClicked.connect(return_db)

        self.layout.addWidget(db_tree)

        self.setLayout(self.layout)
        self.resize(800,800)

class CSV_POPUP(QDialog): 
    def __init__(self,parent, filename=None):
        super().__init__(parent)
        self.setWindowTitle("CSV Viewer") 
        self.resize(900,600) 

        layout = QVBoxLayout()
        self.setLayout(layout) 

        label= QLabel(f"Displaying CSV file : {filename}")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label) 

        self.table = QTableWidget()
        layout.addWidget(self.table) 

        close_button = QPushButton("Close") 
        close_button.clicked.connect(self.close) 
        layout.addWidget(close_button) 

        if filename: 
            self.load_csv(filename)

    def load_csv(self,filename): 
        """load csv file into QTableWidget

        Args:
            filename (_type_): _description_
        """
        csv_path = Path(__file__).resolve().parent.parent.parent.parent / "data" / filename
        absolute_csv_path = os.path.abspath(csv_path)

        try: 
            with open(absolute_csv_path,newline='',encoding='utf-8') as input_file: 
                readr = csv.reader(input_file) 
                rows = list(readr) 

                self.table.setRowCount(len(rows)) 
                self.table.setColumnCount(2)
                self.table.setHorizontalHeaderLabels(["Classification","Tweet"]) 

                for i,row in enumerate(rows[1:]): 
                    class_item = QTableWidgetItem(row[0]) 
                    class_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable) 
                    self.table.setItem(i,0,class_item) 

                    tweet_item = QTableWidgetItem(row[1]) 
                    tweet_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable) 
                    self.table.setItem(i,1,tweet_item) 

                self.table.resizeColumnsToContents()

        except Exception as e: 
            QMessageBox.critical(self, "Error",f"Unable to read CSV:\n{e}")



class KNN_ACCURACY_POPUP(QDialog):
    def __init__(self, parent, filename):
        super().__init__(parent)
        self.filename = filename
        self.setWindowTitle("Analyze K Impact & Matrices")
        self.resize(1100, 800) 
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        self.layout = QVBoxLayout(content_widget)

        config_layout = QHBoxLayout()
        
        config_layout.addWidget(QLabel("K Min:"))
        self.spin_min = QSpinBox()
        self.spin_min.setRange(1, 30)
        self.spin_min.setValue(1)
        config_layout.addWidget(self.spin_min)

        config_layout.addWidget(QLabel("K Max:"))
        self.spin_max = QSpinBox()
        self.spin_max.setRange(1, 30)
        self.spin_max.setValue(15)
        config_layout.addWidget(self.spin_max)

        self.btn_run = QPushButton("Generate Analysis")
        self.btn_run.clicked.connect(self.run_analysis)
        config_layout.addWidget(self.btn_run)
        
        self.layout.addLayout(config_layout)

        self.lbl_result = QLabel("")
        self.lbl_result.setAlignment(Qt.AlignCenter)
        self.lbl_result.setStyleSheet("font-size: 16px; margin: 10px;")
        self.layout.addWidget(self.lbl_result)


        self.lbl_graph = QLabel("Select a range and click 'Generate Analysis'")
        self.lbl_graph.setAlignment(Qt.AlignCenter)
        self.lbl_graph.setStyleSheet("border: 1px solid #ccc; background-color: white; margin-bottom: 20px;")
        self.lbl_graph.setMinimumHeight(350)
        self.layout.addWidget(self.lbl_graph)

        matrices_container = QHBoxLayout()
        

        def create_matrix_placeholder(title):
            vbox = QVBoxLayout()
            lbl_title = QLabel(title)
            lbl_title.setAlignment(Qt.AlignCenter)
            lbl_title.setStyleSheet("font-weight: bold;")
            
            lbl_img = QLabel()
            lbl_img.setAlignment(Qt.AlignCenter)
            lbl_img.setStyleSheet("border: 1px dashed #aaa; background-color: #f9f9f9;")
            lbl_img.setFixedSize(300, 250)
            lbl_img.setScaledContents(True)
            
            vbox.addWidget(lbl_title)
            vbox.addWidget(lbl_img)
            return vbox, lbl_title, lbl_img

        self.layout_neg, self.lbl_title_neg, self.lbl_img_neg = create_matrix_placeholder("Best for Negatives")
        self.layout_neu, self.lbl_title_neu, self.lbl_img_neu = create_matrix_placeholder("Best for Neutrals")
        self.layout_pos, self.lbl_title_pos, self.lbl_img_pos = create_matrix_placeholder("Best for Positives")

        matrices_container.addLayout(self.layout_neg)
        matrices_container.addLayout(self.layout_neu)
        matrices_container.addLayout(self.layout_pos)

        self.layout.addLayout(matrices_container)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def run_analysis(self):
        k_min = self.spin_min.value()
        k_max = self.spin_max.value()

        if k_min >= k_max:
            QMessageBox.warning(self, "Input Error", "K Min must be strictly lower than K Max.")
            return

        self.lbl_graph.setText("Calculating... Please wait.")
        self.lbl_result.setText("")
        self.lbl_graph.repaint()

        try:

            (list_of_correctness, 
             (best_pos_k, best_pos_matrix), 
             (best_neu_k, best_neu_matrix), 
             (best_neg_k, best_neg_matrix)) = test_distance(self.filename, k_min, k_max, step=1)


            best_k_global = -1
            best_avg_score = -1
            for (scores, k) in list_of_correctness:
                curr_avg = sum(scores) / 3
                if curr_avg > best_avg_score:
                    best_avg_score = curr_avg
                    best_k_global = k
            
            self.lbl_result.setText(f"Best Global K: {best_k_global} (Avg Accuracy: {best_avg_score:.2f}%)")


            pixmap_graph = get_graph_pixmap(list_of_correctness)
            self.lbl_graph.setPixmap(pixmap_graph)
            self.lbl_graph.setScaledContents(False)


            def update_matrix_view(lbl_title, lbl_img, category_name, k_val, matrix):

                lbl_title.setText(f"Best for {category_name} (k={k_val})")

                pixmap = get_matrix_pixmap(matrix)
                lbl_img.setPixmap(pixmap)


            update_matrix_view(self.lbl_title_neg, self.lbl_img_neg, "Negatives", best_neg_k, best_neg_matrix)
            

            update_matrix_view(self.lbl_title_neu, self.lbl_img_neu, "Neutrals", best_neu_k, best_neu_matrix)

            update_matrix_view(self.lbl_title_pos, self.lbl_img_pos, "Positives", best_pos_k, best_pos_matrix)

        except Exception as e:
            self.lbl_graph.setText(f"Error:\n{str(e)}")
            import traceback
            traceback.print_exc()



class CMP_BAY_ACCURACY_POPUP(QDialog):
    def __init__(self, parent, filename):
        super().__init__(parent)
        self.setWindowTitle("Naive Bayes Analysis Results")
        self.resize(900, 700)
        self.layout = QVBoxLayout()


        raw_data = []
        try:

            for row in iter_csv(filename):
                if len(row) >= 2:

                    raw_data.append((row[1], row[0])) 
            
            if not raw_data:
                raise ValueError("CSV file is empty or malformed.")

            results, names = compare_bayes_configs(raw_data)
            fig = print_bayes_graph(results, names)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not process Bayes analysis:\n{e}")
            self.close() 
            return

        best_avg = -1
        best_name = "None"
        for i, (p, neu, neg) in enumerate(results):
            avg = (p + neu + neg) / 3
            if avg > best_avg:
                best_avg = avg
                best_name = names[i]

        info_text = (f"<b>Analysis Report:</b><br>"
                     f"Tested configurations: {len(names)}<br>"
                     f"Best Model: <b>{best_name}</b><br>"
                     f"Average Accuracy: <b>{best_avg:.2f}%</b>")
        
        info_label = QLabel(info_text)
        info_label.setAlignment(Qt.AlignCenter)
        
        canvas = FigureCanvas(fig)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)

        self.layout.addWidget(info_label)
        self.layout.addWidget(canvas)
        self.layout.addWidget(close_btn)

        self.setLayout(self.layout)




class BAY_ONE_CONF_ACCURACY_POPUP(QDialog):
    """
    Displays the result of a SINGLE configuration.
    It takes the filename + params, calculates the matrix, and shows the Heatmap.
    """

    def __init__(self, parent, filename, ngram_mode, use_frequency):
        super().__init__(parent)
        

        mode_str = "Unigrams" if ngram_mode == 'uni' else "Bigrams" if ngram_mode == 'bi' else "Uni+Bi"
        freq_str = "Frequency" if use_frequency else "Presence"
        config_name = f"{mode_str} - {freq_str}"
        
        self.setWindowTitle(f"Result for: {config_name}")
        self.resize(600, 550)
        self.layout = QVBoxLayout()


        try:

            raw_data = []
            for row in iter_csv(filename):
                if len(row) >= 2:
                    raw_data.append((row[1], row[0]))
            
            if not raw_data: raise ValueError("Empty CSV")

            import random
            random.shuffle(raw_data)
            split = int(len(raw_data) * 0.8)
            train_data = raw_data[:split]
            test_data = raw_data[split:]

            matrix = get_bayes_confusion_matrix(train_data, test_data, ngram_mode, use_frequency)
            

            pos, neu, neg = get_correctness(matrix)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Calculation failed:\n{e}")
            self.close()
            return
        text = (f"<h2>Configuration: {config_name}</h2>"
                f"<b>Accuracy:</b><br>"
                f"Positives: {pos*100:.1f}%<br>"
                f"Neutrals: {neu*100:.1f}%<br>"
                f"Negatives: {neg*100:.1f}%")
        
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        fig = self.create_heatmap(matrix)
        canvas = FigureCanvas(fig)
        
        btn = QPushButton("Close")
        btn.clicked.connect(self.close)
        
        self.layout.addWidget(label)
        self.layout.addWidget(canvas)
        self.layout.addWidget(btn)
        self.setLayout(self.layout)

    def create_heatmap(self, matrix):
        row_0 = [matrix["0"]["true"], matrix["0"]["but_neu"], matrix["0"]["but_p"]]
        row_2 = [matrix["2"]["but_neg"], matrix["2"]["true"], matrix["2"]["but_p"]]
        row_4 = [matrix["4"]["but_neg"], matrix["4"]["but_neu"], matrix["4"]["true"]]
        data = np.array([row_0, row_2, row_4])

        fig, ax = plt.subplots(figsize=(5, 4))
        cax = ax.imshow(data, cmap='Blues')
        fig.colorbar(cax)
        
        labels = ['Neg (0)', 'Neu (2)', 'Pos (4)']
        ax.set_xticks(range(3))
        ax.set_yticks(range(3))
        ax.set_xticklabels(labels)
        ax.set_yticklabels(labels)
        ax.set_title("Confusion Matrix")

        for i in range(3):
            for j in range(3):
                val = data[i, j]
                color = "white" if val > data.max()/2 else "black"
                ax.text(j, i, str(val), ha='center', va='center', color=color)
        
        fig.tight_layout()
        return fig


