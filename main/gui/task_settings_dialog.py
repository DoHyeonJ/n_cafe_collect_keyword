from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                           QLabel, QListWidget, QPushButton, QLineEdit,
                           QMessageBox, QInputDialog, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt
from ..utils.task_manager import TaskManager
from datetime import datetime

class SettingsDialog(QDialog):
    """설정 저장/불러오기 대화상자"""
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.task_manager = TaskManager()
        self.init_ui()
        self.load_settings_list()
        
    def init_ui(self):
        """UI 초기화"""
        # 대화상자 설정
        self.setWindowTitle("설정 관리")
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
        list_group = QGroupBox("설정 목록")
        list_layout = QVBoxLayout()
        list_layout.setContentsMargins(10, 20, 10, 10)
        list_layout.setSpacing(10)
        
        # 작업 설정 목록 위젯
        self.settings_list = QListWidget()
        self.settings_list.itemSelectionChanged.connect(self.on_setting_selected)
        list_layout.addWidget(self.settings_list)
        
        # 작업 설정 정보 그룹
        info_group = QGroupBox("선택한 설정 정보")
        info_layout = QFormLayout()
        info_layout.setContentsMargins(10, 20, 10, 10)
        info_layout.setSpacing(10)
        
        # 정보 레이블
        self.filename_label = QLabel("-")
        self.saved_at_label = QLabel("-")
        self.account_label = QLabel("-")
        self.keyword_label = QLabel("-")
        self.target_label = QLabel("-")
        self.sort_label = QLabel("-")
        self.trade_method_label = QLabel("-")
        self.trade_status_label = QLabel("-")
        self.api_key_label = QLabel("-")
        self.ai_keyword_label = QLabel("-")
        
        # 정보 추가
        info_layout.addRow("파일명:", self.filename_label)
        info_layout.addRow("저장 시간:", self.saved_at_label)
        info_layout.addRow("계정 정보:", self.account_label)
        info_layout.addRow("검색 키워드:", self.keyword_label)
        info_layout.addRow("대상:", self.target_label)
        info_layout.addRow("정렬 방식:", self.sort_label)
        info_layout.addRow("거래 방법:", self.trade_method_label)
        info_layout.addRow("거래 상태:", self.trade_status_label)
        info_layout.addRow("API KEY:", self.api_key_label)
        info_layout.addRow("AI 분석키워드:", self.ai_keyword_label)
        
        info_group.setLayout(info_layout)
        list_group.setLayout(list_layout)
        
        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 저장 버튼
        self.save_btn = QPushButton("현재 설정 저장")
        self.save_btn.clicked.connect(self.save_current_settings)
        
        # 불러오기 버튼
        self.load_btn = QPushButton("선택한 설정 불러오기")
        self.load_btn.clicked.connect(self.load_selected_settings)
        self.load_btn.setEnabled(False)  # 초기에는 비활성화
        
        # 삭제 버튼
        self.delete_btn = QPushButton("선택한 설정 삭제")
        self.delete_btn.clicked.connect(self.delete_selected_setting)
        self.delete_btn.setEnabled(False)  # 초기에는 비활성화
        
        # 이름 변경 버튼
        self.rename_btn = QPushButton("설정 이름 변경")
        self.rename_btn.clicked.connect(self.rename_selected_setting)
        self.rename_btn.setEnabled(False)  # 초기에는 비활성화
        
        # 버튼 추가
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.rename_btn)
        button_layout.addWidget(self.delete_btn)
        
        # 메인 레이아웃에 위젯 추가
        main_layout.addWidget(list_group, 3)  # 비율 3
        main_layout.addWidget(info_group, 2)  # 비율 2 (레이블이 더 많아졌으므로 비율 증가)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def load_settings_list(self):
        """설정 목록 불러오기"""
        # 목록 초기화
        self.settings_list.clear()
        
        # 작업 설정 목록 조회
        task_files = self.task_manager.get_task_list()
        
        # 목록 추가
        for filename in task_files:
            self.settings_list.addItem(filename)
        
        # 정보 초기화
        self.clear_settings_info()
    
    def clear_settings_info(self):
        """설정 정보 초기화"""
        self.filename_label.setText("-")
        self.saved_at_label.setText("-")
        self.account_label.setText("-")
        self.keyword_label.setText("-")
        self.target_label.setText("-")
        self.sort_label.setText("-")
        self.trade_method_label.setText("-")
        self.trade_status_label.setText("-")
        self.api_key_label.setText("-")
        self.ai_keyword_label.setText("-")
        
        # 버튼 비활성화
        self.load_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.rename_btn.setEnabled(False)
    
    def on_setting_selected(self):
        """설정 선택 시 호출"""
        # 선택된 항목 확인
        selected_items = self.settings_list.selectedItems()
        if not selected_items:
            self.clear_settings_info()
            return
        
        # 선택된 파일명
        filename = selected_items[0].text()
        
        # 설정 정보 조회
        task_settings = self.task_manager.load_task_settings(filename)
        
        if not task_settings:
            self.clear_settings_info()
            return
        
        # 설정 정보 표시
        self.filename_label.setText(filename)
        self.saved_at_label.setText(task_settings.get('saved_at', '-'))
        
        # 계정 정보
        accounts = task_settings.get('accounts', {})
        if accounts:
            account_ids = list(accounts.keys())
            self.account_label.setText(f"{len(account_ids)}개 계정" if len(account_ids) > 1 else account_ids[0])
        else:
            self.account_label.setText("-")
        
        # 작업 정보 표시
        tasks = task_settings.get('tasks', [])
        if tasks and len(tasks) > 0:
            first_task = tasks[0]  # 첫 번째 작업 정보만 표시
            
            # 검색 키워드
            keywords = first_task.get('keywords', [])
            self.keyword_label.setText(", ".join(keywords) if keywords else "-")
            
            # 대상
            target = first_task.get('target', '-')
            self.target_label.setText(target)
            
            # 정렬
            sort_option = first_task.get('sort_option', '-')
            self.sort_label.setText(sort_option)
            
            # 거래 방법
            trade_method = first_task.get('trade_method', '-')
            self.trade_method_label.setText(trade_method)
            
            # 거래 상태
            trade_status = first_task.get('trade_status', '-')
            self.trade_status_label.setText(trade_status)
            
            # AI 분석 키워드
            ai_keywords = first_task.get('ai_keywords', [])
            self.ai_keyword_label.setText(", ".join(ai_keywords) if ai_keywords else "-")
        else:
            self.keyword_label.setText("-")
            self.target_label.setText("-")
            self.sort_label.setText("-")
            self.trade_method_label.setText("-")
            self.trade_status_label.setText("-")
            self.ai_keyword_label.setText("-")
        
        # API 키
        try:
            api_key = task_settings.get('task_settings', {}).get('api_key', '')
            if api_key:
                # API 키는 보안을 위해 일부만 표시
                masked_key = api_key[:4] + "****" + api_key[-4:] if len(api_key) > 8 else "****"
                self.api_key_label.setText(masked_key)
            else:
                self.api_key_label.setText("-")
        except Exception as e:
            print(f"API 키 표시 오류: {str(e)}")
            self.api_key_label.setText("-")
        
        # 버튼 활성화
        self.load_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        self.rename_btn.setEnabled(True)
    
    def save_current_settings(self):
        """현재 설정값 저장"""
        # 모든 설정 정보 가져오기
        settings_data = self.main_window.get_all_settings()
        
        # 설정 데이터 확인
        if not settings_data:
            QMessageBox.warning(self, "경고", "저장할 설정이 없습니다.")
            return
            
        # 설정 데이터 디버그 정보 출력
        accounts = settings_data.get('accounts', {})
        tasks = settings_data.get('tasks', [])
        api_key = settings_data.get('task_settings', {}).get('api_key', '')
        search_keywords = settings_data.get('task_settings', {}).get('search_keywords', '')
        ai_keywords = settings_data.get('task_settings', {}).get('ai_keywords', '')
        
        print(f"저장 정보 확인: 계정({len(accounts)}개), 작업({len(tasks)}개), API 키({len(api_key)>0})")
        print(f"키워드 정보: 검색 키워드({search_keywords}), AI 키워드({ai_keywords})")
        
        # 모든 설정 값이 비어있는지 확인
        has_content = (
            len(accounts) > 0 or 
            len(tasks) > 0 or 
            api_key or 
            search_keywords or 
            ai_keywords
        )
        
        if not has_content:
            print("경고: 모든 설정 값이 비어있습니다.")
            reply = QMessageBox.question(
                self,
                "설정 저장",
                "설정 값이 비어있습니다. 그래도 저장하시겠습니까?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        # 파일명 입력 대화상자
        filename, ok = QInputDialog.getText(
            self, 
            "설정 저장", 
            "저장할 파일 이름을 입력하세요:",
            QLineEdit.Normal,
            f"설정_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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
        
        # 설정 저장
        success = self.task_manager.save_task_settings(settings_data, filename)
        
        if success:
            # 계정 수와 API 키 정보 추가하여 표시
            accounts_info = f"계정 {len(accounts)}개, " if accounts else ""
            api_info = "API 키 포함, " if api_key else ""
            keywords_info = f"검색 키워드({len(search_keywords.split(',')) if search_keywords else 0}개)" if search_keywords else ""
            
            info_msg = f"설정이 '{filename}'에 저장되었습니다. ({accounts_info}{api_info}{keywords_info})"
            QMessageBox.information(self, "저장 완료", info_msg)
            print(f"설정 저장 성공: {filename}")
            self.load_settings_list()  # 목록 새로고침
        else:
            QMessageBox.critical(self, "저장 실패", "설정 저장 중 오류가 발생했습니다.")
            print(f"설정 저장 실패: {filename}")
    
    def load_selected_settings(self):
        """선택한 설정 불러오기"""
        try:
            # 선택된 항목 확인
            selected_items = self.settings_list.selectedItems()
            if not selected_items:
                print("불러오기 실패: 선택된 항목이 없습니다.")
                return
            
            # 선택된 파일명
            filename = selected_items[0].text()
            print(f"선택된 설정 파일: {filename}")
            
            # 설정 불러오기
            task_settings = self.task_manager.load_task_settings(filename)
            
            if not task_settings:
                QMessageBox.critical(self, "불러오기 실패", "설정을 불러오는 중 오류가 발생했습니다.")
                print("불러오기 실패: 설정 파일을 읽을 수 없습니다.")
                return
            
            # 불러온 설정 정보 확인 및 디버그 출력
            accounts = task_settings.get('accounts', {})
            tasks = task_settings.get('tasks', [])
            task_settings_data = task_settings.get('task_settings', {})
            api_key = task_settings_data.get('api_key', '')
            search_keywords = task_settings_data.get('search_keywords', '')
            ai_keywords = task_settings_data.get('ai_keywords', '')
            saved_at = task_settings.get('saved_at', '')
            
            print(f"불러온 설정 정보: 계정({len(accounts)}개), 작업({len(tasks)}개), API 키({len(api_key)>0})")
            print(f"검색 키워드: {search_keywords}")
            print(f"AI 키워드: {ai_keywords}")
            print(f"저장 시간: {saved_at}")
            
            # 키가 모두 비어있는지 확인
            if not accounts and not tasks and not api_key and not search_keywords and not ai_keywords:
                reply = QMessageBox.warning(
                    self, 
                    "불러오기 경고", 
                    "선택한 설정 파일에 데이터가 없습니다. 계속 진행하시겠습니까?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    print("불러오기 취소: 비어있는 설정 파일이었습니다.")
                    return
            
            # 현재 설정과 병합 여부 확인
            current_settings = self.main_window.get_all_settings()
            current_tasks = current_settings.get('tasks', [])
            current_accounts = current_settings.get('accounts', {})
            
            if current_tasks or current_accounts:
                reply = QMessageBox.question(
                    self,
                    "설정 덮어쓰기",
                    "현재 설정을 불러온 설정으로 덮어쓰시겠습니까?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    print("불러오기 취소: 사용자가 덮어쓰기를 취소했습니다.")
                    return
            
            # 설정 적용
            try:
                print("설정 적용 시작...")
                success = self.main_window.apply_settings(task_settings)
                
                if success:
                    # 불러온 설정 정보 표시
                    accounts_info = f"계정 {len(accounts)}개, " if accounts else ""
                    tasks_info = f"작업 {len(tasks)}개, " if tasks else ""
                    api_info = "API 키 포함, " if api_key else ""
                    keywords_info = f"검색 키워드 포함" if search_keywords else ""
                    
                    info_msg = f"설정 '{filename}'을(를) 불러왔습니다. ({accounts_info}{tasks_info}{api_info}{keywords_info})"
                    QMessageBox.information(self, "불러오기 완료", info_msg)
                    print(f"설정 불러오기 성공: {filename}")
                    self.accept()  # 대화상자 닫기
                else:
                    QMessageBox.warning(self, "불러오기 부분 실패", "일부 설정을 적용하는 데 실패했습니다.")
                    print("불러오기 부분 실패: apply_settings 메서드가 False를 반환했습니다.")
            except Exception as e:
                QMessageBox.critical(self, "적용 실패", f"설정을 적용하는 중 오류가 발생했습니다.\n오류: {str(e)}")
                print(f"설정 적용 중 오류: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "불러오기 실패", f"설정을 불러오는 중 예기치 않은 오류가 발생했습니다.\n오류: {str(e)}")
            print(f"불러오기 중 예외 발생: {str(e)}")
    
    def delete_selected_setting(self):
        """선택한 설정 삭제"""
        # 선택된 항목 확인
        selected_items = self.settings_list.selectedItems()
        if not selected_items:
            return
        
        # 선택된 파일명
        filename = selected_items[0].text()
        
        # 삭제 확인
        reply = QMessageBox.question(
            self,
            "설정 삭제",
            f"'{filename}' 설정을 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # 작업 설정 삭제
        success = self.task_manager.delete_task_settings(filename)
        
        if success:
            QMessageBox.information(self, "삭제 완료", f"설정 '{filename}'이(가) 삭제되었습니다.")
            self.load_settings_list()  # 목록 새로고침
            self.clear_settings_info()  # 정보 초기화
        else:
            QMessageBox.critical(self, "삭제 실패", "설정 삭제 중 오류가 발생했습니다.")
    
    def rename_selected_setting(self):
        """선택한 설정 이름 변경"""
        # 선택된 항목 확인
        selected_items = self.settings_list.selectedItems()
        if not selected_items:
            return
        
        # 선택된 파일명
        old_filename = selected_items[0].text()
        
        # 새 파일명 입력 대화상자
        new_filename, ok = QInputDialog.getText(
            self, 
            "설정 이름 변경", 
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
                f"설정 이름이 '{old_filename}'에서 '{new_filename}'(으)로 변경되었습니다."
            )
            self.load_settings_list()  # 목록 새로고침
        else:
            QMessageBox.critical(self, "이름 변경 실패", "설정 이름 변경 중 오류가 발생했습니다.")
    
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