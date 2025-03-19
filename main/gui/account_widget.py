from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from ..api.auth import NaverAuth
import traceback
import os

class LoginWorker(QThread):
    finished = pyqtSignal(bool, dict)  # 성공 여부, 헤더 정보
    progress = pyqtSignal(str, str)  # 메시지, 색상

    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password
        self.auth = NaverAuth()

    def run(self):
        try:
            self.progress.emit(f"계정 {self.username} 로그인 시도 중...", "blue")
            
            # 자격 증명 설정
            self.auth.set_credentials(self.username, self.password)
            
            # 로그인 시도
            success, headers = self.auth.login()
            
            if success:
                self.progress.emit(f"계정 {self.username} 로그인 성공!", "green")
                self.finished.emit(True, headers)
            else:
                self.progress.emit(f"계정 {self.username} 로그인 실패", "red")
                self.finished.emit(False, {})
        except Exception as e:
            self.progress.emit(f"로그인 오류: {str(e)}", "red")
            print(traceback.format_exc())
            self.finished.emit(False, {})

class AccountWidget(QWidget):
    login_success = pyqtSignal(dict)  # 로그인 성공 시그널 (헤더 정보 전달)
    account_added = pyqtSignal(str, str)  # 계정 추가 시그널 (id, pw)
    
    def __init__(self, log, monitor_widget):
        super().__init__()
        self.log = log
        self.monitor_widget = monitor_widget
        self.login_worker = None  # 현재 로그인 워커
        self.current_account = None  # 현재 로그인된 계정
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 로그인 타이틀
        title_label = QLabel("계정 로그인")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # ID 입력
        id_layout = QHBoxLayout()
        id_label = QLabel("아이디:")
        id_label.setStyleSheet("color: white; min-width: 60px;")
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("네이버 아이디 입력")
        self.id_input.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3d3d3d;
                padding: 5px;
                border-radius: 3px;
            }
            QLineEdit:focus {
                border: 1px solid #5c85d6;
            }
        """)
        id_layout.addWidget(id_label)
        id_layout.addWidget(self.id_input)
        
        # 비밀번호 입력
        pw_layout = QHBoxLayout()
        pw_label = QLabel("비밀번호:")
        pw_label.setStyleSheet("color: white; min-width: 60px;")
        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("네이버 비밀번호 입력")
        self.pw_input.setEchoMode(QLineEdit.Password)  # 비밀번호 모드
        self.pw_input.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3d3d3d;
                padding: 5px;
                border-radius: 3px;
            }
            QLineEdit:focus {
                border: 1px solid #5c85d6;
            }
        """)
        pw_layout.addWidget(pw_label)
        pw_layout.addWidget(self.pw_input)
        
        # 로그인 버튼
        login_btn_layout = QHBoxLayout()
        self.login_btn = QPushButton("로그인")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #707070;
                color: #a0a0a0;
            }
        """)
        self.login_btn.clicked.connect(self.login_with_input)
        
        # 로그아웃 버튼
        self.logout_btn = QPushButton("로그아웃")
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #d65c5c;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #b84a4a;
            }
            QPushButton:disabled {
                background-color: #707070;
                color: #a0a0a0;
            }
        """)
        self.logout_btn.clicked.connect(self.logout)
        self.logout_btn.setEnabled(False)  # 초기에는 비활성화
        
        login_btn_layout.addWidget(self.login_btn)
        login_btn_layout.addWidget(self.logout_btn)
        
        # 로그인 상태 표시
        self.status_label = QLabel("로그인 상태: 로그인되지 않음")
        self.status_label.setStyleSheet("color: #cccccc; margin-top: 10px;")
        
        # 레이아웃 구성
        layout.addLayout(id_layout)
        layout.addLayout(pw_layout)
        layout.addLayout(login_btn_layout)
        layout.addWidget(self.status_label)
        
        # 여백 추가
        layout.addStretch()
        
        self.setLayout(layout)
        
    def login_with_input(self):
        """입력 필드에서 ID와 비밀번호를 가져와 로그인"""
        username = self.id_input.text().strip()
        password = self.pw_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "입력 오류", "아이디와 비밀번호를 모두 입력해주세요.")
            return
        
        # 로그인 버튼 비활성화
        self.login_btn.setEnabled(False)
        self.status_label.setText("로그인 상태: 로그인 시도 중...")
        self.status_label.setStyleSheet("color: #5c85d6; margin-top: 10px;")
        
        self.log.info(f"계정 '{username}'으로 로그인을 시도합니다.")
        self.start_login(username, password)
        
    def start_login(self, username, password):
        """계정 로그인 시작"""
        # 이전 로그인 워커가 있으면 정리
        if self.login_worker and self.login_worker.isRunning():
            self.login_worker.terminate()
            self.login_worker.wait()
        
        # 로그인 워커 생성
        self.login_worker = LoginWorker(username, password)
        self.login_worker.progress.connect(self.on_login_progress)
        self.login_worker.finished.connect(lambda success, headers: self.on_login_finished(success, headers, username, password))
        
        # 워커 시작
        self.login_worker.start()
        
    def on_login_progress(self, message, color):
        """로그인 진행상황 업데이트"""
        self.log.add_log(message, color)
        self.monitor_widget.add_log_message({'message': message, 'color': color})
        
    def on_login_finished(self, success, headers, username, password):
        """로그인 완료 처리"""
        if success:
            # 현재 계정 정보 저장
            self.current_account = username
            
            # 로그인 성공 상태 표시
            self.status_label.setText(f"로그인 상태: {username} (로그인됨)")
            self.status_label.setStyleSheet("color: #4CAF50; margin-top: 10px; font-weight: bold;")
            
            # 버튼 상태 변경
            self.login_btn.setEnabled(False)
            self.logout_btn.setEnabled(True)
            
            # 입력 필드 비활성화
            self.id_input.setEnabled(False)
            self.pw_input.setEnabled(False)
            
            # 계정 추가 시그널 발생
            self.account_added.emit(username, password)
            
            # 로그인 성공 시그널 발생
            self.login_success.emit(headers)
            
            self.log.info(f"계정 {username} 로그인 성공")
        else:
            # 로그인 실패 상태 표시
            self.status_label.setText("로그인 상태: 로그인 실패")
            self.status_label.setStyleSheet("color: #d65c5c; margin-top: 10px;")
            
            # 버튼 상태 변경
            self.login_btn.setEnabled(True)
            
            self.log.error(f"계정 {username} 로그인 실패")
            
            # 오류 메시지 표시
            QMessageBox.warning(self, "로그인 실패", "아이디 또는 비밀번호가 올바르지 않습니다.")
    
    def logout(self):
        """로그아웃 처리"""
        if not self.current_account:
            return
            
        # 로그아웃 메시지
        self.log.info(f"계정 '{self.current_account}'에서 로그아웃합니다.")
        
        # 현재 계정 초기화
        self.current_account = None
        
        # 상태 초기화
        self.status_label.setText("로그인 상태: 로그인되지 않음")
        self.status_label.setStyleSheet("color: #cccccc; margin-top: 10px;")
        
        # 입력 필드 초기화 및 활성화
        self.id_input.clear()
        self.pw_input.clear()
        self.id_input.setEnabled(True)
        self.pw_input.setEnabled(True)
        
        # 버튼 상태 변경
        self.login_btn.setEnabled(True)
        self.logout_btn.setEnabled(False) 