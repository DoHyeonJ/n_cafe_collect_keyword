from PyQt5.QtWidgets import (QWidget, QLabel, QTableWidget, QVBoxLayout, 
                           QTableWidgetItem, QGroupBox, QHeaderView)
from PyQt5.QtCore import pyqtSlot, QVariant, QUrl, Qt
from PyQt5.QtGui import QDesktopServices
from ..utils.log import Log
from .styles import DARK_STYLE

class BaseMonitorWidget(QWidget):
    def __init__(self, log: Log):
        super().__init__()
        self.log = log
        
        # task_monitor 초기화 (상단 모니터)
        self.task_monitor = QTableWidget(0, 4)  # 4개의 컬럼 (NO, 아이디, 내용, URL)
        self.task_monitor.setHorizontalHeaderLabels(["NO", "제목", "내용", "URL"])
        
        # URL 클릭 이벤트 연결
        self.task_monitor.itemClicked.connect(self.on_item_clicked)
        
        # 컬럼 너비 설정
        header = self.task_monitor.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # NO
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 제목
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # 내용
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # URL
        
        self.task_monitor.setColumnWidth(0, 50)  # NO
        self.task_monitor.setColumnWidth(1, 150)  # 제목
        self.task_monitor.setColumnWidth(2, 150)  # 내용
        self.task_monitor.setColumnWidth(3, 150)  # URL
        
        # 가로 스크롤바 숨기기
        self.task_monitor.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 테이블 스타일 설정
        self.task_monitor.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                gridline-color: #3d3d3d;
            }
            QTableWidget::item {
                padding: 5px;
                border: none;
            }
            QTableWidget::item:hover {
                text-decoration: underline;
                cursor: pointer;
            }
            QHeaderView::section {
                background-color: #353535;
                padding: 5px;
                border: 1px solid #3d3d3d;
                color: white;
                font-weight: bold;
            }
            QTableCornerButton::section {
                background-color: #353535;
                border: 1px solid #3d3d3d;
            }
        """)
        
        # 여백 제거
        self.task_monitor.setContentsMargins(0, 0, 0, 0)
        
        # log_monitor 초기화 (하단 모니터)
        self.log_monitor = QTableWidget(0, 2)  # 2개의 컬럼 (시간, 메시지)
        self.log_monitor.setHorizontalHeaderLabels(["시간", "메시지"])
        
        # 컬럼 너비 설정
        log_header = self.log_monitor.horizontalHeader()
        log_header.setSectionResizeMode(0, QHeaderView.Fixed)  # 시간
        log_header.setSectionResizeMode(1, QHeaderView.Stretch)  # 메시지
        self.log_monitor.setColumnWidth(0, 180)  # 시간 컬럼 너비 조정
        
        # 가로 스크롤바 숨기기
        self.log_monitor.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def on_item_clicked(self, item):
        """테이블 아이템 클릭 이벤트 처리"""
        if item.column() == 3:  # URL 열인 경우
            url = item.text()
            if url:
                QDesktopServices.openUrl(QUrl(url))

    @pyqtSlot(QVariant)
    def add_task_monitor_row(self, data):
        """댓글 모니터에 새로운 행을 추가합니다.
        
        Args:
            data (dict): 모니터링 데이터
                - timestamp (str): 작업 시간
                - account_id (str): 계정 ID
                - content (str): 댓글 내용
                - url (str): 게시글 URL
        """
        # 새로운 행 추가
        current_row = self.task_monitor.rowCount()
        self.task_monitor.insertRow(current_row)
        
        # 데이터 설정
        self.task_monitor.setItem(current_row, 0, QTableWidgetItem(str(current_row + 1)))  # NO
        self.task_monitor.setItem(current_row, 1, QTableWidgetItem(data['account_id']))
        self.task_monitor.setItem(current_row, 2, QTableWidgetItem(data['content']))
        self.task_monitor.setItem(current_row, 3, QTableWidgetItem(data['url']))
        
        # 스크롤을 최신 항목으로 이동
        self.task_monitor.scrollToBottom()

class ScriptMonitorWidget(BaseMonitorWidget):
    def __init__(self, log: Log):
        super().__init__(log)
        self.init_ui()

    def init_ui(self):
        group_box = QGroupBox()
        layout = QVBoxLayout()

        # 게시글 수집 모니터
        self.board_monitor_label = QLabel('게시글 수집 모니터')
        self.board_monitor = QTableWidget(0, 5)
        self.board_monitor.setHorizontalHeaderLabels(
            ["수집시간", "카페ID", "게시글ID", "게시글 제목", "작성자"]
        )
        
        # 게시글 생성 모니터 - 헤더 변경
        self.task_monitor_label = QLabel('댓글 생성 모니터')
        self.task_monitor = QTableWidget(0, 4)  # 컬럼 수를 4개로 변경
        self.task_monitor.setHorizontalHeaderLabels(
            ["시간", "아이디", "내용", "URL"]
        )

        # 컬럼 너비 설정
        self.setup_column_widths()

        layout.addWidget(self.board_monitor_label)
        layout.addWidget(self.board_monitor)
        layout.addWidget(self.task_monitor_label)
        layout.addWidget(self.task_monitor)
        
        group_box.setLayout(layout)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(group_box)
        self.setLayout(main_layout)

    def setup_column_widths(self):
        # 게시글 수집 모니터 컬럼 너비 설정
        board_header = self.board_monitor.horizontalHeader()
        board_header.setSectionResizeMode(0, QHeaderView.Fixed)  # 수집시간
        board_header.setSectionResizeMode(1, QHeaderView.Fixed)  # 카페ID
        board_header.setSectionResizeMode(2, QHeaderView.Fixed)  # 게시글ID
        board_header.setSectionResizeMode(3, QHeaderView.Stretch)  # 게시글 제목
        board_header.setSectionResizeMode(4, QHeaderView.Fixed)  # 작성자
        
        self.board_monitor.setColumnWidth(0, 150)  # 수집시간
        self.board_monitor.setColumnWidth(1, 80)   # 카페ID
        self.board_monitor.setColumnWidth(2, 80)   # 게시글ID
        self.board_monitor.setColumnWidth(4, 100)  # 작성자

        # 게시글 생성 모니터 컬럼 너비 설정 - 새로운 컬럼 구조에 맞게 수정
        task_header = self.task_monitor.horizontalHeader()
        task_header.setSectionResizeMode(0, QHeaderView.Fixed)  # 시간
        task_header.setSectionResizeMode(1, QHeaderView.Fixed)  # 아이디
        task_header.setSectionResizeMode(2, QHeaderView.Stretch)  # 내용
        task_header.setSectionResizeMode(3, QHeaderView.Fixed)  # URL
        
        self.task_monitor.setColumnWidth(0, 180)  # 시간 (2025-02-27 12:31:15 포맷이 다 보이도록)
        self.task_monitor.setColumnWidth(1, 100)  # 아이디
        self.task_monitor.setColumnWidth(3, 200)  # URL

class RoutineMonitorWidget(BaseMonitorWidget):
    def __init__(self, log: Log):
        super().__init__(log)
        self.init_ui()

    def init_ui(self):
        # 게시글 모니터 테이블 (task_monitor)
        self.task_monitor = QTableWidget(0, 4)
        self.task_monitor.setHorizontalHeaderLabels(
            ["NO", "아이디", "내용", "URL"]
        )
        
        # 테이블 헤더 설정
        task_header = self.task_monitor.horizontalHeader()
        task_header.setSectionResizeMode(0, QHeaderView.Fixed)  # NO
        task_header.setSectionResizeMode(1, QHeaderView.Fixed)  # 아이디
        task_header.setSectionResizeMode(2, QHeaderView.Stretch)  # 내용
        task_header.setSectionResizeMode(3, QHeaderView.Fixed)  # URL
        
        self.task_monitor.setColumnWidth(0, 50)  # NO
        self.task_monitor.setColumnWidth(1, 100)  # 아이디
        self.task_monitor.setColumnWidth(3, 150)  # URL
        
        # 가로 스크롤바 숨기기
        self.task_monitor.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 작업로그 모니터
        self.log_monitor = QTableWidget(0, 2)
        self.log_monitor.setHorizontalHeaderLabels(
            ["NO", "메시지"]
        )

        # 컬럼 너비 설정
        log_header = self.log_monitor.horizontalHeader()
        log_header.setSectionResizeMode(0, QHeaderView.Fixed)  # NO
        log_header.setSectionResizeMode(1, QHeaderView.Stretch)  # 메시지
        self.log_monitor.setColumnWidth(0, 50)  # NO
        
        # 가로 스크롤바 숨기기
        self.log_monitor.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        group_box = QGroupBox()
        layout = QVBoxLayout()
        layout.addWidget(self.task_monitor)
        layout.addWidget(self.log_monitor)
        
        group_box.setLayout(layout)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(group_box)
        self.setLayout(main_layout) 