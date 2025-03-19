from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, 
                           QVBoxLayout, QHBoxLayout, QGroupBox)
from PyQt5.QtCore import pyqtSignal
from ..api import API
from ..utils.log import Log
from .styles import DARK_STYLE

class LoginWidget(QWidget):
    login_success = pyqtSignal(dict)  # 로그인 성공 시그널

    def __init__(self, log: Log):
        super().__init__()
        self.log = log
        self.api = API(self.log)
        self.is_logged_in = False
        self.init_ui()

    def init_ui(self):
        group_box = QGroupBox()
        layout = QVBoxLayout()
        
        # 로그인 입력 레이아웃
        login_layout = QHBoxLayout()
        
        self.id_label = QLabel('ID')
        self.id_input = QLineEdit()
        self.id_input.setFixedHeight(40)
        
        self.pw_label = QLabel('PW')
        self.pw_input = QLineEdit()
        self.pw_input.setEchoMode(QLineEdit.Password)
        self.pw_input.setFixedHeight(40)
        
        self.toggle_pw_btn = QPushButton('비밀번호 보기')
        self.toggle_pw_btn.setCheckable(True)
        self.toggle_pw_btn.toggled.connect(self.toggle_password)
        
        self.login_btn = QPushButton('로그인')
        self.login_btn.clicked.connect(self.handle_login)
        self.login_btn.setObjectName("login_btn")
        
        self.logout_btn = QPushButton('로그아웃')
        self.logout_btn.clicked.connect(self.handle_logout)
        self.logout_btn.setObjectName("logout_btn")
        
        login_layout.addWidget(self.id_label)
        login_layout.addWidget(self.id_input)
        login_layout.addWidget(self.pw_label)
        login_layout.addWidget(self.pw_input)
        login_layout.addWidget(self.toggle_pw_btn)
        login_layout.addWidget(self.login_btn)
        login_layout.addWidget(self.logout_btn)
        
        layout.addLayout(login_layout)
        group_box.setLayout(layout)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(group_box)
        self.setLayout(main_layout)

    def toggle_password(self, checked):
        self.pw_input.setEchoMode(
            QLineEdit.Normal if checked else QLineEdit.Password
        )
        self.toggle_pw_btn.setText(
            '비밀번호 숨김' if checked else '비밀번호 보기'
        )

    def handle_login(self):
        if not self.id_input.text() or not self.pw_input.text():
            self.log.add_log("ID와 비밀번호를 입력해주세요.", "red")
            return

        self.log.add_log("로그인을 시작합니다...")
        success = self.api.auto_login(
            self.id_input.text().strip(),
            self.pw_input.text().strip()
        )

        if success:
            self.is_logged_in = True
            self.id_input.setEnabled(False)
            self.pw_input.setEnabled(False)
            self.login_btn.setEnabled(False)
            self.log.add_log("로그인에 성공했습니다.", "green")
            # 로그인 성공 시그널 발생
            self.login_success.emit(self.api.headers)
        else:
            self.log.add_log("로그인에 실패했습니다.", "red")

    def handle_logout(self):
        if not self.is_logged_in:
            self.log.add_log("로그인 되어있지 않습니다.", "red")
            return
            
        self.is_logged_in = False
        self.id_input.clear()
        self.pw_input.clear()
        self.id_input.setEnabled(True)
        self.pw_input.setEnabled(True)
        self.login_btn.setEnabled(True)
        self.log.add_log("로그아웃 되었습니다.") 