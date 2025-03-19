from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QLabel, 
                           QTextEdit, QHBoxLayout, QSpinBox, QCheckBox, QGroupBox, QListWidget, QPushButton,
                           QDialog)
from PyQt5.QtCore import Qt
from .cafe_widget import CafeWidget

class PromptDialog(QDialog):
    """AI 프롬프트 관리 다이얼로그"""
    def __init__(self, prompts=None, parent=None):
        super().__init__(parent)
        self.prompts = prompts or []
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("AI 프롬프트 관리")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        
        # 설명 영역 추가
        desc_group = QGroupBox("프롬프트 설정 안내")
        desc_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-weight: bold;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 10px;
                padding: 15px;
            }
        """)
        desc_layout = QVBoxLayout()
        
        desc_text = QLabel(
            "• 여기에 설정된 프롬프트 중 하나가 랜덤하게 선택되어 AI에게 전달됩니다.\n"
            "• 프롬프트를 통해 댓글의 성향, 말투, 작성 스타일을 지정할 수 있습니다.\n"
            "• 예시: '~님 말씀처럼...'으로 시작하는 공감하는 말투로 작성해주세요.\n"
            "• 예시: 항상 마지막에 '화이팅!' 이라고 붙여서 작성해주세요."
        )
        desc_text.setStyleSheet("""
            color: #aaaaaa;
            font-size: 12px;
            line-height: 1.5;
        """)
        desc_text.setWordWrap(True)
        desc_layout.addWidget(desc_text)
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        # 프롬프트 리스트 위젯
        list_container = QWidget()
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        # 헤더 영역 (제목 + 총 개수)
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        list_label = QLabel("저장된 프롬프트 목록")
        list_label.setStyleSheet("font-weight: bold; color: white;")
        
        self.total_count_label = QLabel("(총 0개)")
        self.total_count_label.setStyleSheet("color: #aaaaaa;")
        
        header_layout.addWidget(list_label)
        header_layout.addWidget(self.total_count_label)
        header_layout.addStretch()
        
        list_layout.addWidget(header_container)
        
        self.prompt_list = QListWidget()
        self.prompt_list.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                color: white;
                background-color: #353535;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 8px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #404040;
                border: 1px solid #5c85d6;
            }
            QListWidget::item:hover:!selected {
                background-color: #383838;
                border: 1px solid #4a4a4a;
            }
        """)
        
        # 기존 프롬프트 로드
        for prompt in self.prompts:
            self.prompt_list.addItem(prompt)
        self.update_total_count()
            
        list_layout.addWidget(self.prompt_list)
        layout.addWidget(list_container)
        
        # 프롬프트 입력 영역
        input_label = QLabel("새 프롬프트 입력:")
        input_label.setStyleSheet("color: white;")
        layout.addWidget(input_label)
        
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("예: 20대 여성 / 친근하고 활발한 말투 / 10~20자 이내로 작성")
        self.prompt_input.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
                min-height: 60px;
                max-height: 60px;
            }
            QTextEdit:hover {
                border: 1px solid #5c85d6;
            }
        """)
        layout.addWidget(self.prompt_input)
        
        # 버튼 영역
        btn_layout = QHBoxLayout()
        
        # 프롬프트 추가/수정/삭제 버튼
        self.add_btn = QPushButton("추가")
        self.edit_btn = QPushButton("수정")
        self.remove_btn = QPushButton("삭제")
        
        # 버튼 스타일 설정
        button_style = """
            QPushButton {
                background-color: #5c85d6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4a6fb8;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #aaaaaa;
            }
        """
        self.add_btn.setStyleSheet(button_style)
        
        edit_button_style = button_style.replace("#5c85d6", "#4CAF50").replace("#4a6fb8", "#45a049")
        self.edit_btn.setStyleSheet(edit_button_style)
        
        remove_button_style = button_style.replace("#5c85d6", "#d65c5c").replace("#4a6fb8", "#b84a4a")
        self.remove_btn.setStyleSheet(remove_button_style)
        
        # 버튼 이벤트 연결
        self.add_btn.clicked.connect(self.add_prompt)
        self.edit_btn.clicked.connect(self.edit_prompt)
        self.remove_btn.clicked.connect(self.remove_prompt)
        
        # 버튼 초기 상태 설정
        self.edit_btn.setEnabled(False)
        self.remove_btn.setEnabled(False)
        
        # 리스트 선택 변경 이벤트 연결
        self.prompt_list.itemSelectionChanged.connect(self.on_prompt_selection_changed)
        
        # 버튼을 레이아웃에 추가
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # 확인/취소 버튼
        dialog_btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("확인")
        self.cancel_btn = QPushButton("취소")
        
        self.ok_btn.setStyleSheet(button_style)
        self.cancel_btn.setStyleSheet(button_style)
        
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        dialog_btn_layout.addStretch()
        dialog_btn_layout.addWidget(self.ok_btn)
        dialog_btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(dialog_btn_layout)
        
        self.setLayout(layout)
        
    def add_prompt(self):
        """프롬프트 추가"""
        prompt_text = self.prompt_input.toPlainText().strip()
        if not prompt_text:
            return
            
        # 중복 체크
        for i in range(self.prompt_list.count()):
            if self.prompt_list.item(i).text() == prompt_text:
                return
                
        # 프롬프트 추가
        self.prompt_list.addItem(prompt_text)
        self.prompt_input.clear()
        self.update_total_count()
        
        # 입력 필드에 포커스
        self.prompt_input.setFocus()
    
    def edit_prompt(self):
        """선택된 프롬프트 수정"""
        current_item = self.prompt_list.currentItem()
        if current_item:
            prompt_text = self.prompt_input.toPlainText().strip()
            if prompt_text:
                current_item.setText(prompt_text)
                self.prompt_input.clear()
                self.prompt_list.clearSelection()
    
    def remove_prompt(self):
        """선택된 프롬프트 삭제"""
        current_row = self.prompt_list.currentRow()
        if current_row >= 0:
            self.prompt_list.takeItem(current_row)
            self.prompt_input.clear()
            self.prompt_list.clearSelection()
            self.update_total_count()
    
    def on_prompt_selection_changed(self):
        """프롬프트 선택 상태 변경 시 호출"""
        has_selection = bool(self.prompt_list.selectedItems())
        self.edit_btn.setEnabled(has_selection)
        self.remove_btn.setEnabled(has_selection)
        
        if has_selection:
            current_item = self.prompt_list.currentItem()
            self.prompt_input.setPlainText(current_item.text())
        else:
            self.prompt_input.clear()
    
    def update_total_count(self):
        """총 프롬프트 개수 업데이트"""
        count = self.prompt_list.count()
        self.total_count_label.setText(f"(총 {count}개)")
    
    def get_prompts(self):
        """현재 프롬프트 목록 반환"""
        prompts = []
        for i in range(self.prompt_list.count()):
            prompts.append(self.prompt_list.item(i).text())
        return prompts

class CommentSettingWidget(QWidget):
    def __init__(self, log):
        super().__init__()
        self.log = log
        self.prompts = []  # 프롬프트 목록 저장
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 1. AI 프롬프트 설정
        prompt_group = QGroupBox("AI 프롬프트 설정")
        prompt_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-weight: bold;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        
        prompt_layout = QVBoxLayout()
        
        # 프롬프트 개수 표시 레이블
        self.prompt_count_label = QLabel("등록된 프롬프트: 0개")
        self.prompt_count_label.setStyleSheet("color: white;")
        
        # 프롬프트 관리 버튼
        self.manage_prompt_btn = QPushButton("프롬프트 관리")
        self.manage_prompt_btn.setStyleSheet("""
            QPushButton {
                background-color: #5c85d6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                min-width: 120px;
                min-height: 45px;  /* 기존 30px에서 1.5배 증가 */
            }
            QPushButton:hover {
                background-color: #4a6fb8;
            }
        """)
        self.manage_prompt_btn.clicked.connect(self.show_prompt_dialog)
        
        prompt_layout.addWidget(self.prompt_count_label)
        prompt_layout.addWidget(self.manage_prompt_btn)
        prompt_group.setLayout(prompt_layout)
        
        # 2. 댓글 간격 설정
        interval_group = QGroupBox("댓글 간격 설정")
        interval_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-weight: bold;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        
        interval_layout = QVBoxLayout()
        
        interval_desc = QLabel("계정별 댓글 작성 간격을 설정하세요 (초 단위):")
        interval_desc.setStyleSheet("color: white;")
        
        interval_input_layout = QHBoxLayout()
        
        interval_label = QLabel("기본 간격:")
        interval_label.setStyleSheet("color: white;")
        
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(10, 600)  # 10초 ~ 10분
        self.interval_spin.setValue(60)  # 기본값 60초
        self.interval_spin.setSuffix(" 초")
        self.interval_spin.setStyleSheet("""
            QSpinBox {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
                min-width: 80px;
            }
            QSpinBox:hover {
                border: 1px solid #5c85d6;
            }
        """)
        
        interval_range_label = QLabel("오차 범위(±):")
        interval_range_label.setStyleSheet("color: white;")
        
        self.interval_range_spin = QSpinBox()
        self.interval_range_spin.setRange(0, 120)  # 0초 ~ 2분
        self.interval_range_spin.setValue(15)  # 기본값 15초
        self.interval_range_spin.setSuffix(" 초")
        self.interval_range_spin.setStyleSheet("""
            QSpinBox {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
                min-width: 80px;
            }
            QSpinBox:hover {
                border: 1px solid #5c85d6;
            }
        """)
        
        interval_input_layout.addWidget(interval_label)
        interval_input_layout.addWidget(self.interval_spin)
        interval_input_layout.addWidget(interval_range_label)
        interval_input_layout.addWidget(self.interval_range_spin)
        interval_input_layout.addStretch()
        
        interval_layout.addWidget(interval_desc)
        interval_layout.addLayout(interval_input_layout)
        interval_group.setLayout(interval_layout)
        
        # 3. 주요 키워드 설정
        keyword_group = QGroupBox("주요 키워드 설정")
        keyword_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-weight: bold;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        
        keyword_layout = QVBoxLayout()
        
        # 키워드 체크박스와 중복방지 체크박스를 위한 컨테이너
        checkbox_container = QWidget()
        checkbox_layout = QVBoxLayout(checkbox_container)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        checkbox_layout.setSpacing(10)  # 체크박스 간 간격 설정
        
        self.use_keywords = QCheckBox("본문의 주요 키워드를 댓글에 랜덤하게 언급")
        self.use_keywords.setChecked(True)
        
        # 중복방지 체크박스 추가
        self.prevent_duplicate = QCheckBox("댓글 중복 방지")
        self.prevent_duplicate.setChecked(True)
        
        # 체크박스 스타일 설정
        checkbox_style = """
            QCheckBox {
                color: white;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #5c85d6;
                background: #2b2b2b;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #5c85d6;
                background: #5c85d6;
            }
        """
        self.use_keywords.setStyleSheet(checkbox_style)
        self.prevent_duplicate.setStyleSheet(checkbox_style)
        
        checkbox_layout.addWidget(self.use_keywords)
        checkbox_layout.addWidget(self.prevent_duplicate)
        
        keyword_layout.addWidget(checkbox_container)
        keyword_group.setLayout(keyword_layout)
        
        # 메인 레이아웃에 추가
        layout.addWidget(prompt_group)
        layout.addWidget(interval_group)
        layout.addWidget(keyword_group)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # 초기 간격 정보 업데이트
        self.update_interval_info()
    
    def update_interval_info(self):
        """댓글 간격 정보 업데이트"""
        # 랜덤 범위 표시 제거
        pass
    
    def show_prompt_dialog(self):
        """프롬프트 관리 다이얼로그 표시"""
        dialog = PromptDialog(self.prompts, self)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: white;
            }
            QLabel {
                color: white;
            }
        """)
        
        if dialog.exec_():
            # 프롬프트 목록 업데이트
            self.prompts = dialog.get_prompts()
            # 프롬프트 개수 레이블 업데이트
            count = len(self.prompts)
            self.prompt_count_label.setText(f"등록된 프롬프트: {count}개")
            # 로그 추가
            if count > 0:
                self.log.info(f"{count}개의 프롬프트가 등록되었습니다.")
            else:
                self.log.warning("등록된 프롬프트가 없습니다.")
    
    def get_settings(self):
        """댓글 설정 정보 반환"""
        # 댓글 간격 계산
        interval_base = self.interval_spin.value()
        interval_range = self.interval_range_spin.value()
        interval_min = max(0, interval_base - interval_range)
        interval_max = interval_base + interval_range
        
        return {
            'prompts': self.prompts,
            'interval': {
                'base': interval_base,
                'range': interval_range,
                'min': interval_min,
                'max': interval_max
            },
            'use_keywords': self.use_keywords.isChecked(),
            'prevent_duplicate': self.prevent_duplicate.isChecked()
        }
    
    def load_settings(self, settings):
        """설정값 로드"""
        if not settings:
            return
            
        # 프롬프트 설정
        self.prompts = settings.get('prompts', [])
        count = len(self.prompts)
        self.prompt_count_label.setText(f"등록된 프롬프트: {count}개")
        
        # 프롬프트 상태 로그
        if count > 0:
            self.log.info(f"{count}개의 프롬프트가 로드되었습니다.")
        else:
            self.log.warning("등록된 프롬프트가 없습니다.")
        
        # 댓글 간격 설정
        interval = settings.get('interval', {})
        self.interval_spin.setValue(interval.get('base', 60))
        self.interval_range_spin.setValue(interval.get('range', 15))
        
        # 주요 키워드 설정
        self.use_keywords.setChecked(settings.get('use_keywords', True))
        
        # 중복방지 설정
        self.prevent_duplicate.setChecked(settings.get('prevent_duplicate', True))

