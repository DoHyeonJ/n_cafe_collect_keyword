from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                           QLabel, QListWidget, QPushButton, QLineEdit,
                           QMessageBox, QInputDialog, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt
from ..utils.task_manager import TaskManager
from datetime import datetime

class TaskSettingsDialog(QDialog):
    """작업 설정 저장/불러오기 대화상자"""
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.task_manager = TaskManager()
        self.init_ui()
        self.load_task_list()
        
    def init_ui(self):
        """UI 초기화"""
        # 대화상자 설정
        self.setWindowTitle("작업 설정 관리")
        self.setMinimumSize(600, 500)
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
            QPushButton:disabled {
                background-color: #555555;
                color: #aaaaaa;
            }
            QLineEdit {
                background-color: #333;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 작업 설정 목록 그룹
        list_group = QGroupBox("작업 설정 목록")
        list_layout = QVBoxLayout()
        list_layout.setContentsMargins(10, 20, 10, 10)
        list_layout.setSpacing(10)
        
        # 작업 설정 목록 위젯
        self.task_list = QListWidget()
        self.task_list.itemSelectionChanged.connect(self.on_task_selected)
        list_layout.addWidget(self.task_list)
        
        # 작업 설정 정보 그룹
        info_group = QGroupBox("선택한 작업 설정 정보")
        info_layout = QFormLayout()
        info_layout.setContentsMargins(10, 20, 10, 10)
        info_layout.setSpacing(10)
        
        # 정보 레이블
        self.filename_label = QLabel("-")
        self.saved_at_label = QLabel("-")
        self.task_count_label = QLabel("-")
        self.account_count_label = QLabel("-")
        self.prompt_count_label = QLabel("-")
        
        # 정보 추가
        info_layout.addRow("파일명:", self.filename_label)
        info_layout.addRow("저장 시간:", self.saved_at_label)
        info_layout.addRow("작업 수:", self.task_count_label)
        info_layout.addRow("계정 수:", self.account_count_label)
        info_layout.addRow("프롬프트 수:", self.prompt_count_label)
        
        info_group.setLayout(info_layout)
        list_group.setLayout(list_layout)
        
        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 저장 버튼
        self.save_btn = QPushButton("현재 작업 저장")
        self.save_btn.clicked.connect(self.save_current_tasks)
        
        # 불러오기 버튼
        self.load_btn = QPushButton("선택한 작업 불러오기")
        self.load_btn.clicked.connect(self.load_selected_tasks)
        self.load_btn.setEnabled(False)  # 초기에는 비활성화
        
        # 삭제 버튼
        self.delete_btn = QPushButton("삭제")
        self.delete_btn.clicked.connect(self.delete_selected_task)
        self.delete_btn.setEnabled(False)  # 초기에는 비활성화
        
        # 이름 변경 버튼
        self.rename_btn = QPushButton("이름 변경")
        self.rename_btn.clicked.connect(self.rename_selected_task)
        self.rename_btn.setEnabled(False)  # 초기에는 비활성화
        
        # 버튼 추가
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.rename_btn)
        button_layout.addWidget(self.delete_btn)
        
        # 메인 레이아웃에 위젯 추가
        main_layout.addWidget(list_group, 3)  # 비율 3
        main_layout.addWidget(info_group, 1)  # 비율 1
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def load_task_list(self):
        """작업 설정 목록 불러오기"""
        # 목록 초기화
        self.task_list.clear()
        
        # 작업 설정 목록 조회
        task_files = self.task_manager.get_task_list()
        
        # 목록 추가
        for filename in task_files:
            self.task_list.addItem(filename)
        
        # 정보 초기화
        self.clear_task_info()
    
    def clear_task_info(self):
        """작업 설정 정보 초기화"""
        self.filename_label.setText("-")
        self.saved_at_label.setText("-")
        self.task_count_label.setText("-")
        self.account_count_label.setText("-")
        self.prompt_count_label.setText("-")
        
        # 버튼 비활성화
        self.load_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.rename_btn.setEnabled(False)
    
    def on_task_selected(self):
        """작업 설정 선택 시 호출"""
        # 선택된 항목 확인
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            self.clear_task_info()
            return
        
        # 선택된 파일명
        filename = selected_items[0].text()
        
        # 작업 설정 정보 조회
        task_info = self.task_manager.get_task_info(filename)
        
        if not task_info:
            self.clear_task_info()
            return
        
        # 정보 표시
        self.filename_label.setText(task_info['filename'])
        self.saved_at_label.setText(task_info['saved_at'])
        self.task_count_label.setText(str(task_info['task_count']))
        self.account_count_label.setText(str(task_info['account_count']))
        self.prompt_count_label.setText(str(task_info['prompt_count']))
        
        # 버튼 활성화
        self.load_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        self.rename_btn.setEnabled(True)
    
    def save_current_tasks(self):
        """현재 작업 설정 저장"""
        # 작업 목록 확인
        tasks = self.main_window.get_all_tasks()
        if not tasks:
            QMessageBox.warning(self, "경고", "저장할 작업이 없습니다.")
            return
        
        # 파일명 입력 대화상자
        filename, ok = QInputDialog.getText(
            self, 
            "작업 설정 저장", 
            "저장할 파일 이름을 입력하세요:",
            QLineEdit.Normal,
            f"작업설정_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        if not ok or not filename:
            return
        
        # 파일명 유효성 검사
        if not self.is_valid_filename(filename):
            QMessageBox.warning(
                self, 
                "경고", 
                "유효하지 않은 파일 이름입니다. 특수문자를 제외한 이름을 입력해주세요."
            )
            return
        
        # 이미 존재하는 파일명인지 확인
        if filename in self.task_manager.get_task_list():
            reply = QMessageBox.question(
                self,
                "파일 덮어쓰기",
                f"'{filename}' 파일이 이미 존재합니다. 덮어쓰시겠습니까?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        # 계정 정보 수집
        accounts = self.main_window.get_accounts_settings()
        
        # 작업 설정 생성
        task_settings = {
            'tasks': tasks,
            'accounts': accounts
        }
        
        # 작업 설정 저장
        success = self.task_manager.save_task_settings(task_settings, filename)
        
        if success:
            QMessageBox.information(self, "저장 완료", f"작업 설정이 '{filename}'에 저장되었습니다.")
            self.load_task_list()  # 목록 새로고침
        else:
            QMessageBox.critical(self, "저장 실패", "작업 설정 저장 중 오류가 발생했습니다.")
    
    def load_selected_tasks(self):
        """선택한 작업 설정 불러오기"""
        # 선택된 항목 확인
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            return
        
        # 선택된 파일명
        filename = selected_items[0].text()
        
        # 현재 작업이 있는 경우 확인
        current_tasks = self.main_window.get_all_tasks()
        if current_tasks:
            reply = QMessageBox.question(
                self,
                "작업 덮어쓰기",
                "현재 작업 목록이 있습니다. 불러온 작업으로 덮어쓰시겠습니까?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        # 작업 설정 불러오기
        task_settings = self.task_manager.load_task_settings(filename)
        
        if not task_settings:
            QMessageBox.critical(self, "불러오기 실패", "작업 설정을 불러오는 중 오류가 발생했습니다.")
            return
        
        # 작업 설정 적용
        success = self.main_window.apply_settings(task_settings)
        
        if success:
            QMessageBox.information(self, "불러오기 완료", f"작업 설정 '{filename}'을(를) 불러왔습니다.")
            self.accept()  # 대화상자 닫기
        else:
            QMessageBox.warning(self, "불러오기 부분 실패", "일부 설정을 적용하는 데 실패했습니다.")
    
    def delete_selected_task(self):
        """선택한 작업 설정 삭제"""
        # 선택된 항목 확인
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            return
        
        # 선택된 파일명
        filename = selected_items[0].text()
        
        # 삭제 확인
        reply = QMessageBox.question(
            self,
            "작업 설정 삭제",
            f"'{filename}' 작업 설정을 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # 작업 설정 삭제
        success = self.task_manager.delete_task_settings(filename)
        
        if success:
            QMessageBox.information(self, "삭제 완료", f"작업 설정 '{filename}'이(가) 삭제되었습니다.")
            self.load_task_list()  # 목록 새로고침
            self.clear_task_info()  # 정보 초기화
        else:
            QMessageBox.critical(self, "삭제 실패", "작업 설정 삭제 중 오류가 발생했습니다.")
    
    def rename_selected_task(self):
        """선택한 작업 설정 이름 변경"""
        # 선택된 항목 확인
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            return
        
        # 선택된 파일명
        old_filename = selected_items[0].text()
        
        # 새 파일명 입력 대화상자
        new_filename, ok = QInputDialog.getText(
            self, 
            "작업 설정 이름 변경", 
            "새 파일 이름을 입력하세요:",
            QLineEdit.Normal,
            old_filename
        )
        
        if not ok or not new_filename or new_filename == old_filename:
            return
        
        # 파일명 유효성 검사
        if not self.is_valid_filename(new_filename):
            QMessageBox.warning(
                self, 
                "경고", 
                "유효하지 않은 파일 이름입니다. 특수문자를 제외한 이름을 입력해주세요."
            )
            return
        
        # 이미 존재하는 파일명인지 확인
        if new_filename in self.task_manager.get_task_list():
            QMessageBox.warning(
                self,
                "이름 변경 실패",
                f"'{new_filename}' 파일이 이미 존재합니다. 다른 이름을 입력해주세요."
            )
            return
        
        # 작업 설정 이름 변경
        success = self.task_manager.rename_task_settings(old_filename, new_filename)
        
        if success:
            QMessageBox.information(
                self, 
                "이름 변경 완료", 
                f"작업 설정 이름이 '{old_filename}'에서 '{new_filename}'(으)로 변경되었습니다."
            )
            self.load_task_list()  # 목록 새로고침
        else:
            QMessageBox.critical(self, "이름 변경 실패", "작업 설정 이름 변경 중 오류가 발생했습니다.")
    
    def is_valid_filename(self, filename):
        """파일명 유효성 검사
        
        Args:
            filename (str): 검사할 파일명
            
        Returns:
            bool: 유효한 파일명 여부
        """
        # 파일명에 사용할 수 없는 문자 확인
        invalid_chars = r'<>:"/\|?*'
        return not any(char in filename for char in invalid_chars) 