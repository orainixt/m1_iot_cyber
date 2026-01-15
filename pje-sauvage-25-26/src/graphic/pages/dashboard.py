from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QStackedWidget, QWidget, QVBoxLayout, QLabel, QAction, QCheckBox, QHBoxLayout
from tools.gui_tools import get_screen_size


class DashBoard(QWidget):
    def __init__(self,stack):
        super().__init__()

        self.stack = stack

        self.layout = QVBoxLayout() 
        (self.width, self.height) = get_screen_size()

        self.init_widget()

        self.setLayout(self.layout)


    def init_widget(self): 
        
        self.layout.setSpacing(0)

        # TITLE AND SELF ID

        title = QLabel("Sentiment analysis on Twitter")
        title.setAlignment(Qt.AlignCenter) 
        title.setStyleSheet("font-size:72px;")
        title.setMaximumHeight(int(self.height * 0.10))

        self_id = QLabel("Created by Lucas Sauvage | Informatic Master")
        self_id.setAlignment(Qt.AlignCenter)
        self_id.setMaximumHeight(int(self.height * 0.05))

        title_layout = QVBoxLayout()

        title_layout.addWidget(title)
        title_layout.addWidget(self_id)


        self.layout.addLayout(title_layout)

        # SUMMARY 

        summary = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam vel tincidunt mi. Sed interdum ullamcorper scelerisque. Proin rhoncus dignissim ligula, quis auctor elit. Quisque aliquet, mauris nec gravida ornare, nulla erat cursus lacus, in pretium nibh nibh vitae enim. Duis pellentesque neque nibh, in placerat mauris porttitor rutrum. Nulla facilisi. Pellentesque hendrerit leo quis sollicitudin auctor. In egestas, urna id malesuada ultrices, ex ipsum venenatis nisi, a maximus orci lorem vel dolor. Fusce nec facilisis quam. In hendrerit pellentesque ligula, quis elementum ligula volutpat vel. Cras dapibus scelerisque dui, convallis tincidunt turpis aliquam vel. Nam eleifend neque vel ultrices laoreet. Phasellus eleifend eget urna a varius." 

        summary_label = QLabel(summary) 

        summary_label.setAlignment(Qt.AlignCenter)

        summary_label.setWordWrap(True)  
        self.layout.addWidget(summary_label)

        columns_layout = QHBoxLayout()

        # DATABASE ACCESS

        db_col = QVBoxLayout()
        
        db_title = QLabel("DataBase Handler") 
        db_title.setAlignment(Qt.AlignTop | Qt.AlignCenter) 
        see_db_button = QPushButton("Click here to handle database")
        see_db_button.clicked.connect(self.see_tweets)

        db_col.addWidget(db_title)
        db_col.addWidget(see_db_button)

        columns_layout.addLayout(db_col)

        self.layout.addLayout(columns_layout)

    def see_tweets(self): 
        self.stack.setCurrentIndex(1)

