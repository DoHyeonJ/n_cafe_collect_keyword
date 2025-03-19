from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QGroupBox, QLabel, QTableWidget, 
                           QHeaderView, QTableWidgetItem, QTabWidget, 
                           QTextEdit, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from datetime import datetime
from ..utils.log import Log
import pandas as pd

class RoutineTab(QWidget):
    execute_tasks_clicked = pyqtSignal(bool)  # 작업 실행/정지 시그널
    
    def __init__(self, log: Log):
        super().__init__()
        self.log = log
        self.is_running = False  # 실행 상태
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # 다음 작업 정보 표시 영역
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
        
        # 버튼 컨테이너 추가
        button_container = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 10)
        
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
        button_layout.addStretch()
        button_layout.addWidget(self.clear_btn)
        button_container.setLayout(button_layout)
        
        # 작업 모니터 테이블
        self.task_monitor = QTableWidget(0, 4)
        self.task_monitor.setHorizontalHeaderLabels(["NO", "아이디", "내용", "URL"])
        
        # 컬럼 너비 설정
        header = self.task_monitor.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # NO
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # 아이디
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # 내용
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # URL
        
        self.task_monitor.setColumnWidth(0, 50)  # NO
        self.task_monitor.setColumnWidth(1, 100)  # 아이디
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
            QHeaderView::section {
                background-color: #353535;
                padding: 5px;
                border: 1px solid #3d3d3d;
                color: white;
                font-weight: bold;
            }
        """)
        
        # 로그 모니터 추가
        self.log_monitor = QTableWidget(0, 2)
        self.log_monitor.setHorizontalHeaderLabels(["시간", "메시지"])
        
        # 로그 모니터 컬럼 너비 설정
        log_header = self.log_monitor.horizontalHeader()
        log_header.setSectionResizeMode(0, QHeaderView.Fixed)  # 시간
        log_header.setSectionResizeMode(1, QHeaderView.Stretch)  # 메시지
        self.log_monitor.setColumnWidth(0, 180)  # 시간
        
        # 로그 모니터 가로 스크롤바 숨기기
        self.log_monitor.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 로그 모니터 높이 설정
        self.log_monitor.setMinimumHeight(100)
        self.log_monitor.setMaximumHeight(150)
        
        # 로그 모니터 스타일 설정
        self.log_monitor.setStyleSheet("""
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
        """)
        
        # 실행 버튼 추가
        self.execute_btn = QPushButton("실행")
        self.execute_btn.setFixedHeight(40)
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
        
        # 메인 레이아웃에 위젯 추가
        layout.addWidget(button_container)
        layout.addWidget(self.task_monitor)
        layout.addWidget(self.next_task_label)
        layout.addWidget(self.log_monitor)
        layout.addWidget(self.execute_btn)
        self.setLayout(layout)

    def toggle_execution(self):
        """실행/중지 버튼 클릭 시 호출되는 메서드"""
        try:
            if not self.is_running:
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
                
                # 실행 시그널 발생
                self.execute_tasks_clicked.emit(True)
                self.log.info("작업 실행이 시작되었습니다.")
            else:
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
                
                # 중지 시그널 발생
                self.execute_tasks_clicked.emit(False)
                self.log.info("작업 실행이 중지되었습니다.")
        except Exception as e:
            self.log.error(f"toggle_execution 메서드 실행 중 오류 발생: {str(e)}")
            # 오류 발생 시 상태 초기화
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

    def add_log_message(self, log_entry):
        """로그 메시지 추가"""
        message = log_entry.get('message', '')
        color = log_entry.get('color', 'white')
        
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
        """
        next_task_number = info.get('next_task_number', 0)
        next_execution_time = info.get('next_execution_time', '')
        wait_time = info.get('wait_time', '')
        current_task = info.get('current_task', {})
        
        # 현재 작업 정보 추출
        task_id = current_task.get('task_id', '')
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
            
            action_info = ""
            if action:
                action_info += f" | {action} 중"
            
            # 최종 텍스트 구성
            self.next_task_label.setText(
                f"{task_info}{action_info} | 다음 실행: {next_execution_time}"
            )
        
        self.log.info(f"다음 작업 정보가 업데이트되었습니다: {next_task_number}")

    def export_to_excel(self):
        """작업 모니터 데이터를 엑셀 파일로 내보내기"""
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
        reply = QMessageBox.question(
            self,
            '수집 초기화',
            '현재 수집된 모든 데이터가 삭제됩니다.\n계속하시겠습니까?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.task_monitor.setRowCount(0)
                self.log.info('작업 모니터가 초기화되었습니다.')
                QMessageBox.information(self, '초기화 완료', '작업 모니터가 초기화되었습니다.')
            except Exception as e:
                self.log.error(f'작업 모니터 초기화 중 오류 발생: {str(e)}')
                QMessageBox.critical(self, '오류', f'작업 모니터 초기화 중 오류가 발생했습니다:\n{str(e)}') 