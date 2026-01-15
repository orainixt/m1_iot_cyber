from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QStackedWidget, QWidget, QVBoxLayout, QLabel, QAction, QCheckBox, QHBoxLayout, QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem, QHeaderView, QTextEdit, QSlider, QMessageBox, QDialog, QSpinBox, QListWidget, QLineEdit, QComboBox, QRadioButton, QButtonGroup 
from PyQt5.QtCore import Qt, pyqtSignal
from tools.csv_tools import fetch_csv_files, check_if_all_cleaned, fetch_csv_filenames, iter_csv, fetch_csv_cleaned_filenames, clean_csv, get_algo_accuracy, get_algo_matrix
from tools.gui_tools import get_screen_size, create_populate_db_tree
from tools.distance import knn, test_distance, print_matrix_graph, test_database, get_correctness_pourcent, get_matrix_pixmap, auto_grade_database_to_csv_knn
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from tools.baysienne_tools import auto_grade_database_to_csv_baysienne
from graphic.popup.popus import DATABASE_POPUP, CSV_POPUP, KNN_ACCURACY_POPUP, CMP_BAY_ACCURACY_POPUP, BAY_ONE_CONF_ACCURACY_POPUP


class HandleDatabases(QWidget):

    def __init__(self,stack): 
        super().__init__() 

        self.stack = stack 
        self.layout = QHBoxLayout()

        (self.width,self.height) = get_screen_size()

        self.cleaned_db = None
        self.graded_db = None
        self.to_delete_db = None

        self.selected_delimiter = ','
        self.function_to_grade = knn
        self.algo_base = None

        self.k = 11 
        
        self.mode = 'uni' 
        self.count_mode = False 

        self.init_widget()

        self.setLayout(self.layout) 

    def init_widget(self): 

        def get_and_store_db(db,target):
            if target == "cleaned":
                self.cleaned_db = db
                self.clean_selected_db.setText(f"Connected DB : {db}")
            if target == "graded":
                self.graded_db = db
                self.grade_selected_db_label.setText(f"Connected DB : {db}")
            if target == "to_delete": 
                self.to_delete_db = db 
                self.delete_choose_db_label.setText(f"Connected DB : {db}") 
            if target == "algo_base": 
                self.algo_base = db
                self.grade_algo_base_label.setText(f"Connected DB : {db}") 

        def display_popup(target,cleaned): 
            popup = DATABASE_POPUP(cleaned,self)
            popup.db_signal.connect(lambda db: get_and_store_db(db,target))
            popup.exec_()



        def display_algo_accuracy_popup():
            """
            Refactored: Just instantiates the popups.
            Logic is moved inside the popups.
            """
            # Ensure a database is selected
            if not hasattr(self, 'graded_db') or not self.graded_db:
                 QMessageBox.warning(self, "Warning", "Please select a database first.")
                 return

            # --- KNN ---
            if self.knn_radio_button.isChecked():
                # We pass the filename, k, and the grading function
                popup = KNN_ACCURACY_POPUP(self, self.graded_db)
                popup.exec_()

            # --- NAIVE BAYES ---
            if self.naive_baysienne_radio_button.isChecked():
                # We just pass the filename
                popup = CMP_BAY_ACCURACY_POPUP(self, self.graded_db)
                popup.exec_()

            if self.baysienne_radio_button.isChecked(): 
                popup = BAY_ONE_CONF_ACCURACY_POPUP(self, self.graded_db, self.mode, self.count_mode)
                popup.exec_()
            


        def display_db_popup(db): 
            popup = CSV_POPUP(self,db) 
            popup.exec_()

        def add_delimiter():
            delimiter = self.input_delimiter_text.text().strip() 
            if delimiter: 
                self.delimiter_list.addItem(delimiter)
                self.input_delimiter_text.clear()

        def populate_delimiters(): 
            self.delimiter_list.addItem(',')
            self.delimiter_list.addItem(';')
            self.delimiter_list.addItem(':')

        def get_and_store_delimiter(item): 
            text = item.text() 
            self.selected_delimiter = text 
            self.selected_delimiter_label.setText(f"Delimiter selected : '{self.selected_delimiter}'")

        def function_changed(text): 
            if text == "KNN Algorithm": 
                self.function_to_grade = knn

        def set_k(k): 
            self.k = k 


        def display_mode(texte):
            self.label_resultat.setText(f"Selected : {texte}")
            if texte == 'Uni':
                self.mode='uni' 
            if texte=='Bi':
                self.mode='bi'
            if texte=='Bi+Uni': 
                self.mode = 'uni+bi'

        def set_count_mode(is_freq):
            if is_freq : 
                self.count_mode = True 
                self.label_etat.setText("Selected : Frequence") 
            else: 
                self.count_mode = False 
                self.label_etat.setText("Selected : Presence") 


        def grade_selected_db(): 
            if self.knn_radio_button.isChecked():
                auto_grade_database_to_csv_knn(self.graded_db, self.algo_base) 

            if self.naive_baysienne_radio_button.isChecked() or self.baysienne_radio_button.isChecked():
                auto_grade_database_to_csv_baysienne(self.graded_db,self.algo_base,self.mode, self.count_mode) 




        # clean / auto-grade tweets
        handle_column = QVBoxLayout() 

        clean_label = QLabel("Here you'll find all the tools to clean tweets")
        clean_label.setObjectName("secondary-title")

        sub_clean_label = QLabel("To properly clean the database, you must select the delimiter of your CSV file.\nWhen it's done, you can press the Clean Selected DataBase button.\nCare : Cleaning database can be long.\n")

        clean_db_layout = QHBoxLayout() #Layout for selected db (button + print) 

        clean_db_button = QPushButton("Choose DataBase")  
        clean_db_button.clicked.connect(lambda: display_popup("cleaned",False))

        self.clean_selected_db = QLabel("No database selected")

        see_clean_db_button = QPushButton("See DataBase") 
        see_clean_db_button.clicked.connect(lambda: display_db_popup(self.cleaned_db))
 
        clean_db_layout.addWidget(clean_db_button)
        clean_db_layout.addWidget(self.clean_selected_db)
        clean_db_layout.addWidget(see_clean_db_button)


        #  choice for the delimiter 
        delimiter_layout = QVBoxLayout() 

        delimiter_choice_layout = QHBoxLayout() 

        # DELIMITER LIST
        self.delimiter_list = QListWidget()
        
        self.delimiter_list.setMaximumWidth(int(self.width /4)) 
        self.delimiter_list.setMaximumHeight(int(self.height / 10))
        
        populate_delimiters() 
        
        self.delimiter_list.itemClicked.connect(get_and_store_delimiter)


        self.selected_delimiter_label = QLabel(f"Delimiter selected : '{self.selected_delimiter}'")
        
        delimiter_choice_layout.addWidget(self.delimiter_list) 
        delimiter_choice_layout.addWidget(self.selected_delimiter_label) 

        input_delimiter_layout = QHBoxLayout() 

        self.input_delimiter_text = QLineEdit() 
        self.input_delimiter_text.setPlaceholderText("Enter a new delimiter ...") 

        input_delimiter_button = QPushButton("Press here to add new delimiter") 
        input_delimiter_button.clicked.connect(add_delimiter)

        input_delimiter_layout.addWidget(self.input_delimiter_text) 
        input_delimiter_layout.addWidget(input_delimiter_button) 
        
        delimiter_layout.addLayout(delimiter_choice_layout) 
        delimiter_layout.addLayout(input_delimiter_layout)

        buttons_layout = QHBoxLayout()

        clean_button = QPushButton("Clean selected database")
        clean_button.clicked.connect(lambda : clean_csv(self.cleaned_db,self.selected_delimiter))

        buttons_layout.addWidget(clean_button) 


        handle_column.addWidget(clean_label)
        handle_column.addWidget(sub_clean_label) 
        handle_column.addLayout(clean_db_layout)
        handle_column.addLayout(delimiter_layout)
        handle_column.addWidget(clean_label)
        handle_column.addLayout(buttons_layout)
        
        self.layout.addLayout(handle_column)

        # GRADE COLUMN 

        grade_column = QVBoxLayout() 

        grade_label = QLabel("Here are all the tools to autograde databases\nCare ! The database has to be cleaned before")
        grade_label.setObjectName("secondary-title") 

        grade_db_layout = QHBoxLayout() #Layout for selected db (button + print) 

        grade_db_button = QPushButton("Choose DataBase")  
        grade_db_button.clicked.connect(lambda: display_popup("graded",False))

        self.grade_selected_db_label = QLabel("No database selected")

        see_grade_db_button = QPushButton("See DataBase") 
        see_grade_db_button.clicked.connect(lambda: display_db_popup(self.graded_db))
 
        grade_db_layout.addWidget(grade_db_button)
        grade_db_layout.addWidget(self.grade_selected_db_label)
        grade_db_layout.addWidget(see_grade_db_button)
        
        grade_function_label = QLabel("Please select the algorithm to use for the classification :") 
       
        grade_function_layout = QHBoxLayout()

        self.grade_algo_base_label = QLabel("No Base selected -- Base must be graded")
        
        grade_algo_base_button = QPushButton("Choose Base for Algorithm")
        grade_algo_base_button.clicked.connect(lambda: display_popup("algo_base",True)) 


        grade_function_layout.addWidget(self.grade_algo_base_label)
        grade_function_layout.addWidget(grade_algo_base_button) 
        
        k_layout = QHBoxLayout() 

        grade_function_knn_label = QLabel("KNN Algorithm") 


        k_label = QLabel("Please adjust k (number of neighbours) -- default k=11")
        k_selecteur = QSpinBox()
        k_selecteur.setRange(1,30) 
        k_selecteur.setValue(11)   
        k_selecteur.valueChanged.connect(set_k) 

        k_layout.addWidget(grade_function_knn_label)
        k_layout.addWidget(k_label) 
        k_layout.addWidget(k_selecteur) 


        baysienne_layout = QHBoxLayout()

        baysienne_label = QLabel("Baysienne Algorithm")

        self.combo_box = QComboBox()
        
        mode_list = ["Uni", "Bi", "Bi+Uni"]
        self.combo_box.addItems(mode_list)

        self.combo_box.currentTextChanged.connect(display_mode)

        self.label_resultat = QLabel("Select an option")
        
        self.case = QCheckBox("Switch")
        self.case.toggled.connect(set_count_mode)
        
        self.label_etat = QLabel("Presence")
        
        baysienne_layout.addWidget(baysienne_label)
        baysienne_layout.addWidget(self.combo_box) 
        baysienne_layout.addWidget(self.case)
        baysienne_layout.addWidget(self.label_etat)
        
        naive_baysienne_layout = QHBoxLayout()

        naive_baysienne_label = QLabel("All Permutations Comparaison for Baysienne") 
        naive_baysienne_label_fill = QLabel("-----------------NO PARAMETERS-----------------")

        naive_baysienne_layout.addWidget(naive_baysienne_label)
        naive_baysienne_layout.addWidget(naive_baysienne_label_fill)
        
        radio_layout = QHBoxLayout() 

        self.knn_radio_button = QRadioButton("Select KNN")
        self.baysienne_radio_button = QRadioButton("Select Bayesienne with Parameters") 
        self.naive_baysienne_radio_button = QRadioButton("Select All Permutations of Baysienne")

        self.knn_radio_button.setChecked(True)

        group = QButtonGroup()
        group.addButton(self.knn_radio_button)
        group.addButton(self.baysienne_radio_button)
        group.addButton(self.naive_baysienne_radio_button) 

        radio_layout.addWidget(self.knn_radio_button)
        radio_layout.addWidget(self.baysienne_radio_button)
        radio_layout.addWidget(self.naive_baysienne_radio_button) 

        grade_buttons_layout = QHBoxLayout() 

        grade_selected_db_button = QPushButton("Grade selected DataBase")
        grade_selected_db_button.clicked.connect(grade_selected_db)

        test_selected_database_button = QPushButton("Test selected algorithm with selected database")
        test_selected_database_button.clicked.connect(display_algo_accuracy_popup)

        grade_buttons_layout.addWidget(grade_selected_db_button) 
        grade_buttons_layout.addWidget(test_selected_database_button) 

        grade_column.addWidget(grade_label) 
        grade_column.addLayout(grade_db_layout)
        grade_column.addWidget(grade_function_label) 
        grade_column.addLayout(grade_function_layout)
        grade_column.addLayout(k_layout)
        grade_column.addLayout(baysienne_layout) 
        grade_column.addLayout(naive_baysienne_layout)
        grade_column.addLayout(radio_layout)
        grade_column.addLayout(grade_buttons_layout) 

        self.layout.addLayout(grade_column) 
