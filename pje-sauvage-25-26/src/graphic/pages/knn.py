from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QStackedWidget, QWidget, QVBoxLayout, QLabel, QAction, QCheckBox, QHBoxLayout, QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem, QHeaderView, QTextEdit, QSlider, QMessageBox, QDialog, QSpinBox
from PyQt5.QtCore import Qt, pyqtSignal
from tools.csv_tools import fetch_csv_files, check_if_all_cleaned, fetch_csv_filenames, iter_csv, fetch_csv_cleaned_filenames
from tools.gui_tools import get_screen_size, create_populate_db_tree
from tools.distance import knn, test_distance, print_matrix_graph, weighted_knn, matrix_to_text
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from graphic.popup.popus import display_db_popup


class KNN_RESULT_POPUP(QDialog): 
    def __init__(self,parent=None,knn_result=None):
        super().__init__(parent)

        (res,tweet,k,_) = knn_result
        self.setWindowTitle("KNN Algorithm Analysis")
        self.layout = QVBoxLayout()
        title_label = QLabel("Please find here all the informations") 

        tweet_label = QLabel(f"The tweet was : {tweet}")
        k_label = QLabel(f"You choosed {k} as the number of neighbours") 

        res = int(res)

        if res==0: 
            printable_res = "Neutral"
        elif res==2: 
            printable_res = "Negative"
        elif res==4 : 
            printable_res = "Positive"

        res_label = QLabel(f"The KNN algorithms returns {res}\nIt means the tweet has been classified as {printable_res}")


        self.layout.addWidget(title_label)
        self.layout.addWidget(tweet_label)
        self.layout.addWidget(k_label)
        self.layout.addWidget(res_label)
        self.setLayout(self.layout) 


class KNN_TEST_POPUP(QDialog):
    def __init__(self,parent=None,filename= None):
        super().__init__(parent)

        self.filename = filename

        self.setWindowTitle("KNN Algorithm Test")
        
        self.layout = QVBoxLayout()

        
        self.parameters_layout = QHBoxLayout()

        self.label_low = QLabel("Lower bound for k:")
        self.spin_low = QSpinBox()
        self.spin_low.setRange(0, 100)
        self.spin_low.setValue(5)

        self.label_high = QLabel("Higher bound for k:")
        self.spin_high = QSpinBox()
        self.spin_high.setRange(0, 100)
        self.spin_high.setValue(20)

        self.label_step = QLabel("Step :")
        self.spin_step = QSpinBox()
        self.spin_step.setRange(0,5)
        self.spin_step.setValue(2)

        self.graph_button = QPushButton("Show Graph")
        self.graph_button.clicked.connect(self.show_graph)

        self.parameters_layout.addWidget(self.label_low)
        self.parameters_layout.addWidget(self.spin_low)

        self.parameters_layout.addWidget(self.label_high)
        self.parameters_layout.addWidget(self.spin_high)

        self.parameters_layout.addWidget(self.label_step)
        self.parameters_layout.addWidget(self.spin_step)

        self.canvas = FigureCanvas(plt.figure())

        self.layout.addLayout(self.parameters_layout)
        self.layout.addWidget(self.canvas, stretch=1)

        self.matrices_layout = QHBoxLayout()
        self.matrix_pos_text = QTextEdit()
        self.matrix_neu_text = QTextEdit()
        self.matrix_neg_text = QTextEdit()

        for w in [self.matrix_pos_text, self.matrix_neu_text, self.matrix_neg_text]:
            w.setReadOnly(True)
            w.setMinimumWidth(200) 
            self.matrices_layout.addWidget(w)

        self.layout.addLayout(self.matrices_layout)

        self.layout.addWidget(self.graph_button)

        self.setLayout(self.layout)
        

    def show_graph(self):
        self.resize(1280,720)
        #best_* is a tuple (best_*_k,best_*_matrix)
        (correctness_pourcent, (best_pos,best_pos_matrix), (best_neu,best_neu_matrix), (best_neg,best_neg_matrix)) = test_distance(
        self.filename,
        self.spin_low.value(),
        self.spin_high.value(),
        self.spin_step.value()
        )
        print(best_neg)
        fig = print_matrix_graph(correctness_pourcent)

        self.canvas.figure = fig
        self.canvas.draw()

        def matrix_to_text(matrix):
            text = ""
            for real_class, predictions in matrix.items():
                if real_class == "0": real_class_str = "Negative"
                elif real_class == "2": real_class_str = "Neutral"
                elif real_class == "4": real_class_str = "Positive"
                total = sum(predictions.values())
                text += f"{real_class_str}:\n"
                for pred_class, count in predictions.items():
                    pourcent = (count / total) * 100
                    text += f"  {pred_class} = {count} ({pourcent:.2f}%)\n"
            return text

        self.matrix_pos_text.setPlainText(f"Best Positive k={best_pos}\n\n{matrix_to_text(best_pos_matrix)}")
        self.matrix_neu_text.setPlainText(f"Best Neutral k={best_neu}\n\n{matrix_to_text(best_neu_matrix)}")
        self.matrix_neg_text.setPlainText(f"Best Negative k={best_neg}\n\n{matrix_to_text(best_neg_matrix)}")

