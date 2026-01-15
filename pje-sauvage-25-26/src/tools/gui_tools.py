from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets

def get_screen_size():
    # Récupère l'instance existante ou crée une instance temporaire
    app = QApplication.instance() or QApplication([])  
    screen = app.primaryScreen()
    size = screen.size()
    return size.width(), size.height()


def create_populate_db_tree(db_filenames,width): 
    """
    create and populate the db tree of all the databases in ./data
    width is used to resize 
    Args:
        db_filenames (_type_): _description_
        width (_type_): _description_

    Returns:
        _type_: _description_
    """
    db_tree = QtWidgets.QTreeWidget() 
    db_tree.setMaximumWidth(int(width * 0.6))
    db_tree.setHeaderLabels(["Name", "Options"])

    root = QtWidgets.QTreeWidgetItem(["Databases"])
    db_tree.addTopLevelItem(root) 

    for db in db_filenames: 
        item = QtWidgets.QTreeWidgetItem([db]) 
        root.addChild(item)

        selected_checkbox = QtWidgets.QCheckBox("Check")
        selected_checkbox.setObjectName("tree-checkbox")
        selected_checkbox.setMaximumWidth(30)
        db_tree.setItemWidget(item, 1, selected_checkbox)


    root.setExpanded(True)

    header = db_tree.header()
    header.setStretchLastSection(False)

    header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)

    return db_tree