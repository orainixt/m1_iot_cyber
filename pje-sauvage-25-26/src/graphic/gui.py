import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QShortcut, QMessageBox
from PyQt5.QtGui import QKeySequence
from graphic.main_window import MainWindow
from pathlib import Path

def create_app(): 
    # Verify if there's already a Qt instance
    app = QApplication.instance() 

    if not app : 
        # If not, create it 
        app = QApplication(sys.argv)

    setStyle(app)

    window = MainWindow() 
    window.setWindowTitle("Sentiment analysis on Twitter") 

    screen = app.primaryScreen()
    w = int(screen.availableGeometry().width() * 0.8)
    h = int(screen.availableGeometry().height() * 0.8)
    window.setFixedSize(w, h)

    shortcut = QShortcut(QKeySequence("Escape"), window)
    shortcut.activated.connect(lambda: 
            QMessageBox.question(
                window,
                "EXIT", 
                "Are you sure you want to exit ?", 
                QMessageBox.Yes | QMessageBox.No
            ) ==  QMessageBox.Yes and app.quit()
        )


    return app, window


def setStyle(app):
    curr_dir = Path(__file__).resolve().parent
    style_file = curr_dir / "style.qss" 

    if style_file.exists(): 
        with open(style_file, 'r') as f: 
            app.setStyleSheet(f.read()) 
    else: 
        print("style sheet not found") 
    
