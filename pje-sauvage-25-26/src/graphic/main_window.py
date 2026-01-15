import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QStackedWidget, QWidget, QVBoxLayout, QLabel, QAction, QCheckBox, QHBoxLayout, QWidgetAction

from graphic.pages.dashboard import DashBoard
from graphic.pages.knn import KNN
from graphic.pages.handle_databases import HandleDatabases
from graphic.pages.handle_clusters import HandleClusters

from tools.gui_tools import get_screen_size

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        
        self.stack = QStackedWidget() 
        self.setCentralWidget(self.stack) 

        self.dashboard_page = DashBoard(self.stack)
        self.handle_page = HandleDatabases(self.stack)
        self.knn_page = KNN(self.stack)
        self.clusters_page = HandleClusters(self.stack)


        self.stack.addWidget(self.dashboard_page) #add at index 0
        self.stack.addWidget(self.handle_page)
        self.stack.addWidget(self.knn_page)
        self.stack.addWidget(self.clusters_page)


        (self.width, self.height) = get_screen_size()

        self.create_menu()  


        #put last
        self.stack.setCurrentIndex(0)



    def see_tweets_event(self): 
        print("redirecting to list") 

    def create_menu(self): 
        """_summary_
        """
        #cant find a way to get the menu right (except with spaces)
        number_of_tab_for_illusion = int((self.width * 0.75) / 4) 
        menu = self.menuBar()
        pages_menu = menu.addMenu(f"Reveal pages{"\t" * number_of_tab_for_illusion}                               Press Esc to Exit") 

        dashboard_action = QAction("DashBoard",self) 
        dashboard_action.triggered.connect(lambda: self.stack.setCurrentIndex(0))

        handle_action = QAction("Handle Databases", self) 
        handle_action.triggered.connect(lambda: self.stack.setCurrentIndex(1))

        knn_action = QAction("KNN Algorithm", self) 
        knn_action.triggered.connect(lambda: self.stack.setCurrentIndex(2)) 

        clusters_action = QAction("Clusters", self)
        clusters_action.triggered.connect(lambda: self.stack.setCurrentIndex(3))



        pages_menu.addAction(dashboard_action) 
        pages_menu.addAction(handle_action)
        pages_menu.addAction(knn_action)
        pages_menu.addAction(clusters_action)



        # tell user how to quit (in pages_menu (sliding? menu))
        quit_action = QWidgetAction(self)

        container = QWidget()
        layout = QHBoxLayout(container) 
        layout.setContentsMargins(0,0,10,0) 

        exit_label = QLabel("Press Esc to Exit")

        layout.addWidget(exit_label) 

        quit_action.setDefaultWidget(container) 

        pages_menu.addAction(quit_action) 





