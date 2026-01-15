from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QStackedWidget, QWidget, QVBoxLayout, QLabel, QAction, QCheckBox, QHBoxLayout, QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem, QHeaderView, QTextEdit, QSlider, QMessageBox, QDialog, QSpinBox
from PyQt5.QtCore import Qt, pyqtSignal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from tools.gui_tools import get_screen_size 
from graphic.popup.popus import display_db_popup
from tools.clusters import average_complete, ward

class CLUSTER_RESULT_POPUP(QDialog):
    def __init__(self,parent,*args): 
        super().__init__(parent) 
        
        self.setWindowTitle("Cluster Analysis") 
        self.layout = QVBoxLayout() 

        titre_label = QLabel("Please find here all the cluster analysis informations") 
        
        nb_param = len(args)

        if nb_param == 4: 

            (avg,comp,_,_) = args

            self.canvas_avg = FigureCanvas(avg) 
            self.canvas_comp = FigureCanvas(comp)

            self.canvas_avg.draw()
            self.canvas_comp.draw() 

            self.layout.addWidget(self.canvas_avg) 
            self.layout.addWidget(self.canvas_comp) 
        elif nb_param == 2:
            (ward,_) = args
            self.canvas = FigureCanvas(ward) 
            self.canvas.draw()
            self.layout.addWidget(self.canvas) 
        else: 
            QMessageBox.warning(self, "Parameters Error", "This Popup only accepts 2 or 4 arguments") 


        self.setLayout(self.layout)


class HandleClusters(QWidget): 
    def __init__(self,stack): 
        super().__init__() 

        self.stack = stack 
        self.layout = QHBoxLayout()

        (self.width,self.height) = get_screen_size()
        self.cluster_db = None 
        self.method = None

        self.init_widget()

        self.setLayout(self.layout)     

    def init_widget(self): 
        #already defined in knn.py but dk yet how the arch will be 
        def get_and_store_db(db):
            cluster_selected_db.setText(f"Selected DB : {db}")
            self.cluster_db = db 
        def invert_method(): 
            self.method = "ward" if self.method == "avg_complete" else "avg_complete"
            avg_or_ward_label.setText("Ward" if self.method=="ward" else "Average & Complete")

        def set_and_store(cluster): 
            self.cluster_db = cluster
            cluster_selected_db.setText(f"{self.cluster_db}") 

        def launch_clusters():
            if self.cluster_db == None: 
                QMessageBox.information(self, "DataBase Error", "Please select a DataBase via 'Choose KNN base'")
                return
            cluster_figure = average_complete(self.cluster_db) if self.method == "avg_complete" else ward(self.cluster_db)
            popup = CLUSTER_RESULT_POPUP(self,*cluster_figure)
            popup.exec_()
                

        column_layout = QVBoxLayout() 

        cluster_label = QLabel("Handle Clusters")

        cluster_db_layout = QHBoxLayout()

        cluster_file_button = QPushButton("Choose file to cluster")  
        cluster_file_button.clicked.connect(lambda: display_db_popup(True,set_and_store,self))

        cluster_selected_db = QLabel("No database selected")


        select_avg_or_ward_label = QLabel("Please select which method") 

        choose_method_layout = QHBoxLayout()

        avg_or_ward_button=QPushButton("Average & Complete or Ward ?")
        avg_or_ward_button.clicked.connect(invert_method)

        avg_or_ward_label = QLabel("None") 

        choose_method_layout.addWidget(avg_or_ward_button)
        choose_method_layout.addWidget(avg_or_ward_label)
    

        launch_clusters_button = QPushButton("Launch Clusters") 
        launch_clusters_button.clicked.connect(launch_clusters)

        cluster_db_layout.addWidget(cluster_file_button)
        cluster_db_layout.addWidget(cluster_selected_db)

        cluster_db_layout.addLayout(choose_method_layout)
        
        cluster_db_layout.addWidget(launch_clusters_button)
    
        column_layout.addLayout(cluster_db_layout)

        self.layout.addLayout(column_layout)
