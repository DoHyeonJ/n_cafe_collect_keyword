from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                            QPushButton, QLabel, QLineEdit, QMessageBox,
                            QInputDialog, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
import os

class SettingsDialog(QDialog):
    settings_selected = pyqtSignal(str)  # 설정 선택 시그널
    
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.selected_file = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("설정 관리")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        # 설정 파일 목록 레이블
        list_label = QLabel("저장된 설정 목록")
        list_label.setStyleSheet("font-weight: bold; color: white;")
        layout.addWidget(list_label)
        
        # 설정 파일 목록
        self.settings_list = QListWidget()
        self.settings_list.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3d3d3d;
            }
            QListWidget::item:selected {
                background-color: #4b6eaf;
            }
            QListWidget::item:hover {
                background-color: #353535;
            }
        """)
        self.settings_list.itemClicked.connect(self.on_item_selected)
        self.settings_list.itemDoubleClicked.connect(self.load_selected_settings)
        layout.addWidget(self.settings_list)
        
        # 버튼 영역
        button_layout = QHBoxLayout()
        
        # 새 설정 저장 버튼
        self.save_btn = QPushButton("현재 설정 저장")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.save_btn.clicked.connect(self.save_current_settings)
        
        # 설정 불러오기 버튼
        self.load_btn = QPushButton("불러오기")
        self.load_btn.setStyleSheet("""
            QPushButton {
                background-color: #5c85d6;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4b6eaf;
            }
        """)
        self.load_btn.clicked.connect(self.load_selected_settings)
        self.load_btn.setEnabled(False)  # 초기에는 비활성화
        
        # 설정 삭제 버튼
        self.delete_btn = QPushButton("삭제")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #d65c5c;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #b84a4a;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_selected_settings)
        self.delete_btn.setEnabled(False)  # 초기에는 비활성화
        
        # 이름 변경 버튼
        self.rename_btn = QPushButton("이름 변경")
        self.rename_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFA500;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #FF8C00;
            }
        """)
        self.rename_btn.clicked.connect(self.rename_selected_settings)
        self.rename_btn.setEnabled(False)  # 초기에는 비활성화
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.rename_btn)
        button_layout.addWidget(self.delete_btn)
        
        layout.addLayout(button_layout)
        
        # 안내 문구 추가
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #5c85d6;
                border-radius: 4px;
                padding: 5px;
                margin-top: 10px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        info_label = QLabel(
            "<b>설정 저장 안내</b><br><br>"
            "설정 파일에는 다음 정보가 저장됩니다:<br>"
            "• 등록된 계정 목록 (아이디/비밀번호)<br>"
            "• 작업 목록 및 각 작업의 세부 설정<br><br>"
            "※ 설정 파일은 프로그램을 실행하는 PC에만 저장되며, 외부로 전송되지 않습니다. <br>"
        )
        info_label.setStyleSheet("""
            color: #cccccc;
            padding: 5px;
        """)
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        
        layout.addWidget(info_frame)
        
        # 닫기 버튼
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        
        self.close_btn = QPushButton("닫기")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        
        close_layout.addWidget(self.close_btn)
        layout.addLayout(close_layout)
        
        self.setLayout(layout)
        
        # 설정 파일 목록 로드
        self.load_settings_list()
        
    def load_settings_list(self):
        """저장된 설정 파일 목록 로드"""
        self.settings_list.clear()
        settings_files = self.settings_manager.get_settings_list()
        
        for file_name in settings_files:
            # .json 확장자 제거하여 표시
            display_name = file_name
            if display_name.endswith('.json'):
                display_name = display_name[:-5]
                
            self.settings_list.addItem(display_name)
    
    def on_item_selected(self, item):
        """설정 파일 선택 시 처리"""
        self.selected_file = item.text()
        if self.selected_file.endswith('.json') == False:
            self.selected_file += '.json'
            
        self.load_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        self.rename_btn.setEnabled(True)
    
    def save_current_settings(self):
        """현재 설정 저장"""
        name, ok = QInputDialog.getText(
            self, '설정 저장', '설정 이름을 입력하세요:',
            QLineEdit.Normal, f"설정_{self.get_current_date_time()}"
        )
        
        if ok and name:
            # 메인 윈도우에서 현재 설정 데이터 가져오기
            settings_data = self.parent().get_all_settings()
            
            # 설정 저장
            success, result = self.settings_manager.save_settings(settings_data, name)
            
            if success:
                QMessageBox.information(self, '저장 완료', f'설정이 저장되었습니다.\n{os.path.basename(result)}')
                self.load_settings_list()  # 목록 새로고침
            else:
                QMessageBox.warning(self, '저장 실패', f'설정 저장 중 오류가 발생했습니다.\n{result}')
    
    def load_selected_settings(self):
        """선택한 설정 불러오기"""
        if not self.selected_file:
            return
            
        reply = QMessageBox.question(
            self, 
            '설정 불러오기',
            f'"{self.selected_file[:-5]}" 설정을 불러오시겠습니까?\n\n'
            f'현재 설정이 모두 변경됩니다.\n'
            f'일부 계정은 재로그인이 필요할 수 있습니다.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, result = self.settings_manager.load_settings(self.selected_file)
            
            if success:
                # 메인 윈도우에 설정 적용
                if self.parent().apply_settings(result):
                    QMessageBox.information(self, '불러오기 완료', '설정을 성공적으로 불러왔습니다.')
                    self.close()  # 대화상자 닫기
            else:
                QMessageBox.warning(self, '불러오기 실패', f'설정을 불러오는 중 오류가 발생했습니다.\n{result}')
    
    def delete_selected_settings(self):
        """선택한 설정 삭제"""
        if not self.selected_file:
            return
            
        reply = QMessageBox.question(
            self, 
            '설정 삭제',
            f'"{self.selected_file[:-5]}" 설정을 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, error = self.settings_manager.delete_settings(self.selected_file)
            
            if success:
                QMessageBox.information(self, '삭제 완료', '설정이 삭제되었습니다.')
                self.load_settings_list()  # 목록 새로고침
                
                # 버튼 비활성화
                self.load_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
                self.rename_btn.setEnabled(False)
                self.selected_file = None
            else:
                QMessageBox.warning(self, '삭제 실패', f'설정을 삭제하는 중 오류가 발생했습니다.\n{error}')
    
    def rename_selected_settings(self):
        """선택한 설정 이름 변경"""
        if not self.selected_file:
            return
            
        old_name = self.selected_file
        if old_name.endswith('.json'):
            old_name = old_name[:-5]
            
        new_name, ok = QInputDialog.getText(
            self, '이름 변경', '새 이름을 입력하세요:',
            QLineEdit.Normal, old_name
        )
        
        if ok and new_name:
            success, error = self.settings_manager.rename_settings(self.selected_file, new_name)
            
            if success:
                QMessageBox.information(self, '이름 변경 완료', '설정 이름이 변경되었습니다.')
                self.load_settings_list()  # 목록 새로고침
                
                # 버튼 비활성화
                self.load_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
                self.rename_btn.setEnabled(False)
                self.selected_file = None
            else:
                QMessageBox.warning(self, '이름 변경 실패', f'설정 이름을 변경하는 중 오류가 발생했습니다.\n{error}')
    
    def get_current_date_time(self):
        """현재 날짜와 시간을 문자열로 반환"""
        from datetime import datetime
        return datetime.now().strftime('%Y%m%d_%H%M%S') 