class KNN(QWidget): 


    def __init__(self,stack): 
        super().__init__() 

        self.stack = stack 
        self.layout = QHBoxLayout()

        (self.width,self.height) = get_screen_size()

        self.knn_db = None # GET VIA POPUP
        self.knn_algo = knn

        self.init_widget()

        self.setLayout(self.layout) 


    def init_widget(self): 

        def print_k_value(value):
            knn_number_text.setText(f"k (number of tweets in the base) : {value}") 

        def get_and_store_db(db):
            knn_selected_db.setText(f"Selected DB : {db}")
            self.knn_db = db 

        def launch_knn_algo():
            if self.knn_db == None: 
                QMessageBox.information(self, "DataBase Error", "Please select a DataBase via 'Choose KNN base'")
                return
            tweet = knn_tweet.toPlainText() 
            k_value = knn_number_slider.value()
            base = iter_csv(self.knn_db)
            base = [(int(grade), tweet) for grade, tweet in iter_csv(self.knn_db)]


            res = self.knn_algo(tweet,k_value,base)

            popup = KNN_RESULT_POPUP(self,(res, tweet, k_value, base))
            popup.exec_()

        def test_knn_algo():
            if self.knn_db == None: 
                QMessageBox.information(self, "DataBase Error", "Please select a DataBase via 'Choose KNN base'")
                return
            popup = KNN_TEST_POPUP(self,(self.knn_db))
            popup.exec_()
        
        def choose_knn_algo(): 
            if self.knn_algo == knn:
                self.knn_algo = weighted_knn
            else:
                self.knn_algo = knn
            self.knn_weighted_label.setText(
                "weighted" if self.knn_algo == weighted_knn else "non-weighted"
            )


            
    
        column_layout = QHBoxLayout() 

        # KNN ALGORITHM 

        knn_column = QVBoxLayout() 

        ######### Test KNN on 1 tweet 
        knn_one_tweet = QVBoxLayout() 

        knn_text = QLabel("KNN Algorithm for one tweet") 

        knn_parameters_layout = QHBoxLayout()

        knn_tweet = QTextEdit()
        knn_tweet.setPlaceholderText("Please enter the tweet you want to classify ...")


        knn_number_slider = QSlider(Qt.Horizontal) 
        knn_number_slider.setRange(0,30) 
        knn_number_slider.setValue(11) 
        knn_number_slider.valueChanged.connect(print_k_value)

        knn_number_text = QLabel("k (number of tweets in the base) : 11")

        knn_button = QPushButton("Choose KNN base")  

        knn_button.clicked.connect(lambda: display_db_popup(True,get_and_store_db,self))

        knn_parameters_layout.addWidget(knn_number_slider)
        knn_parameters_layout.addWidget(knn_number_text)
        knn_parameters_layout.addWidget(knn_button)

        knn_selected_db = QLabel("No database selected")

        knn_start_button = QPushButton("Launch KNN Algorithm")
        knn_start_button.clicked.connect(launch_knn_algo)

        knn_test_layout = QHBoxLayout()

        knn_test_buton = QPushButton("Test KNN Algorithm")
        knn_test_buton.clicked.connect(test_knn_algo)

        knn_weighted_button = QPushButton("Weighted ? Default - No") 
        knn_weighted_button.clicked.connect(choose_knn_algo)

        self.knn_weighted_label = QLabel(f"Non-Weighted") 

        knn_one_tweet.addWidget(knn_text)
        knn_one_tweet.addWidget(knn_tweet)

        knn_one_tweet.addLayout(knn_parameters_layout) 
        knn_one_tweet.addWidget(knn_selected_db)
        knn_one_tweet.addWidget(knn_start_button)


        knn_test_layout.addWidget(knn_test_buton)
        knn_test_layout.addWidget(knn_weighted_button) 
        knn_test_layout.addWidget(self.knn_weighted_label) 

        knn_column.addLayout(knn_one_tweet)
        self.layout.addLayout(knn_column)


            