class ScriptTab(QWidget):
    def __init__(self, log):
        super().__init__()
        self.log = log
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # 설정 탭 위젯
        settings_tab = QTabWidget()
        settings_tab.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
                background: #2b2b2b;
            }
            QTabBar::tab {
                background: #353535;
                color: #cccccc;
                padding: 8px 12px;
                border: 1px solid #3d3d3d;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #2b2b2b;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: #404040;
            }
        """)
        
        # 카페 설정
        self.cafe_widget = CafeWidget(self.log)
        
        # 댓글 설정
        self.comment_widget = CommentSettingWidget(self.log)
        
        # 탭에 위젯 추가
        settings_tab.addTab(self.cafe_widget, "카페 설정")
        settings_tab.addTab(self.comment_widget, "댓글 설정")
        
        layout.addWidget(settings_tab)
        self.setLayout(layout)
        
    def get_comment_settings(self):
        """댓글 설정 정보 반환 (프롬프트 목록과 중복방지 설정)"""
        comment_settings = self.comment_widget.get_settings()
        prompts = comment_settings.get('prompts', [])
        
        # 프롬프트가 비어있는지 확인하고 로그 추가
        if not prompts:
            self.log.warning("AI 프롬프트가 설정되지 않았습니다.")
        
        return {
            'prompts': prompts,
            'prevent_duplicate': comment_settings.get('prevent_duplicate', True)
        }
    
    def get_current_settings(self):
        """현재 설정 정보 반환"""
        return {
            'cafe': self.cafe_widget.get_settings(),
            'comment': self.comment_widget.get_settings()
        }
    
    def load_account_settings(self, account_id):
        """선택된 계정의 설정 로드"""
        # 나중에 구현
        pass
    
    def save_account_settings(self, account_id):
        """현재 설정을 선택된 계정에 저장"""
        # 나중에 구현
        pass
    
    def load_task_settings(self, task_id):
        """작업의 설정값을 UI에 로드"""
        # 나중에 구현
        pass
    
    def save_task_settings(self, task_id):
        """현재 UI 설정값을 작업에 저장"""
        # 나중에 구현
        pass
    
    def load_settings(self, settings):
        """설정값 로드"""
        if not settings:
            return
            
        # 카페 설정 로드
        cafe_settings = settings.get('cafe', {})
        self.cafe_widget.load_settings(cafe_settings)
        
        # 댓글 설정 로드
        comment_settings = settings.get('comment', {})
        self.comment_widget.load_settings(comment_settings) 