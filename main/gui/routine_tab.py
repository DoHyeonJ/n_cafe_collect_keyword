from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QGroupBox, QLabel, 
                           QListWidget, QSpinBox, QLineEdit, QTableWidget, QHeaderView, QTableWidgetItem, QTabWidget, QCheckBox, QTextEdit, QMessageBox, QFileDialog)
from .monitor_widget import RoutineMonitorWidget, BaseMonitorWidget
from .styles import DARK_STYLE
from datetime import datetime
from PyQt5.QtCore import Qt, pyqtSignal
from ..api.ai_generator import AIGenerator
from ..api.ip_manage import change_ip, get_current_ip, is_tethering_enabled, toggle_usb_tethering
from ..utils.log import Log
import pandas as pd

class RoutineTab(BaseMonitorWidget):
    execute_tasks_clicked = pyqtSignal(bool)  # 작업 실행/정지 시그널, 실행 상태를 전달
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.is_running = False  # 실행 상태
        self.api_key_validated = False  # API 키 검증 상태
        self.main_window = None  # MainWindow 인스턴스 저장
        self.worker = None  # Worker 인스턴스 저장
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # 다음 작업 정보 표시 영역 추가
        # next_task_info = QGroupBox("다음 작업 정보")
        # next_task_layout = QHBoxLayout()
        
        self.next_task_label = QLabel("대기 중...")
        self.next_task_label.setStyleSheet("""
            QLabel {
                color: #5c85d6;
                font-size: 13px;
                padding: 10px;
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
            }
        """)
        
        # next_task_layout.addWidget(self.next_task_label)
        # next_task_info.setLayout(next_task_layout)
        
        # 탭 위젯 (상단)
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
                background: #2b2b2b;
            }
            QTabBar::tab {
                background: #353535;
                color: #cccccc;
                padding: 5px 10px;  /* 탭 크기 축소 */
                border: 1px solid #3d3d3d;
                border-bottom: none;
                min-width: 80px;  /* 최소 너비 설정 */
                max-width: 120px;  /* 최대 너비 설정 */
            }
            QTabBar::tab:selected {
                background: #2b2b2b;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: #404040;
            }
        """)
        
        # 2. 게시글 모니터 탭
        post_monitor_tab = QWidget()
        post_layout = QVBoxLayout()
        
        # 버튼 컨테이너 추가
        button_container = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 10)  # 아래쪽 여백만 추가
        
        # 엑셀 다운로드 버튼
        self.excel_btn = QPushButton("엑셀 다운로드")
        self.excel_btn.setStyleSheet("""
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
        self.excel_btn.clicked.connect(self.export_to_excel)
        
        # 수집 초기화 버튼
        self.clear_btn = QPushButton("수집 초기화")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #d65c5c;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #b84a4a;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_monitor)
        
        button_layout.addWidget(self.excel_btn)
        button_layout.addStretch()  # 중간 공간을 채우기 위한 stretch
        button_layout.addWidget(self.clear_btn)
        button_container.setLayout(button_layout)
        
        # 레이아웃에 버튼 컨테이너와 모니터 추가
        post_layout.addWidget(button_container)
        post_layout.addWidget(self.task_monitor)
        post_monitor_tab.setLayout(post_layout)
        
        # 3. 공지사항 탭
        notice_tab = QWidget()
        notice_layout = QVBoxLayout()
        notice_text = QTextEdit()
        notice_text.setReadOnly(True)
        notice_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: white;
                border: none;
            }
        """)
        notice_layout.addWidget(notice_text)
        notice_tab.setLayout(notice_layout)
        
        # 4. 기간연장/문의 탭
        support_tab = QWidget()
        support_layout = QVBoxLayout()
        
        contact_info = QLabel("""
            기간연장 및 문의사항은 아래로 연락주세요:
            
            카카오톡: @example
            이메일: support@example.com
            전화: 010-1234-5678
        """)
        contact_info.setStyleSheet("color: white; padding: 20px;")
        contact_info.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        support_layout.addWidget(contact_info)
        support_tab.setLayout(support_layout)
        
        # 탭 추가
        tab_widget.addTab(post_monitor_tab, "작업 모니터")
        tab_widget.addTab(notice_tab, "공지사항")
        tab_widget.addTab(support_tab, "기간연장/문의")
        
        # 로그 모니터 - BaseMonitorWidget에서 상속받은 log_monitor 직접 사용
        self.log_monitor.setMinimumHeight(70)
        self.log_monitor.setMaximumHeight(120)
        
        # 로그 모니터 스타일 개선
        log_monitor_style = """
            QTableWidget {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                gridline-color: #3d3d3d;
            }
            QTableWidget::item {
                padding: 5px;
                border: none;
                min-height: 25px;
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
        """
        self.log_monitor.setStyleSheet(log_monitor_style)
        
        # 실행 버튼
        self.execute_btn = QPushButton("실행")
        self.execute_btn.setFixedHeight(40)  # 높이 고정
        self.execute_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.execute_btn.clicked.connect(self.toggle_execution)
        
        # 메인 레이아웃 구성
        layout.addWidget(tab_widget)
        #layout.addWidget(next_task_info)
        layout.addWidget(self.log_monitor)
        layout.addWidget(self.execute_btn)
        self.setLayout(layout)

    def set_main_window(self, main_window):
        """MainWindow 인스턴스 설정
        
        Args:
            main_window: MainWindow 인스턴스
        """
        self.main_window = main_window
        # worker 속성이 있을 때만 설정 (초기화 시점에는 없을 수 있음)
        if hasattr(main_window, 'worker'):
            self.set_worker(main_window.worker)

    def set_worker(self, worker):
        """Worker 인스턴스 설정 및 시그널 연결
        
        Args:
            worker: Worker 인스턴스
        """
        self.worker = worker
        if worker:
            # IP 변경 시그널 연결
            worker.ip_changed.connect(self.update_ip_label)
            
    def update_ip_label(self, new_ip):
        """IP 레이블 업데이트
        
        Args:
            new_ip (str): 새 IP 주소
        """
        if hasattr(self, 'current_ip_label'):
            self.current_ip_label.setText(new_ip)

    def toggle_execution(self):
        """실행/중지 버튼 클릭 시 호출되는 메서드"""
        try:
            if not self.is_running:
                # 실행 시작 전 API 키 검증 확인
                api_key = self.api_key_input.text().strip()
                
                if not api_key:
                    QMessageBox.warning(self, "API 키 필요", "작업을 실행하기 전에 API 키를 입력해주세요.")
                    return
                    
                if not self.api_key_validated:
                    reply = QMessageBox.question(
                        self, 
                        "API 키 검증 필요", 
                        "API 키가 검증되지 않았습니다. 검증을 진행하시겠습니까?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes
                    )
                    
                    if reply == QMessageBox.Yes:
                        # API 키 검증 진행
                        self.validate_api_key()
                        # 검증 후에도 유효하지 않으면 실행 중단
                        if not self.api_key_validated:
                            return
                    else:
                        return
                
                # 작업 실행 버튼 클릭 로그 - 직접 콘솔에 출력하여 로그 재귀 호출 방지
                print("작업 실행 버튼이 클릭되었습니다.")
                print(f"작업 실행 상태 변경: is_running = {self.is_running} → True")
                
                # 실행 상태로 변경
                self.is_running = True
                self.execute_btn.setText("중지")
                self.execute_btn.setStyleSheet("""
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
                
                # 상태 변경 확인 로그 - 직접 콘솔에 출력
                print(f"버튼 상태 변경 후: is_running = {self.is_running}, 버튼 텍스트 = '중지'")
                
                # 실행 시그널 발생
                self.execute_tasks_clicked.emit(True)
                print("실행 시그널이 발생되었습니다.")
            else:
                # 작업 중지 버튼 클릭 로그 - 직접 콘솔에 출력
                print("작업 중지 버튼이 클릭되었습니다.")
                print(f"작업 실행 상태 변경: is_running = {self.is_running} → False")
                
                # 중지 상태로 변경
                self.is_running = False
                self.execute_btn.setText("실행")
                self.execute_btn.setStyleSheet("""
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
                
                # 상태 변경 확인 로그 - 직접 콘솔에 출력
                print(f"버튼 상태 변경 후: is_running = {self.is_running}, 버튼 텍스트 = '실행'")
                
                # 중지 시그널 발생
                self.execute_tasks_clicked.emit(False)
                print("중지 시그널이 발생되었습니다.")
        except Exception as e:
            # 예외 발생 시 콘솔에 출력
            print(f"toggle_execution 메서드 실행 중 오류 발생: {str(e)}")
            # 상태 초기화
            self.is_running = False
            self.execute_btn.setText("실행")
            self.execute_btn.setStyleSheet("""
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

    def show_monitor(self):
        self.log_monitor.setVisible(True)
        self.task_monitor.setVisible(True)

    def hide_monitor(self):
        self.log_monitor.setVisible(False)
        self.task_monitor.setVisible(False)

    def add_log_message(self, log_entry):
        """로그 메시지 추가 - RoutineMonitorWidget에 위임"""
        message = log_entry.get('message', '')
        color = log_entry.get('color', 'black')
        
        # 로그 테이블에 새 행 추가
        row = self.log_monitor.rowCount()
        self.log_monitor.insertRow(row)
        
        # 시간 아이템 생성
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_item = QTableWidgetItem(current_time)
        time_item.setForeground(Qt.gray)
        
        # 메시지 아이템 생성
        message_item = QTableWidgetItem(message)
        if color == "red":
            message_item.setForeground(Qt.red)
        elif color == "blue":
            message_item.setForeground(Qt.blue)
        elif color == "green":
            message_item.setForeground(Qt.green)
        else:
            message_item.setForeground(Qt.white)
        
        # 아이템 설정
        self.log_monitor.setItem(row, 0, time_item)
        self.log_monitor.setItem(row, 1, message_item)
        
        # 새로 추가된 행으로 스크롤
        self.log_monitor.scrollToBottom()

    def update_next_task_info(self, info):
        """다음 작업 정보 업데이트
        
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
        next_task_number = info.get('next_task_number', 0)
        next_execution_time = info.get('next_execution_time', '')
        wait_time = info.get('wait_time', '')
        current_task = info.get('current_task', {})
        
        # 현재 작업 정보 추출
        task_id = current_task.get('task_id', '')
        cafe_name = current_task.get('cafe_name', '')
        board_name = current_task.get('board_name', '')
        article_title = current_task.get('article_title', '')
        account_id = current_task.get('account_id', '')
        progress = current_task.get('progress', '')
        action = current_task.get('action', '')
        
        # 작업 정보 표시 텍스트 구성
        if action == '대기':
            # 대기 중인 경우
            if next_task_number > 0:
                self.next_task_label.setText(
                    f"다음 작업 #{next_task_number} - {next_execution_time} (대기: {wait_time})"
                )
            else:
                self.next_task_label.setText("대기 중...")
        else:
            # 작업 중인 경우
            task_info = f"작업 #{next_task_number}"
            if task_id:
                task_info += f" (ID: {task_id})"
            
            cafe_info = ""
            if cafe_name:
                cafe_info += f" | 카페: {cafe_name}"
            if board_name:
                cafe_info += f" | 게시판: {board_name}"
            
            article_info = ""
            if article_title:
                # 게시글 제목이 너무 길면 잘라내기
                if len(article_title) > 20:
                    article_title = article_title[:20] + "..."
                article_info += f" | 게시글: {article_title}"
            
            account_info = ""
            if account_id:
                account_info += f" | 계정: {account_id}"
            
            progress_info = ""
            if progress:
                progress_info += f" | {progress}"
            
            action_info = ""
            if action:
                action_info += f" | {action} 중"
            
            # 최종 텍스트 구성
            self.next_task_label.setText(
                f"{task_info}{cafe_info}{article_info}{account_info}{progress_info}{action_info} | 다음 실행: {next_execution_time}"
            )

    def get_settings(self):
        """현재 설정 정보 반환"""
        return {
            'min_interval': self.min_interval.value(),
            'max_interval': self.max_interval.value(),
            'repeat': self.repeat_checkbox.isChecked(),
            'use_ip_tethering': self.ip_tethering_checkbox.isChecked(),
            'api_key': self.api_key_input.text().strip()
        }

    def load_settings(self, settings):
        """설정값 로드"""
        if not settings:
            return
            
        self.min_interval.setValue(settings.get('min_interval', 5))
        self.max_interval.setValue(settings.get('max_interval', 15))
        self.repeat_checkbox.setChecked(settings.get('repeat', True))
        self.ip_tethering_checkbox.setChecked(settings.get('use_ip_tethering', False))
        self.api_key_input.setText(settings.get('api_key', ''))

    def on_ip_tethering_toggled(self, checked):
        """IP 테더링 체크박스 상태 변경 시 호출되는 메서드"""
        self.ip_status_container.setVisible(checked)
        self.validate_ip_btn.setEnabled(checked)
        
        if checked:
            # 현재 IP 표시
            self.update_current_ip()
            # 테더링 상태 확인
            if not is_tethering_enabled():
                reply = QMessageBox.question(
                    self, 
                    "테더링 활성화 필요", 
                    "테더링이 활성화되어 있지 않습니다. 활성화하시겠습니까?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    # 테더링 활성화 시도
                    tethering_enabled = toggle_usb_tethering(True)
                    
                    # 테더링 상태 확인 및 사용자에게 알림
                    if tethering_enabled:
                        QMessageBox.information(
                            self,
                            "테더링 활성화 성공",
                            "USB 테더링이 성공적으로 활성화되었습니다."
                        )
                        # IP 정보 업데이트
                        self.update_current_ip()
                    else:
                        QMessageBox.warning(
                            self,
                            "테더링 활성화 실패",
                            "USB 테더링 활성화에 실패했습니다.\n"
                            "기기 연결 상태와 권한을 확인해주세요."
                        )
                        # 체크박스 상태 되돌리기
                        self.ip_tethering_checkbox.setChecked(False)
                else:
                    self.ip_tethering_checkbox.setChecked(False)
        else:
            # 테더링 비활성화 시도
            if is_tethering_enabled():
                toggle_usb_tethering(False)
                self.log.info("USB 테더링이 비활성화되었습니다.")
        
        # 로그 메시지 추가
        self.log.info(f"IP 테더링 사용: {'활성화' if checked else '비활성화'}")
    
    def update_current_ip(self):
        """현재 IP 주소 업데이트"""
        try:
            current_ip = get_current_ip()
            self.current_ip_label.setText(current_ip)
            return current_ip
        except Exception as e:
            self.current_ip_label.setText("알 수 없음")
            self.log.error(f"IP 조회 중 오류 발생: {str(e)}")
            return None
    
    def validate_ip_change(self):
        """IP 변경 검증 버튼 클릭 시 호출되는 메서드"""
        # 검증 중 UI 업데이트
        self.validate_ip_btn.setEnabled(False)
        self.ip_status.setText("검증 중...")
        self.ip_status.setStyleSheet("color: #5c85d6;")
        
        try:
            # 테더링 상태 확인
            if not is_tethering_enabled():
                self.log.info("테더링이 활성화되어 있지 않습니다. 활성화를 시도합니다.")
                
                # 테더링 활성화 시도
                tethering_enabled = toggle_usb_tethering(True)
                
                if not tethering_enabled:
                    self.ip_status.setText("✗ 테더링 실패")
                    self.ip_status.setStyleSheet("color: #d65c5c;")
                    self.log.error("USB 테더링 활성화에 실패했습니다.")
                    QMessageBox.warning(
                        self, 
                        "테더링 활성화 실패", 
                        "USB 테더링 활성화에 실패했습니다.\n"
                        "기기 연결 상태와 권한을 확인해주세요."
                    )
                    self.validate_ip_btn.setEnabled(True)
                    return
                
                self.log.info("USB 테더링이 활성화되었습니다.")
            
            # IP 변경 시도
            is_changed, old_ip, new_ip = change_ip()
            
            # 현재 IP 업데이트
            self.current_ip_label.setText(new_ip)
            
            if is_changed:
                self.ip_status.setText("✓ 검증 완료")
                self.ip_status.setStyleSheet("color: #4CAF50;")
                self.log.info(f"IP 변경 성공: {old_ip} → {new_ip}")
            else:
                self.ip_status.setText("✗ 검증 실패")
                self.ip_status.setStyleSheet("color: #d65c5c;")
                self.log.error(f"IP 변경 실패: {old_ip} → {new_ip}")
                QMessageBox.warning(self, "IP 변경 실패", "IP 주소가 변경되지 않았습니다. 테더링 설정을 확인해주세요.")
        except Exception as e:
            self.ip_status.setText("✗ 오류 발생")
            self.ip_status.setStyleSheet("color: #d65c5c;")
            error_msg = f"IP 변경 중 오류 발생: {str(e)}"
            self.log.error(error_msg)
            QMessageBox.critical(self, "IP 변경 오류", error_msg)
        
        # 검증 완료 후 UI 업데이트
        self.validate_ip_btn.setEnabled(True)

    def validate_api_key(self):
        """API 키 검증 버튼 클릭 시 호출되는 메서드"""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            QMessageBox.warning(self, "API 키 검증", "API 키를 입력해주세요.")
            return
        
        # 검증 중 UI 업데이트
        self.validate_api_btn.setEnabled(False)
        self.api_key_status.setText("검증 중...")
        self.api_key_status.setStyleSheet("color: #5c85d6;")
        
        # API 키 검증
        try:
            ai_generator = AIGenerator(api_key=api_key)
            is_valid, message = ai_generator.validate_api_key()
            
            if is_valid:
                self.api_key_validated = True
                self.api_key_status.setText("✓ 유효한 키")
                self.api_key_status.setStyleSheet("color: #4CAF50;")
                self.log.info("API 키 검증 성공: " + message)
                
                # 메인 윈도우에 API 키 설정
                if self.main_window and hasattr(self.main_window, 'set_ai_api_key'):
                    self.main_window.set_ai_api_key(api_key)
            else:
                self.api_key_validated = False
                self.api_key_status.setText("✗ 유효하지 않음")
                self.api_key_status.setStyleSheet("color: #d65c5c;")
                self.log.error("API 키 검증 실패: " + message)
                QMessageBox.warning(self, "API 키 검증 실패", message)
        except Exception as e:
            self.api_key_validated = False
            self.api_key_status.setText("✗ 오류 발생")
            self.api_key_status.setStyleSheet("color: #d65c5c;")
            error_msg = f"API 키 검증 중 오류 발생: {str(e)}"
            self.log.error(error_msg)
            QMessageBox.critical(self, "API 키 검증 오류", error_msg)
        
        # 검증 완료 후 UI 업데이트
        self.validate_api_btn.setEnabled(True) 

    def export_to_excel(self):
        """작업 모니터 데이터를 엑셀 파일로 내보내기"""
        # 사용자 확인
        reply = QMessageBox.question(
            self,
            '엑셀 다운로드',
            '현재 수집된 데이터를 엑셀 파일로 다운로드하시겠습니까?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
            
        try:
            # 데이터 수집
            data = []
            for row in range(self.task_monitor.rowCount()):
                row_data = []
                for col in range(self.task_monitor.columnCount()):
                    item = self.task_monitor.item(row, col)
                    row_data.append(item.text() if item else '')
                data.append(row_data)
            
            # DataFrame 생성
            df = pd.DataFrame(data, columns=['NO', '아이디', '내용', 'URL'])
            
            # 파일 저장 대화상자
            default_filename = f'작업_모니터_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "엑셀 파일 저장",
                default_filename,
                "Excel Files (*.xlsx)"
            )
            
            if filename:
                # 엑셀 파일로 저장
                df.to_excel(filename, index=False, engine='openpyxl')
                self.log.info(f'엑셀 파일이 저장되었습니다: {filename}')
                QMessageBox.information(self, '저장 완료', '엑셀 파일이 성공적으로 저장되었습니다.')
        except Exception as e:
            self.log.error(f'엑셀 파일 저장 중 오류 발생: {str(e)}')
            QMessageBox.critical(self, '오류', f'엑셀 파일 저장 중 오류가 발생했습니다:\n{str(e)}')

    def clear_monitor(self):
        """작업 모니터 데이터 초기화"""
        # 사용자 확인
        reply = QMessageBox.question(
            self,
            '수집 초기화',
            '현재 수집된 모든 데이터가 삭제됩니다.\n계속하시겠습니까?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 테이블 초기화
                self.task_monitor.setRowCount(0)
                self.log.info('작업 모니터가 초기화되었습니다.')
                QMessageBox.information(self, '초기화 완료', '작업 모니터가 초기화되었습니다.')
            except Exception as e:
                self.log.error(f'작업 모니터 초기화 중 오류 발생: {str(e)}')
                QMessageBox.critical(self, '오류', f'작업 모니터 초기화 중 오류가 발생했습니다:\n{str(e)}') 