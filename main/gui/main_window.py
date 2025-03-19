from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                           QGroupBox, QTabWidget, QPushButton, QLabel, QLineEdit, QTextEdit, 
                           QComboBox, QCheckBox, QRadioButton, QButtonGroup, QFrame, QSpacerItem, 
                           QSizePolicy, QAction, QFileDialog, QMenu, QMenuBar, QMessageBox, 
                           QSystemTrayIcon, QToolBar, QInputDialog, QDialog, QProgressDialog, QFormLayout, QListWidget, QScrollArea, QSpinBox, QTableWidgetItem)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSettings, QSize, QUrl, QRect, QPoint
from PyQt5.QtGui import QIcon, QPixmap, QDesktopServices, QFont, QColor

from .routine_tab import RoutineTab
from .account_widget import AccountWidget
from .task_settings_dialog import TaskSettingsDialog
from .settings_dialog import SettingsDialog

from ..utils.log import Log
from ..utils.licence import Licence
from ..utils.settings_manager import SettingsManager
from ..api.auth import NaverAuth
from ..api.cafe import CafeAPI
from ..api.ai_generator import AIGenerator
from .styles import DARK_STYLE
from ..worker import Worker
import time
import os
import sys

class TaskDetailDialog(QDialog):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.init_ui()
        
    def init_ui(self):
        # 대화상자 설정
        self.setWindowTitle(f"작업 #{self.task['id']} 상세 정보")
        self.setMinimumSize(700, 450)  # 높이 줄임
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: white;
            }
            QLabel {
                color: white;
            }
            QGroupBox {
                color: white;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 기본 정보 그룹
        basic_group = QGroupBox("기본 정보")
        basic_layout = QFormLayout()
        basic_layout.setContentsMargins(15, 20, 15, 15)
        basic_layout.setSpacing(10)
        
        # 계정 정보
        account_count = len(self.task.get('all_accounts', []))
        self.account_label = QLabel(f"{account_count}개 계정")
        
        # 계정 목록 대화상자 버튼
        self.show_accounts_btn = QPushButton("계정 목록 보기")
        self.show_accounts_btn.setStyleSheet("""
            QPushButton {
                background-color: #5c85d6;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4a6fb8;
            }
        """)
        self.show_accounts_btn.clicked.connect(self.show_accounts_dialog)
        
        # 계정 컨테이너
        account_container = QWidget()
        account_layout = QHBoxLayout()  # 가로 배치로 변경
        account_layout.setContentsMargins(0, 0, 0, 0)
        account_layout.setSpacing(10)
        account_layout.addWidget(self.account_label)
        account_layout.addWidget(self.show_accounts_btn)
        account_container.setLayout(account_layout)
        
        # 카페 및 게시판 정보
        cafe_info = self.task['cafe_info']
        board_info = self.task['board_info']
        cafe_label = QLabel(f"{cafe_info['cafe_name']}")
        board_label = QLabel(f"{board_info['board_name']}")
        
        # 기본 정보 추가
        basic_layout.addRow("계정:", account_container)
        basic_layout.addRow("카페:", cafe_label)
        basic_layout.addRow("게시판:", board_label)
        basic_group.setLayout(basic_layout)
        
        # 작업 설정 그룹
        task_group = QGroupBox("작업 설정")
        task_layout = QFormLayout()
        task_layout.setContentsMargins(15, 20, 15, 15)
        task_layout.setSpacing(10)
        
        # 작업 설정 정보
        cafe_settings = self.task['cafe_settings']
        post_count = cafe_settings.get('post_count', 0)
        comment_min = cafe_settings.get('comment_count', {}).get('min', 0)
        comment_max = cafe_settings.get('comment_count', {}).get('max', 0)
        like_min = cafe_settings.get('like_count', {}).get('min', 0)
        like_max = cafe_settings.get('like_count', {}).get('max', 0)
        
        # 작업 설정 추가
        task_layout.addRow("게시글 수집:", QLabel(f"{post_count}개"))
        task_layout.addRow("댓글 작업:", QLabel(f"{comment_min}~{comment_max}개 (랜덤)"))
        task_layout.addRow("좋아요 작업:", QLabel(f"{like_min}~{like_max}개 (랜덤)"))
        task_group.setLayout(task_layout)
        
        # 댓글 설정 그룹
        comment_group = QGroupBox("댓글 설정")
        comment_layout = QFormLayout()
        comment_layout.setContentsMargins(15, 20, 15, 15)
        comment_layout.setSpacing(10)
        
        # 댓글 설정 정보
        comment_settings = self.task['comment_settings']
        interval = comment_settings.get('interval', {})
        interval_min = interval.get('min', 0)
        interval_max = interval.get('max', 0)
        use_keywords = '사용' if comment_settings.get('use_keywords', False) else '미사용'
        prevent_duplicate = '사용' if comment_settings.get('prevent_duplicate', True) else '미사용'
        
        # 프롬프트 목록
        prompts = comment_settings.get('prompts', [])
        prompt_count = len(prompts)
        
        # 프롬프트 대화상자 버튼
        self.show_prompts_btn = QPushButton("AI 프롬프트 보기")
        self.show_prompts_btn.setStyleSheet("""
            QPushButton {
                background-color: #5c85d6;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4a6fb8;
            }
        """)
        self.show_prompts_btn.clicked.connect(self.show_prompts_dialog)
        
        # 프롬프트 컨테이너
        prompt_container = QWidget()
        prompt_layout = QHBoxLayout()  # 가로 배치로 변경
        prompt_layout.setContentsMargins(0, 0, 0, 0)
        prompt_layout.setSpacing(10)
        prompt_layout.addWidget(QLabel(f"{prompt_count}개 등록됨"))
        prompt_layout.addWidget(self.show_prompts_btn)
        prompt_container.setLayout(prompt_layout)
        
        # 댓글 설정 추가
        comment_layout.addRow("댓글 간격:", QLabel(f"{interval_min}~{interval_max}초 (랜덤)"))
        comment_layout.addRow("키워드 사용:", QLabel(use_keywords))
        comment_layout.addRow("중복 방지:", QLabel(prevent_duplicate))
        comment_layout.addRow("AI 프롬프트:", prompt_container)
        comment_group.setLayout(comment_layout)
        
        # 확인 버튼
        close_btn = QPushButton("확인")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #5c85d6;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: 100px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a6fb8;
            }
        """)
        close_btn.clicked.connect(self.accept)
        
        # 레이아웃에 위젯 추가
        main_layout.addWidget(basic_group)
        main_layout.addWidget(task_group)
        main_layout.addWidget(comment_group)
        main_layout.addWidget(close_btn, alignment=Qt.AlignCenter)
        
        self.setLayout(main_layout)
    
    def show_accounts_dialog(self):
        """계정 목록을 별도의 대화상자로 표시"""
        accounts = self.task.get('all_accounts', [])
        if not accounts:
            QMessageBox.information(self, "계정 목록", "등록된 계정이 없습니다.")
            return
            
        # 계정 목록 대화상자 생성
        dialog = QDialog(self)
        dialog.setWindowTitle("계정 목록")
        dialog.setMinimumSize(300, 400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: white;
            }
            QLabel {
                color: white;
            }
            QListWidget {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #444;
            }
            QListWidget::item:selected {
                background-color: #4a6fb8;
            }
            QPushButton {
                background-color: #5c85d6;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #4a6fb8;
            }
        """)
        
        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 계정 수 표시
        count_label = QLabel(f"총 {len(accounts)}개 계정")
        count_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(count_label)
        
        # 계정 목록 위젯
        account_list = QListWidget()
        for account in accounts:
            account_list.addItem(account)
        layout.addWidget(account_list)
        
        # 닫기 버튼
        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def show_prompts_dialog(self):
        """프롬프트 목록을 별도의 대화상자로 표시"""
        prompts = self.task['comment_settings'].get('prompts', [])
        if not prompts:
            QMessageBox.information(self, "AI 프롬프트", "등록된 프롬프트가 없습니다.")
            return
            
        # 프롬프트 목록 대화상자 생성
        dialog = QDialog(self)
        dialog.setWindowTitle("AI 프롬프트 목록")
        dialog.setMinimumSize(500, 400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: white;
            }
            QLabel {
                color: white;
            }
            QScrollArea {
                border: 1px solid #555;
                background-color: #333;
            }
            QPushButton {
                background-color: #5c85d6;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #4a6fb8;
            }
        """)
        
        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 프롬프트 수 표시
        count_label = QLabel(f"총 {len(prompts)}개 프롬프트")
        count_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(count_label)
        
        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # 프롬프트 컨테이너
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.setSpacing(10)
        
        # 프롬프트 목록 추가
        for i, prompt in enumerate(prompts, 1):
            prompt_frame = QWidget()
            prompt_frame.setStyleSheet("background-color: #3a3a3a; border-radius: 4px;")
            
            prompt_layout = QVBoxLayout()
            prompt_layout.setContentsMargins(10, 10, 10, 10)
            
            # 프롬프트 번호
            number_label = QLabel(f"프롬프트 #{i}")
            number_label.setStyleSheet("color: #aaa; font-size: 12px;")
            
            # 프롬프트 내용
            content_label = QLabel(prompt)
            content_label.setWordWrap(True)
            content_label.setStyleSheet("color: #ddd; padding: 5px 0;")
            
            prompt_layout.addWidget(number_label)
            prompt_layout.addWidget(content_label)
            prompt_frame.setLayout(prompt_layout)
            
            container_layout.addWidget(prompt_frame)
        
        container_layout.addStretch()
        container.setLayout(container_layout)
        scroll.setWidget(container)
        
        layout.addWidget(scroll)
        
        # 닫기 버튼
        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)
        
        dialog.setLayout(layout)
        dialog.exec_()

class TaskListItem(QWidget):
    def __init__(self, task_name, task_info, task_number, parent=None):
        super().__init__(parent)
        self.task_info = task_info  # 작업 정보 저장
        self.task_number = task_number  # 작업 번호 저장
        
        # 클릭 가능한 스타일 설정
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 4px;
            }
            QWidget:hover {
                background-color: #3a3a3a;
                cursor: pointer;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(12)
        
        # 왼쪽 상태 표시 바 & 번호
        left_container = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(2)
        
        # 작업 번호
        self.number_label = QLabel(f"#{task_number}")
        self.number_label.setStyleSheet("""
            color: #5c85d6;
            font-size: 14px;
            font-weight: bold;
        """)
        
        # 상태 표시 바
        self.status_bar = QWidget()
        self.status_bar.setFixedWidth(4)
        self.status_bar.setMinimumHeight(40)
        self.status_bar.setStyleSheet("""
            background-color: #5c85d6;
            border-radius: 2px;
        """)
        
        left_layout.addWidget(self.number_label, alignment=Qt.AlignCenter)
        left_layout.addWidget(self.status_bar, alignment=Qt.AlignCenter)
        left_container.setLayout(left_layout)
        
        # 중앙 정보 영역
        info_container = QWidget()
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)
        
        # 계정 및 검색 정보
        main_info_layout = QHBoxLayout()
        main_info_layout.setContentsMargins(0, 0, 0, 0)
        main_info_layout.setSpacing(15)  # 간격 증가
        
        # 계정 정보
        self.account_label = QLabel(f"계정: {task_info.get('account_id', '알 수 없음')}")
        self.account_label.setStyleSheet("""
            color: white;
            font-size: 13px;
            font-weight: bold;
        """)
        
        # 키워드 및 대상 정보
        keywords = task_info.get('keywords', '')
        target = task_info.get('target', '전체글')
        
        self.search_info_label = QLabel(f"키워드: {keywords} | 대상: {target}")
        self.search_info_label.setStyleSheet("""
            color: white;
            font-size: 13px;
        """)
        self.search_info_label.setToolTip(f"키워드: {keywords}\n대상: {target}")  # 전체 내용 툴크로 표시
        
        main_info_layout.addWidget(self.account_label)
        main_info_layout.addWidget(self.search_info_label)
        main_info_layout.addStretch()
        
        # 진행 상태 및 카운트 정보
        status_info_layout = QHBoxLayout()
        status_info_layout.setContentsMargins(0, 0, 0, 0)
        status_info_layout.setSpacing(15)
        
        # 상태 레이블
        self.status_label = QLabel(f"상태: {task_info.get('status', '대기 중')}")
        self.status_label.setStyleSheet("""
            color: #aaaaaa;
            font-size: 12px;
        """)
        
        # 진행률 레이블
        progress = task_info.get('progress', 0)
        self.progress_label = QLabel(f"진행률: {progress}%")
        self.progress_label.setStyleSheet("""
            color: #aaaaaa;
            font-size: 12px;
        """)
        
        # 결과 카운트 레이블
        completed = task_info.get('completed_count', 0)
        error = task_info.get('error_count', 0)
        self.count_label = QLabel(f"완료: {completed} | 오류: {error}")
        self.count_label.setStyleSheet("""
            color: #aaaaaa;
            font-size: 12px;
        """)
        
        status_info_layout.addWidget(self.status_label)
        status_info_layout.addWidget(self.progress_label)
        status_info_layout.addWidget(self.count_label)
        status_info_layout.addStretch()
        
        # 정보 레이아웃에 추가
        info_layout.addLayout(main_info_layout)
        info_layout.addLayout(status_info_layout)
        info_container.setLayout(info_layout)
        
        # 레이아웃에 위젯 추가
        layout.addWidget(left_container)
        layout.addWidget(info_container, stretch=1)
        self.setLayout(layout)
        
        # 상태에 따른 스타일 설정
        self.update_status_style(task_info.get('status', '대기 중'))
    
    def limit_text(self, text, max_length):
        """텍스트 길이 제한 함수"""
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text
        
    def update_status_style(self, status):
        """상태에 따른 스타일 업데이트"""
        if status == '진행 중':
            self.status_bar.setStyleSheet("""
                background-color: #5c85d6;
                border-radius: 2px;
            """)
            self.status_label.setStyleSheet("""
                color: #5c85d6;
                font-size: 12px;
                font-weight: bold;
            """)
        elif status == '완료':
            self.status_bar.setStyleSheet("""
                background-color: #4CAF50;
                border-radius: 2px;
            """)
            self.status_label.setStyleSheet("""
                color: #4CAF50;
                font-size: 12px;
                font-weight: bold;
            """)
        elif status == '실패' or status == '오류':
            self.status_bar.setStyleSheet("""
                background-color: #f44336;
                border-radius: 2px;
            """)
            self.status_label.setStyleSheet("""
                color: #f44336;
                font-size: 12px;
                font-weight: bold;
            """)
        elif status == '중지됨':
            self.status_bar.setStyleSheet("""
                background-color: #ff9800;
                border-radius: 2px;
            """)
            self.status_label.setStyleSheet("""
                color: #ff9800;
                font-size: 12px;
                font-weight: bold;
            """)
        else:  # '대기 중' 또는 기타 상태
            self.status_bar.setStyleSheet("""
                background-color: #9e9e9e;
                border-radius: 2px;
            """)
            self.status_label.setStyleSheet("""
                color: #9e9e9e;
                font-size: 12px;
                font-weight: bold;
            """)
            
    def set_post_url(self, url, title=None):
        """게시글 URL 설정 (이전 코드와의 호환성을 위해 유지)"""
        # 상태 업데이트만 수행
        self.update_status_style('완료')
        
    def sizeHint(self):
        """위젯 크기 힌트"""
        return QSize(0, 60)  # 이전보다 더 높게 설정 (두 줄 정보를 표시하므로)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 로그 초기화
        self.log = Log()
        
        # 라이선스 초기화
        self.licence = Licence()
        
        # 계정 정보 초기화
        self.accounts = {}  # 계정 정보 저장 딕셔너리
        
        # 작업 목록 초기화
        self.tasks = []  # 작업 목록
        self.next_task_id = 1  # 다음 작업 ID
        
        # 작업 실행 상태
        self.is_running = False
        self.workers = []  # 워커 목록
        
        # 시그널 연결 상태 추적
        self.task_list_click_connected = False
        
        # 모니터링 위젯 생성
        self.monitor_widget = RoutineTab(self.log)
        
        # 모니터링 위젯 시그널 연결
        self.monitor_widget.execute_tasks_clicked.connect(self.run_tasks)
        
        # 라이선스 확인
        if not self.check_and_create_license():
            self.handle_missing_license()
            return
            
        # UI 초기화
        self.init_ui()

    def check_and_create_license(self):
        """라이선스 파일을 체크하고 없으면 생성하는 함수"""
        try:
            # 라이선스 파일이 없는 경우
            if not os.path.exists('licence.json'):
                return self.handle_missing_license()

            # 라이선스 파일이 있는 경우 유효성 검사
            licence_key = self.licence.get_licence_key()
            is_valid, message = self.licence.check_license(licence_key)

            if not is_valid:
                # 유효하지 않은 라이선스인 경우
                QMessageBox.warning(self, '라이선스 오류', f'라이선스가 유효하지 않습니다.\n{message}')
                
                # 라이선스 파일 삭제
                if os.path.exists('licence.json'):
                    os.remove('licence.json')
                
                # 다시 라이선스 입력 처리
                return self.handle_missing_license()

            # 라이선스가 만료된 경우
            if self.licence.is_expired():
                QMessageBox.critical(self, '라이선스 만료', '라이선스가 만료되었습니다.\n라이선스를 연장하시기 바랍니다.')
                QDesktopServices.openUrl(QUrl("https://do-hyeon.tistory.com/pages/%EB%9D%BC%EC%9D%B4%EC%84%A0%EC%8A%A4-%EA%B5%AC%EB%A7%A4%EC%97%B0%EC%9E%A5-%EA%B0%80%EC%9D%B4%EB%93%9C"))
                return False

            return True

        except Exception as e:
            QMessageBox.critical(self, '오류', '알 수 없는 오류가 발생하였습니다.\n프로그램을 다시 실행해주세요.')
            self.log.add_log(f"라이선스 확인 중 오류 발생: {str(e)}", "red")
            return False

    def handle_missing_license(self):
        """라이선스가 없는 경우 처리"""
        while True:
            input_dialog = QInputDialog(self)
            input_dialog.setWindowTitle('라이선스 키 입력')
            input_dialog.setLabelText('라이선스 키를 입력해주세요:')
            input_dialog.resize(400, 200)
            
            ok = input_dialog.exec_()
            licence_key = input_dialog.textValue().strip()
            
            if not ok:
                return False
                
            if not licence_key:
                QMessageBox.warning(self, '경고', '라이선스 키를 입력해주세요.')
                continue
            
            # 라이선스 유효성 검사
            is_valid, message = self.licence.check_license(licence_key)
            
            if is_valid:
                # 라이선스 정보 저장
                if self.licence.save_licence(licence_key, message):
                    QMessageBox.information(self, '알림', '유효한 라이선스가 확인되었습니다.')
                    return True
                else:
                    QMessageBox.warning(self, '오류', '라이선스 저장 중 오류가 발생했습니다.')
                    continue
            else:
                retry = QMessageBox.question(
                    self,
                    '라이선스 오류',
                    f'유효하지 않은 라이선스입니다.\n사유: {message}\n\n다시 시도하시겠습니까?',
                    QMessageBox.Yes | QMessageBox.No
                )
                if retry == QMessageBox.No:
                    return False
                    
        return False

    def init_ui(self):
        # 메인 위젯 생성
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 메인 레이아웃 설정 (좌우 분할)
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        
        # 좌측 영역 (계정 관리 + 설정)
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        
        # 계정 관리 영역 (좌측 상단)
        account_group = QGroupBox("계정 관리")
        account_layout = QVBoxLayout()
        account_group.setLayout(account_layout)
        
        # 계정 위젯 생성
        self.account_widget = AccountWidget(self.log, self.monitor_widget)
        account_layout.addWidget(self.account_widget)
        
        # 계정 위젯 시그널 연결
        self.account_widget.login_success.connect(self.on_login_success)
        self.account_widget.account_added.connect(self.add_account_to_list)
        
        # 설정 영역 (좌측 하단)
        settings_group = QGroupBox("설정")
        settings_layout = QVBoxLayout()
        settings_group.setLayout(settings_layout)
        
        # 작업 설정 정보 표시
        settings_info = QWidget()
        settings_info_layout = QVBoxLayout()
        settings_info_layout.setSpacing(10)
        
        # 검색 설정 영역
        search_settings = QWidget()
        search_layout = QVBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(10)
        
        # 검색 키워드 입력
        keyword_widget = QWidget()
        keyword_layout = QHBoxLayout()
        keyword_layout.setContentsMargins(0, 0, 0, 0)
        
        keyword_label = QLabel("검색 키워드:")
        keyword_label.setStyleSheet("color: white;")
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("검색할 키워드를 입력하세요")
        self.keyword_input.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3d3d3d;
                padding: 8px;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #5c85d6;
            }
        """)
        
        keyword_layout.addWidget(keyword_label)
        keyword_layout.addWidget(self.keyword_input)
        keyword_widget.setLayout(keyword_layout)
        
        # 검색 대상 설정
        target_widget = QWidget()
        target_layout = QHBoxLayout()
        target_layout.setContentsMargins(0, 0, 0, 0)
        
        target_label = QLabel("대상:")
        target_label.setStyleSheet("color: white;")
        self.target_combo = QComboBox()
        self.target_combo.addItems(["전체글", "거래글", "일반글", "카페명"])
        self.target_combo.setStyleSheet("""
            QComboBox {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3d3d3d;
                padding: 5px;
                border-radius: 4px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(resources/down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_combo)
        target_widget.setLayout(target_layout)
        
        # 정렬 설정
        sort_widget = QWidget()
        sort_layout = QHBoxLayout()
        sort_layout.setContentsMargins(0, 0, 0, 0)
        
        sort_label = QLabel("정렬:")
        sort_label.setStyleSheet("color: white;")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["관련도순", "최신순", "1시간", "1일", "1주", "1개월", "3개월", "6개월", "1년"])
        self.sort_combo.setStyleSheet(self.target_combo.styleSheet())
        
        sort_layout.addWidget(sort_label)
        sort_layout.addWidget(self.sort_combo)
        sort_widget.setLayout(sort_layout)
        
        # 거래방법 설정
        trade_widget = QWidget()
        trade_layout = QHBoxLayout()
        trade_layout.setContentsMargins(0, 0, 0, 0)
        
        trade_label = QLabel("거래방법:")
        trade_label.setStyleSheet("color: white;")
        self.trade_combo = QComboBox()
        self.trade_combo.addItems(["전체", "안전결제", "일반결제"])
        self.trade_combo.setStyleSheet(self.target_combo.styleSheet())
        
        trade_layout.addWidget(trade_label)
        trade_layout.addWidget(self.trade_combo)
        trade_widget.setLayout(trade_layout)
        
        # 거래상태 설정
        status_widget = QWidget()
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        
        status_label = QLabel("거래상태:")
        status_label.setStyleSheet("color: white;")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["전체", "판매중", "판매완료"])
        self.status_combo.setStyleSheet(self.target_combo.styleSheet())
        
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_combo)
        status_widget.setLayout(status_layout)
        
        # AI 설정 영역
        ai_settings = QWidget()
        ai_layout = QVBoxLayout()
        ai_layout.setContentsMargins(0, 0, 0, 0)
        ai_layout.setSpacing(10)
        
        # AI API Key 설정
        api_key_widget = QWidget()
        api_key_layout = QHBoxLayout()
        api_key_layout.setContentsMargins(0, 0, 0, 0)
        api_key_layout.setSpacing(5)
        
        api_key_label = QLabel("AI API Key:")
        api_key_label.setStyleSheet("color: white;")
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("API Key를 입력하세요")
        self.api_key_input.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3d3d3d;
                padding: 8px;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #5c85d6;
            }
        """)
        
        # 검증 버튼 추가
        self.validate_api_btn = QPushButton("검증")
        self.validate_api_btn.setFixedWidth(60)
        self.validate_api_btn.setStyleSheet("""
            QPushButton {
                background-color: #5c85d6;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4a6fb8;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
        """)
        self.validate_api_btn.clicked.connect(self.validate_api_key)
        
        # 검증 상태 레이블 추가
        self.api_key_status = QLabel("")
        self.api_key_status.setStyleSheet("color: #aaaaaa; margin-left: 5px;")
        
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        api_key_layout.addWidget(self.validate_api_btn)
        api_key_layout.addWidget(self.api_key_status)
        api_key_widget.setLayout(api_key_layout)
        
        # AI 분석 키워드 설정
        ai_keyword_widget = QWidget()
        ai_keyword_layout = QHBoxLayout()
        ai_keyword_layout.setContentsMargins(0, 0, 0, 0)
        
        ai_keyword_label = QLabel("AI 분석 키워드:")
        ai_keyword_label.setStyleSheet("color: white;")
        self.ai_keyword_input = QLineEdit()
        self.ai_keyword_input.setPlaceholderText("분석할 키워드를 입력하세요")
        self.ai_keyword_input.setStyleSheet(self.api_key_input.styleSheet())
        
        ai_keyword_layout.addWidget(ai_keyword_label)
        ai_keyword_layout.addWidget(self.ai_keyword_input)
        ai_keyword_widget.setLayout(ai_keyword_layout)
        
        # AI 설정 추가
        ai_layout.addWidget(api_key_widget)
        ai_layout.addWidget(ai_keyword_widget)
        ai_settings.setLayout(ai_layout)
        
        # 검색 설정 추가
        search_layout.addWidget(keyword_widget)  # 검색 키워드 추가
        search_layout.addWidget(target_widget)
        search_layout.addWidget(sort_widget)
        search_layout.addWidget(trade_widget)
        search_layout.addWidget(status_widget)
        search_settings.setLayout(search_layout)
        
        # 설정 정보 레이아웃에 위젯 추가
        settings_info_layout.addWidget(search_settings)  # 검색 설정 추가
        settings_info_layout.addWidget(ai_settings)  # AI 설정 추가
        settings_info.setLayout(settings_info_layout)
        
        # 설정 영역에 위젯 추가
        settings_layout.addWidget(settings_info)
        
        # 좌측 레이아웃에 위젯 추가 (비율 6:4)
        left_layout.addWidget(account_group, 6)
        left_layout.addWidget(settings_group, 4)
        
        # 우측 영역 (모니터링/작업)
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        
        # 모니터링 영역
        monitor_group = QGroupBox("모니터링")
        monitor_layout = QVBoxLayout()
        monitor_group.setLayout(monitor_layout)
        
        # 모니터링 위젯 추가
        monitor_layout.addWidget(self.monitor_widget)
        
        # 우측 레이아웃에 모니터링 그룹 추가
        right_layout.addWidget(monitor_group)
        
        # 메인 레이아웃에 좌우 위젯 추가 (비율 3:7)
        main_layout.addWidget(left_widget, 3)
        main_layout.addWidget(right_widget, 7)
        
        # 메뉴바 생성
        self.create_menu_bar()
        
        # 윈도우 설정
        self.setWindowTitle("네이버 카페 댓글 프로그램")
        self.setGeometry(100, 100, 1050, 750)
        self.setStyleSheet(DARK_STYLE)

    def create_menu_bar(self):
        """메뉴바 생성"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #2b2b2b;
                color: white;
                border-bottom: 1px solid #3d3d3d;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
            }
            QMenuBar::item:selected {
                background-color: #3d3d3d;
            }
            QMenu {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3d3d3d;
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: #3d3d3d;
            }
        """)
        
        # 파일 메뉴
        file_menu = menubar.addMenu('파일')
        
        # 작업 설정 관리 메뉴
        task_settings_action = QAction('작업 설정 관리', self)
        task_settings_action.triggered.connect(self.show_task_settings_dialog)
        file_menu.addAction(task_settings_action)
        
        # 구분선
        file_menu.addSeparator()
        
        # 종료 메뉴
        exit_action = QAction('종료', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 도움말 메뉴
        help_menu = menubar.addMenu('도움말')
        
        # 라이선스 정보 메뉴
        # license_action = QAction('라이선스 정보', self)
        # license_action.triggered.connect(self.show_license_info)
        # help_menu.addAction(license_action)
        
        # 프로그램 정보 메뉴
        about_action = QAction('프로그램 정보', self)
        about_action.triggered.connect(self.show_about_info)
        help_menu.addAction(about_action)
        
        # 개발문의하기 메뉴
        contact_action = QAction('개발문의하기', self)
        contact_action.triggered.connect(self.show_contact_info)
        help_menu.addAction(contact_action)

    def show_task_settings_dialog(self):
        """작업 설정 관리 대화상자 표시"""
        dialog = TaskSettingsDialog(self)
        dialog.exec_()
        
    def show_license_info(self):
        """라이선스 정보 표시"""
        license_key = self.licence.get_licence_key()
        expiry_date = self.licence.get_expiry_date()
        
        message = f"""
라이선스 정보:
- 라이선스 키: {license_key}
- 만료일: {expiry_date}
        """
        
        QMessageBox.information(self, "라이선스 정보", message)
        
    def show_about_info(self):
        """프로그램 정보 표시"""
        message = """
네이버 카페 키워드 게시글 수집 프로그램

© 2025 bedogdog. All Rights Reserved.
        """
        
        QMessageBox.information(self, "프로그램 정보", message)
        
    def show_contact_info(self):
        """개발문의 정보 표시 및 링크 열기"""
        message = """
개발 문의는 아래 텔레그램으로 연락해주세요:
@bedogdog

링크를 클릭하시겠습니까?
        """
        
        reply = QMessageBox.question(
            self, 
            "개발문의하기", 
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            # 텔레그램 링크 열기
            QDesktopServices.openUrl(QUrl("https://t.me/bedogdog"))

    def show_settings_dialog(self):
        """설정 관리 대화상자 표시"""
        dialog = SettingsDialog(self.settings_manager, self)
        dialog.setStyleSheet(DARK_STYLE)
        dialog.exec_()

    def get_all_settings(self):
        """현재 모든 설정값 반환 - 계정 목록과 작업 목록만 저장"""
        # 작업 설정 정보 가져오기
        task_settings = {
            'min_interval': self.monitor_widget.min_interval.value(),
            'max_interval': self.monitor_widget.max_interval.value(),
            'repeat': self.monitor_widget.repeat_checkbox.isChecked(),
            'use_ip_tethering': self.monitor_widget.ip_tethering_checkbox.isChecked(),
            'api_key': self.monitor_widget.api_key_input.text().strip()
        }
        
        return {
            'accounts': self.get_accounts_settings(),
            'tasks': self.tasks,
            'task_settings': task_settings
        }
    
    def get_accounts_settings(self):
        """계정 설정 정보 반환 - 기본 정보만 저장"""
        accounts_data = {}
        for account_id, account_info in self.accounts.items():
            accounts_data[account_id] = {
                'pw': account_info['pw']
                # cafe_list는 저장하지 않음
                # headers는 저장하지 않음 (보안 이슈)
            }
        return accounts_data
    
    def apply_settings(self, settings_data):
        """불러온 설정 적용"""
        # 계정 정복 전에 로그인 필요 여부 확인
        accounts_to_login = []
        
        if 'accounts' in settings_data:
            # 첫 번째 계정만 처리 (단일 계정만 지원)
            first_account_id = None
            first_account_pw = None
            
            for account_id, account_info in settings_data['accounts'].items():
                # 첫 번째 계정만 저장하고 나머지는 무시
                if first_account_id is None:
                    first_account_id = account_id
                    first_account_pw = account_info['pw']
                    break
                    
            if first_account_id:
                # 첫 번째 계정이 이미 있는지 확인
                if first_account_id in self.accounts:
                    # 헤더 정보가 유효한지 확인
                    if not self.is_header_valid(self.accounts[first_account_id].get('headers', {})):
                        accounts_to_login.append((first_account_id, first_account_pw))
                else:
                    # 새 계정은 로그인 필요
                    accounts_to_login.append((first_account_id, first_account_pw))
        
        # 로그인이 필요한 계정이 있으면 사용자에게 알림
        if accounts_to_login:
            accounts_str = "\n".join([f"• {acc[0]}" for acc in accounts_to_login])
            reply = QMessageBox.question(
                self,
                '계정 로그인 필요',
                f'계정의 로그인이 필요합니다:\n\n{accounts_str}\n\n'
                f'로그인을 진행하시겠습니까? (설정 불러오기를 완료하려면 필요합니다)',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.No:
                return False  # 설정 적용 취소
        
        # 기존 데이터 초기화
        old_accounts = self.accounts.copy()
        self.accounts = {}
        self.tasks = []
        
        # 계정 정복 전에 로그인 필요 여부 확인
        accounts_to_login = []
        
        if 'accounts' in settings_data:
            for account_id, account_info in settings_data['accounts'].items():
                # 로그인이 필요한 계정인지 확인
                if account_id not in self.accounts or self.accounts[account_id]['headers'] is None:
                    accounts_to_login.append((account_id, account_info['pw']))
        
        # 로그인이 필요한 계정이 있으면 사용자에게 알림
        if accounts_to_login:
            self.log.info(f"계정에 대해 로그인을 진행합니다...")
            
            # 로그인 진행 상태 대화상자
            progress_dialog = QProgressDialog("계정 로그인 중입니다...", "취소", 0, 1, self)
            progress_dialog.setWindowTitle("로그인 진행 중")
            progress_dialog.setWindowModality(Qt.WindowModal)
            progress_dialog.setAutoClose(True)
            progress_dialog.setAutoReset(True)
            progress_dialog.setCancelButton(None)  # 취소 버튼 비활성화
            progress_dialog.setMinimumDuration(0)  # 즉시 표시
            progress_dialog.show()
            
            login_success_count = 0
            
            # 로그인 진행
            for account_id, password in accounts_to_login:
                auth = NaverAuth()
                auth.set_credentials(account_id, password)
                success, headers = auth.login()
                
                if success:
                    # 로그인 성공 시 헤더 정보 업데이트
                    self.accounts[account_id] = {
                        'pw': password,
                        'headers': headers
                    }
                    self.log.info(f"계정 '{account_id}' 로그인 성공")
                    login_success_count += 1
                else:
                    self.log.error(f"계정 '{account_id}' 로그인 실패")
            
            # 진행 대화상자 완료 및 닫기
            progress_dialog.setValue(1)
            progress_dialog.close()
            
            # 로그인 결과 알림
            if login_success_count > 0:
                QMessageBox.information(
                    self,
                    '로그인 완료',
                    f'계정의 로그인이 완료되었습니다.'
                )
            else:
                QMessageBox.warning(
                    self,
                    '로그인 실패',
                    f'계정의 로그인에 실패했습니다.\n'
                    f'해당 계정은 수동으로 다시 로그인해주세요.'
                )
        
        # 작업 목록 복원
        if 'tasks' in settings_data:
            self.tasks = settings_data['tasks']
            self.update_task_list()
            
        # 작업 설정 적용
        if 'task_settings' in settings_data:
            task_settings = settings_data['task_settings']
            # 모니터 위젯에 설정 적용
            self.monitor_widget.load_settings(task_settings)
        
        self.log.info("설정이 성공적으로 적용되었습니다.")
        return True

    def on_login_progress(self, message, color):
        """로그인 진행상황 업데이트"""
        self.log.add_log(message, color)
        self.monitor_widget.add_log_message({'message': message, 'color': color})
    
    def on_account_login_finished(self, success, headers, account_id):
        """계정 선택 시 로그인 완료 처리"""
        if success:
            # 계정 정보에 헤더 설정
            self.accounts[account_id]['headers'] = headers
            
            # 카페 목록 로드
            self.load_cafe_list(account_id, headers)
            
            self.log.info(f'계정 {account_id} 로그인 성공')
        else:
            self.log.error(f'계정 {account_id} 로그인 실패')
            QMessageBox.warning(self, '로그인 실패', f'계정 "{account_id}"의 로그인에 실패했습니다.\n다른 계정을 선택해주세요.')

    def add_account_to_list(self, account_id, password):
        """계정 목록에 계정 추가 (단일 계정만 관리)"""
        # 기존 계정 정보 초기화 (단일 계정만 관리하므로 모든 계정 삭제)
        self.accounts = {}
        
        # 새 계정 정보 설정
        self.accounts[account_id] = {
            'pw': password,
            'headers': None,
            'cafe_list': []
        }
        
        self.log.info(f'계정 설정됨: {account_id}')

    def on_login_success(self, headers):
        """로그인 성공 시 호출 (AccountWidget에서 발생한 시그널)"""
        # 현재 계정 ID 가져오기
        account_id = self.account_widget.current_account
        
        if account_id:
            # 계정 정보에 헤더 설정
            if account_id in self.accounts:
                self.accounts[account_id]['headers'] = headers
                self.log.info(f'계정 로그인 성공: {account_id}')
            else:
                # 계정이 없는 경우 새로 추가
                self.accounts[account_id] = {
                    'pw': '',  # 비밀번호는 저장하지 않음
                    'headers': headers
                }
                self.log.info(f'새 계정 추가 및 로그인 성공: {account_id}')
            
            # 작업 수행 가능 상태로 UI 업데이트
            # self.monitor_widget.add_log_message({
            #     'message': f'계정 {account_id} 로그인 성공. 이제 작업을 추가할 수 있습니다.',
            #     'color': 'green'
            # })

    def on_task_error(self, task, error_msg):
        """작업 오류 발생 시 호출되는 메서드"""
        # 작업 오류 로그 추가
        self.monitor_widget.add_log_message({
            'message': f"작업 오류: ID {task.get('id', '알 수 없음')}, 상태: {task.get('status', '알 수 없음')}",
            'color': 'red'
        })
        
        # 오류 메시지 로깅
        self.monitor_widget.add_log_message({
            'message': f"오류 내용: {error_msg}",
            'color': 'red'
        })
        
        # 작업 상태 로깅 (모든 작업 완료 여부 확인은 Worker에서 처리)
        task_id = task.get('id', '알 수 없음')
        task_status = task.get('status', '알 수 없음')
        
        self.monitor_widget.add_log_message({
            'message': f"작업 #{task_id} 상태 변경: {task_status}",
            'color': 'blue'
        })

    def on_log_message(self, message_data):
        """Worker에서 전송한 로그 메시지 처리"""
        self.monitor_widget.add_log_message(message_data)
        
    def on_post_completed(self, post_info):
        """댓글 등록 완료 시 호출되는 메서드
        
        Args:
            post_info (dict): 댓글 정보
                - timestamp (str): 작업 시간
                - account_id (str): 계정 ID
                - content (str): 댓글 내용
                - url (str): 게시글 URL
        """
        # 댓글 정보 로그 추가
        self.on_log_message({
            'message': f"📝 댓글 등록 완료: {post_info.get('account_id')} - {post_info.get('content', '')[:30]}...",
            'color': 'green'
        })
        
        # 모니터 위젯에 댓글 정보 추가
        try:
            # 현재 테이블에 행 추가
            row = self.monitor_widget.task_monitor.rowCount()
            self.monitor_widget.task_monitor.insertRow(row)
            
            # 아이템 생성
            no_item = QTableWidgetItem(str(row + 1))
            id_item = QTableWidgetItem(post_info.get('account_id', ''))
            content_item = QTableWidgetItem(post_info.get('content', ''))
            url_item = QTableWidgetItem(post_info.get('url', ''))
            
            # 아이템 설정
            self.monitor_widget.task_monitor.setItem(row, 0, no_item)
            self.monitor_widget.task_monitor.setItem(row, 1, id_item)
            self.monitor_widget.task_monitor.setItem(row, 2, content_item)
            self.monitor_widget.task_monitor.setItem(row, 3, url_item)
            
            # 새로 추가된 행으로 스크롤
            self.monitor_widget.task_monitor.scrollToBottom()
        except Exception as e:
            self.on_log_message({
                'message': f"모니터 위젯에 댓글 정보 추가 중 오류 발생: {str(e)}",
                'color': 'red'
            })

    def set_ai_api_key(self, api_key):
        """AI API 키 설정
        
        Args:
            api_key (str): API 키
        """
        self.ai_api_key = api_key
        self.log.info("AI API 키가 설정되었습니다.")

    def on_next_task_info(self, info):
        """다음 작업 정보 수신 시 호출되는 메서드
        
        Args:
            info (dict): 다음 작업 정보
                - next_task_number (int): 다음 작업 번호
                - next_execution_time (str): 다음 실행 시간
                - wait_time (str): 대기 시간
                - current_task (dict): 현재 작업 정보
                    - task_id (str): 작업 ID
                    - cafe_name (str): 카페 이름
                    - board_name (str): 게시판 이름
                    - article_title (str): 게시글 제목
                    - article_id (str): 게시글 ID
                    - account_id (str): 계정 ID
                    - progress (str): 진행 상황
                    - action (str): 작업 종류
        """
        # 모니터 위젯에 다음 작업 정보 표시
        self.monitor_widget.update_next_task_info(info)

    def on_all_tasks_completed(self, is_normal_completion):
        """모든 작업이 완료되었을 때 호출되는 메서드
        
        Args:
            is_normal_completion (bool): 정상 완료 여부 (True: 정상 완료, False: 중간 중지)
        """
        # 작업 완료 로그 추가
        if is_normal_completion:
            self.monitor_widget.add_log_message({
                'message': "[작업 완료] 모든 작업이 정상적으로 완료되었습니다.",
                'color': 'green'
            })
            
            # 작업 반복 모드 확인
            repeat_mode = self.monitor_widget.repeat_checkbox.isChecked()
            self.log.info(f"작업 반복 모드: {repeat_mode}")
            
            # 작업 리스트가 비어있는지 확인
            if repeat_mode and self.tasks:
                self.log.info("작업 반복 모드가 활성화되어 있습니다. 작업을 다시 시작합니다.")
                
                # Worker 상태 정리
                if hasattr(self, 'worker'):
                    self.log.info("기존 Worker 객체를 정리합니다.")
                    self.worker.is_running = False
                    if self.worker.isRunning():
                        self.worker.wait(1000)
                    del self.worker
                
                # 대기 시간 계산 (5초 후 재시작)
                wait_time = 5
                self.log.info(f"{wait_time}초 후 작업을 다시 시작합니다.")
                self.monitor_widget.add_log_message({
                    'message': f"[작업 반복] {wait_time}초 후 작업을 다시 시작합니다.",
                    'color': 'blue'
                })
                
                # 타이머를 사용하여 일정 시간 후 작업 재시작
                QTimer.singleShot(wait_time * 1000, self.restart_tasks)
                return
            elif repeat_mode and not self.tasks:
                self.log.info("작업 반복 모드가 활성화되어 있지만, 작업 리스트가 비어있어 재시작하지 않습니다.")
                self.monitor_widget.add_log_message({
                    'message': "[작업 반복 중지] 작업 리스트가 비어있어 반복 실행을 중지합니다.",
                    'color': 'red'
                })
        else:
            self.monitor_widget.add_log_message({
                'message': "[작업 중지] 작업이 중간에 중지되었습니다.",
                'color': 'yellow'
            })
        
        # Worker 상태 업데이트 및 정리
        if hasattr(self, 'worker'):
            self.log.info("Worker 상태를 False로 설정하고 정리합니다.")
            self.worker.is_running = False
            
            # Worker 스레드가 실행 중인 경우 대기
            if self.worker.isRunning():
                self.log.info("Worker 스레드가 종료될 때까지 대기합니다.")
                self.worker.wait(1000)  # 최대 1초 대기
                
            # Worker 객체 정리
            self.log.info("Worker 객체를 정리합니다.")
            if hasattr(self, 'worker'):
                del self.worker
        
        # 실행 버튼 상태 변경 (이미 변경되지 않은 경우에만)
        if self.monitor_widget.is_running:
            self.log.info("실행 버튼으로 변경합니다.")
            self.monitor_widget.is_running = False  # 직접 상태 변경
            self.monitor_widget.execute_btn.setText("실행")
            self.monitor_widget.execute_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 10px;
                    font-size: 14px;
                    min-height: 40px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            self.log.info(f"버튼 상태 변경 완료: is_running = {self.monitor_widget.is_running}")
        else:
            self.log.info("버튼이 이미 실행 상태입니다. 상태 변경이 필요하지 않습니다.")
            
        # 다음 작업 정보 초기화
        self.monitor_widget.next_task_label.setText("대기 중...")
        self.log.info("다음 작업 정보가 초기화되었습니다.")

    def restart_tasks(self):
        """작업을 다시 시작하는 메서드 (작업 반복 모드에서 사용)"""
        self.log.info("작업을 다시 시작합니다.")
        
        # 작업 리스트가 비어있는지 확인
        if not self.tasks:
            self.log.info("작업 리스트가 비어있어 재시작하지 않습니다.")
            self.monitor_widget.add_log_message({
                'message': "[작업 반복 중지] 작업 리스트가 비어있어 반복 실행을 중지합니다.",
                'color': 'red'
            })
            
            # 실행 버튼 상태가 실행 상태인 경우 중지 상태로 변경
            if self.monitor_widget.is_running:
                self.log.info("버튼 상태를 중지 상태로 변경합니다.")
                self.monitor_widget.is_running = False  # 직접 상태 변경
                self.monitor_widget.execute_btn.setText("실행")
                self.monitor_widget.execute_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 10px;
                        font-size: 14px;
                        min-height: 40px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
                self.log.info(f"버튼 상태 변경 완료: is_running = {self.monitor_widget.is_running}")
            return
        
        # 버튼이 이미 실행 상태인 경우 중지 상태로 변경
        if not self.monitor_widget.is_running:
            self.log.info("버튼 상태를 실행 상태로 변경합니다.")
            # toggle_execution 호출하지 않고 버튼 상태 직접 변경
            self.monitor_widget.is_running = True
            self.monitor_widget.execute_btn.setText("중지")
            self.monitor_widget.execute_btn.setStyleSheet("""
                QPushButton {
                    background-color: #d65c5c;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 10px;
                    font-size: 14px;
                    min-height: 40px;
                }
                QPushButton:hover {
                    background-color: #b84a4a;
                }
            """)
        
        # 작업 실행
        self.run_tasks(True)

    def add_task(self):
        """작업 추가"""
        # 현재 로그인된 계정이 있는지 확인
        account_id = self.account_widget.current_account
        
        if not account_id:
            QMessageBox.warning(self, '경고', '계정을 먼저 로그인해주세요.')
            return
            
        # 선택된 계정 로그인 확인
        if account_id not in self.accounts or self.accounts[account_id]['headers'] is None:
            QMessageBox.warning(self, '경고', '계정이 로그인되지 않았습니다.\n로그인 후 다시 시도해주세요.')
            return
        
        # 작업 ID 생성
        task_id = len(self.tasks) + 1
        
        # 작업 정보 생성
        task_info = {
            'id': task_id,
            'account_id': account_id,  # 주 계정 ID
            'status': '대기 중',
            'progress': 0,
            'completed_count': 0,
            'error_count': 0,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 작업 목록에 추가
        self.tasks.append(task_info)
        
        # 작업 목록 UI 업데이트
        self.update_task_list()
        
        # 로그 메시지
        msg = f'작업 추가됨: 계정 {account_id}'
        self.log.info(msg)
        self.monitor_widget.add_log_message({'message': msg, 'color': 'blue'})
        
        # 작업 추가 성공 메시지
        QMessageBox.information(self, '작업 추가 완료', f'작업 #{task_id}이(가) 성공적으로 추가되었습니다.')

    def save_settings(self):
        """설정 저장"""
        # 설정 가져오기
        settings = self.get_all_settings()
        
        # 설정 저장 대화상자 표시
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "설정 저장", 
            "", 
            "JSON 파일 (*.json)"
        )
        
        if not filename:
            return
            
        try:
            import json
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
                
            self.log.info(f"설정이 저장되었습니다: {filename}")
            QMessageBox.information(self, "알림", "설정이 저장되었습니다.")
        except Exception as e:
            self.log.error(f"설정 저장 중 오류 발생: {str(e)}")
            QMessageBox.warning(self, "오류", f"설정 저장 중 오류가 발생했습니다:\n{str(e)}")
    
    def load_settings(self):
        """설정 불러오기"""
        # 설정 파일 선택 대화상자 표시
        filename, _ = QFileDialog.getOpenFileName(
            self, 
            "설정 불러오기", 
            "", 
            "JSON 파일 (*.json)"
        )
        
        if not filename:
            return
            
        try:
            import json
            with open(filename, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            # 설정 적용
            self.apply_settings(settings)
            
            self.log.info(f"설정이 로드되었습니다: {filename}")
            QMessageBox.information(self, "알림", "설정이 로드되었습니다.")
        except Exception as e:
            self.log.error(f"설정 로드 중 오류 발생: {str(e)}")
            QMessageBox.warning(self, "오류", f"설정 로드 중 오류가 발생했습니다:\n{str(e)}")
    
    def reset_settings(self):
        """설정 초기화"""
        # 확인 대화상자 표시
        reply = QMessageBox.question(
            self, 
            "설정 초기화", 
            "모든 설정을 초기화하시겠습니까?\n이 작업은 되돌릴 수 없습니다.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 작업 설정 초기화
            self.monitor_widget.min_interval.setValue(5)
            self.monitor_widget.max_interval.setValue(15)
            self.monitor_widget.repeat_checkbox.setChecked(True)
            self.monitor_widget.ip_tethering_checkbox.setChecked(False)
            self.monitor_widget.api_key_input.clear()
            
            self.log.info("설정이 초기화되었습니다.")
            QMessageBox.information(self, "알림", "설정이 초기화되었습니다.")

    def remove_task(self):
        """선택된 작업 삭제"""
        if not self.monitor_widget.task_list.currentItem():
            QMessageBox.warning(self, '경고', '삭제할 작업을 선택해주세요.')
            return
            
        current_item = self.monitor_widget.task_list.currentItem()
        task_idx = self.monitor_widget.task_list.currentRow()
        
        # 작업 ID 확인 (UserRole에 저장된 데이터)
        task_id = current_item.data(Qt.UserRole)
        
        # ID로 작업 찾기
        task_to_remove = None
        for i, task in enumerate(self.tasks):
            if task['id'] == task_id:
                task_to_remove = i
                break
        
        if task_to_remove is not None:
            # 작업 정보 저장
            removed_task = self.tasks[task_to_remove]
            account_id = removed_task['account_id']
            
            # 작업 삭제
            self.tasks.pop(task_to_remove)
            
            # 작업 목록 업데이트
            self.update_task_list()
            
            # 로그 메시지
            msg = f'작업 #{task_id} 삭제됨: 계정 {account_id}'
            self.log.info(msg)
            self.monitor_widget.add_log_message({'message': msg, 'color': 'blue'})

    def validate_api_key(self):
        """API 키 검증"""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            QMessageBox.warning(self, "API 키 검증", "API 키를 입력해주세요.")
            return
        
        # 검증 중 UI 업데이트
        self.validate_api_btn.setEnabled(False)
        self.api_key_status.setText("검증 중...")
        self.api_key_status.setStyleSheet("color: #5c85d6;")
        
        try:
            ai_generator = AIGenerator(api_key=api_key)
            is_valid, message = ai_generator.validate_api_key()
            
            if is_valid:
                self.api_key_status.setText("✓ 유효한 키")
                self.api_key_status.setStyleSheet("color: #4CAF50;")
                self.log.info("API 키 검증 성공: " + message)
                
                # API 키 설정
                self.set_ai_api_key(api_key)
            else:
                self.api_key_status.setText("✗ 유효하지 않음")
                self.api_key_status.setStyleSheet("color: #d65c5c;")
                self.log.error("API 키 검증 실패: " + message)
                QMessageBox.warning(self, "API 키 검증 실패", message)
        except Exception as e:
            self.api_key_status.setText("✗ 오류 발생")
            self.api_key_status.setStyleSheet("color: #d65c5c;")
            error_msg = f"API 키 검증 중 오류 발생: {str(e)}"
            self.log.error(error_msg)
            QMessageBox.critical(self, "API 키 검증 오류", error_msg)
        
        # 검증 완료 후 UI 업데이트
        self.validate_api_btn.setEnabled(True)

    def run_tasks(self, is_manual_run):
        """작업을 실행하는 메서드"""
        self.log.info("작업을 실행합니다.")
        
        # 작업 실행 전 상태 체크
        if not self.monitor_widget.is_running:
            self.log.info("작업을 실행할 수 있는 상태입니다.")
            
            # 작업 실행
            self.monitor_widget.is_running = True
            self.monitor_widget.execute_btn.setText("중지")
            self.monitor_widget.execute_btn.setStyleSheet("""
                QPushButton {
                    background-color: #d65c5c;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 10px;
                    font-size: 14px;
                    min-height: 40px;
                }
                QPushButton:hover {
                    background-color: #b84a4a;
                }
            """)
            
            self.log.info("작업이 성공적으로 실행되었습니다.")
        else:
            self.log.info("작업이 이미 실행 중입니다. 상태 변경이 필요하지 않습니다.")