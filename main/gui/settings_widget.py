from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, 
                           QHBoxLayout, QGroupBox, QLabel, QLineEdit,
                           QComboBox, QCheckBox, QRadioButton, QButtonGroup,
                           QGridLayout, QFrame, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt
from ..utils.log import Log

class SettingsWidget(QWidget):
    def __init__(self, log: Log):
        super().__init__()
        self.log = log
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # 1. 검색 키워드 입력 영역
        keyword_group = QGroupBox("검색 키워드")
        keyword_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #3d3d3d;
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
        
        keyword_layout = QVBoxLayout()
        
        # 검색 키워드 입력
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("검색할 키워드를 입력하세요 (여러 키워드는 쉼표로 구분)")
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
        
        keyword_layout.addWidget(self.keyword_input)
        keyword_group.setLayout(keyword_layout)
        
        # 2. 검색 옵션 영역
        options_group = QGroupBox("검색 옵션")
        options_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #3d3d3d;
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
        
        options_layout = QGridLayout()
        options_layout.setVerticalSpacing(15)
        options_layout.setHorizontalSpacing(20)
        
        # 콤보박스 공통 스타일
        combo_style = """
            QComboBox {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3d3d3d;
                padding: 5px;
                border-radius: 4px;
                min-height: 30px;
            }
            QComboBox:hover {
                border: 1px solid #5c85d6;
            }
            QComboBox QAbstractItemView {
                background-color: #2b2b2b;
                color: white;
                selection-background-color: #5c85d6;
                selection-color: white;
                border: 1px solid #5c85d6;
            }
        """
        
        # 2.1 대상 선택
        target_label = QLabel("대상:")
        target_label.setStyleSheet("color: white;")
        self.target_combo = QComboBox()
        self.target_combo.addItems(["전체글", "거래글", "일반글", "카페명"])
        self.target_combo.setStyleSheet(combo_style)
        options_layout.addWidget(target_label, 0, 0)
        options_layout.addWidget(self.target_combo, 0, 1)
        
        # 2.2 정렬 방식
        sort_label = QLabel("정렬:")
        sort_label.setStyleSheet("color: white;")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["관련도순", "최신순"])
        self.sort_combo.setStyleSheet(combo_style)
        options_layout.addWidget(sort_label, 0, 2)
        options_layout.addWidget(self.sort_combo, 0, 3)
        
        # 2.3 검색 기간
        period_label = QLabel("기간:")
        period_label.setStyleSheet("color: white;")
        self.period_combo = QComboBox()
        self.period_combo.addItems(["전체", "1시간", "1일", "1주", "1개월", "3개월", "6개월", "1년"])
        self.period_combo.setStyleSheet(combo_style)
        options_layout.addWidget(period_label, 1, 0)
        options_layout.addWidget(self.period_combo, 1, 1)
        
        # 2.4 거래 방법
        payment_label = QLabel("거래방법:")
        payment_label.setStyleSheet("color: white;")
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["전체", "안전결제", "일반결제"])
        self.payment_combo.setStyleSheet(combo_style)
        options_layout.addWidget(payment_label, 1, 2)
        options_layout.addWidget(self.payment_combo, 1, 3)
        
        # 2.5 거래 상태
        status_label = QLabel("거래상태:")
        status_label.setStyleSheet("color: white;")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["전체", "판매중", "판매완료"])
        self.status_combo.setStyleSheet(combo_style)
        options_layout.addWidget(status_label, 2, 0)
        options_layout.addWidget(self.status_combo, 2, 1)
        
        options_group.setLayout(options_layout)
        
        # 3. AI 분석 키워드 영역
        ai_group = QGroupBox("AI 분석 설정")
        ai_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #3d3d3d;
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
        
        ai_layout = QVBoxLayout()
        
        # AI 분석 사용 체크박스
        self.use_ai_analysis = QCheckBox("AI 분석 사용")
        self.use_ai_analysis.setStyleSheet("""
            QCheckBox {
                color: white;
                min-height: 25px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #5c85d6;
                background: transparent;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #5c85d6;
                background: #5c85d6;
            }
        """)
        
        # AI API 키 입력
        api_key_layout = QHBoxLayout()
        api_key_label = QLabel("AI API 키:")
        api_key_label.setStyleSheet("color: white;")
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("OpenAI API 키를 입력하세요")
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
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        
        # AI 분석 키워드 입력
        ai_keyword_layout = QVBoxLayout()
        ai_keyword_label = QLabel("AI 분석 키워드 (예: 가격, 브랜드, 기능):")
        ai_keyword_label.setStyleSheet("color: white;")
        self.ai_keyword_input = QLineEdit()
        self.ai_keyword_input.setPlaceholderText("분석할 키워드를 입력하세요 (여러 키워드는 쉼표로 구분)")
        self.ai_keyword_input.setStyleSheet("""
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
        ai_keyword_layout.addWidget(ai_keyword_label)
        ai_keyword_layout.addWidget(self.ai_keyword_input)
        
        ai_layout.addWidget(self.use_ai_analysis)
        ai_layout.addLayout(api_key_layout)
        ai_layout.addLayout(ai_keyword_layout)
        
        ai_group.setLayout(ai_layout)
        
        # 설정 상태 변경 이벤트 연결
        self.use_ai_analysis.stateChanged.connect(self.on_ai_analysis_changed)
        
        # 4. 설정 버튼 영역
        buttons_layout = QHBoxLayout()
        
        self.save_btn = QPushButton('설정 저장')
        self.load_btn = QPushButton('설정 불러오기')
        self.reset_btn = QPushButton('설정 초기화')
        
        # 버튼 스타일
        button_style = """
            QPushButton {
                background-color: #5c85d6;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: 120px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #4a6fb8;
            }
        """
        self.save_btn.setStyleSheet(button_style)
        self.load_btn.setStyleSheet(button_style)
        self.reset_btn.setStyleSheet(button_style.replace('#5c85d6', '#d65c5c').replace('#4a6fb8', '#b84a4a'))
        
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.load_btn)
        buttons_layout.addWidget(self.reset_btn)
        buttons_layout.addStretch()
        
        # 레이아웃 구성
        main_layout.addWidget(keyword_group)
        main_layout.addWidget(options_group)
        main_layout.addWidget(ai_group)
        main_layout.addLayout(buttons_layout)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
        # 초기 상태 설정
        self.on_ai_analysis_changed(self.use_ai_analysis.checkState())
    
    def on_ai_analysis_changed(self, state):
        """AI 분석 사용 여부에 따라 관련 입력 필드 활성화/비활성화"""
        is_enabled = state == Qt.Checked
        self.api_key_input.setEnabled(is_enabled)
        self.ai_keyword_input.setEnabled(is_enabled)
    
    def get_settings(self):
        """설정 정보 반환"""
        # 검색 키워드 분리 (쉼표 기준)
        search_keywords = [k.strip() for k in self.keyword_input.text().split(',') if k.strip()]
        
        # AI 분석 키워드 분리 (쉼표 기준)
        ai_keywords = []
        if self.use_ai_analysis.isChecked():
            ai_keywords = [k.strip() for k in self.ai_keyword_input.text().split(',') if k.strip()]
        
        return {
            'search_keywords': search_keywords,
            'target': self.target_combo.currentText(),
            'sort': self.sort_combo.currentText(),
            'period': self.period_combo.currentText(),
            'payment_method': self.payment_combo.currentText(),
            'status': self.status_combo.currentText(),
            'use_ai_analysis': self.use_ai_analysis.isChecked(),
            'api_key': self.api_key_input.text() if self.use_ai_analysis.isChecked() else '',
            'ai_keywords': ai_keywords
        }
    
    def load_settings(self, settings):
        """설정 불러오기"""
        # 검색 키워드 설정
        if 'search_keywords' in settings:
            self.keyword_input.setText(', '.join(settings['search_keywords']))
        
        # 콤보박스 설정
        if 'target' in settings:
            index = self.target_combo.findText(settings['target'])
            if index >= 0:
                self.target_combo.setCurrentIndex(index)
        
        if 'sort' in settings:
            index = self.sort_combo.findText(settings['sort'])
            if index >= 0:
                self.sort_combo.setCurrentIndex(index)
        
        if 'period' in settings:
            index = self.period_combo.findText(settings['period'])
            if index >= 0:
                self.period_combo.setCurrentIndex(index)
        
        if 'payment_method' in settings:
            index = self.payment_combo.findText(settings['payment_method'])
            if index >= 0:
                self.payment_combo.setCurrentIndex(index)
        
        if 'status' in settings:
            index = self.status_combo.findText(settings['status'])
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
        
        # AI 분석 설정
        self.use_ai_analysis.setChecked(settings.get('use_ai_analysis', False))
        self.api_key_input.setText(settings.get('api_key', ''))
        if 'ai_keywords' in settings:
            self.ai_keyword_input.setText(', '.join(settings['ai_keywords']))
        
        # AI 분석 사용 여부에 따른 UI 업데이트
        self.on_ai_analysis_changed(self.use_ai_analysis.checkState())
    
    def reset_settings(self):
        """설정 초기화"""
        self.keyword_input.clear()
        self.target_combo.setCurrentIndex(0)
        self.sort_combo.setCurrentIndex(0)
        self.period_combo.setCurrentIndex(0)
        self.payment_combo.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
        self.use_ai_analysis.setChecked(False)
        self.api_key_input.clear()
        self.ai_keyword_input.clear()
        
        # AI 분석 사용 여부에 따른 UI 업데이트
        self.on_ai_analysis_changed(self.use_ai_analysis.checkState()) 