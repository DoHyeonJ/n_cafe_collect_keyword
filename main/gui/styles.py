DARK_STYLE = """
    QWidget {
        background-color: #2b2b2b;
        color: #bfbfbf;
        font-size: 14px;
    }
    QGroupBox {
        border: 1px solid #3c3f41;
        border-radius: 5px;
        margin-top: 5px;
        padding: 15px;
    }
    QLineEdit, QComboBox, QTextEdit, QDateTimeEdit, QSpinBox {
        background-color: #3c3f41;
        border: 1px solid #4a4a4a;
        padding: 8px;
        border-radius: 4px;
        color: #dcdcdc;
    }
    QPushButton, QRadioButton, QCheckBox {
        background-color: #3c3f41;
        color: white;
        border: 1px solid #3c3f41;
        padding: 10px;
        border-radius: 4px;
        text-align: center;
    }
    QPushButton:hover, QRadioButton:hover, QCheckBox:hover {
        background-color: #4a4a4a;
        border: 1px solid #4a4a4a;
    }
    QPushButton#execute {
        background-color: #4CAF50;
        border: 1px solid #4CAF50;
    }
    QPushButton#execute:hover {
        background-color: #45a049;
        border: 1px solid #45a049;
    }
    QPushButton#login_btn {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
    }
    QPushButton#login_btn:hover {
        background-color: #45a049;
    }
    QPushButton#logout_btn {
        background-color: #f44336;
        color: white;
        border: none;
        border-radius: 5px;
    }
    QPushButton#logout_btn:hover {
        background-color: #da190b;
    }
    QTableWidget {
        background-color: #2b2b2b;
        border: 1px solid #3c3f41;
        border-radius: 5px;
    }
    QHeaderView::section {
        background-color: #3c3f41;
        color: #dcdcdc;
        border: none;
        padding: 8px;
    }
    QTableWidget::item {
        border: none;
        padding: 5px;
    }
    QTableWidget::item:selected {
        background-color: #4a4a4a;
    }
    QDialog {
        background-color: #2b2b2b;
        color: #bfbfbf;
    }
    QTabWidget::pane {
        border: 1px solid #3c3f41;
        border-radius: 5px;
        padding: 5px;
    }
    QTabBar::tab {
        background-color: #2b2b2b;
        color: #bfbfbf;
        padding: 10px 30px;
        margin-right: 2px;
        border: 1px solid #3c3f41;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        background-color: #3c3f41;
        border-bottom: none;
    }
""" 