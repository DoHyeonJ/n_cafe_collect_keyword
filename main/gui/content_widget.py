from PyQt5.QtWidgets import (QWidget, QLabel, QTextEdit, QVBoxLayout, 
                           QHBoxLayout, QGroupBox, QLineEdit, QSpinBox, QCheckBox)
from ..utils.log import Log
from .styles import DARK_STYLE

class ContentWidget(QWidget):
    def __init__(self, log: Log):
        super().__init__()
        self.log = log
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 프롬프트 입력
        prompt_group = QGroupBox("AI 프롬프트")
        prompt_layout = QVBoxLayout()
        self.prompt = QTextEdit()
        self.prompt.setPlaceholderText("게시글 생성을 위한 프롬프트를 입력하세요...")
        prompt_layout.addWidget(self.prompt)
        prompt_group.setLayout(prompt_layout)

        # 글자수 설정
        length_group = QGroupBox("글자수 설정")
        length_layout = QHBoxLayout()
        self.min_length = QSpinBox()
        self.max_length = QSpinBox()
        self.min_length.setRange(100, 5000)
        self.max_length.setRange(100, 5000)
        self.min_length.setValue(500)
        self.max_length.setValue(1000)
        length_layout.addWidget(QLabel("최소:"))
        length_layout.addWidget(self.min_length)
        length_layout.addWidget(QLabel("최대:"))
        length_layout.addWidget(self.max_length)
        length_layout.addStretch()
        length_group.setLayout(length_layout)

        # 콘텐츠 수집(중복방지) 설정
        content_collection_group = QGroupBox("콘텐츠 수집(중복방지)")
        content_collection_layout = QHBoxLayout()
        
        # 사용 여부 체크박스
        self.use_content_collection = QCheckBox("사용")
        self.use_content_collection.setChecked(True)  # 기본값은 사용함
        
        # 수집할 게시글 수 설정
        self.content_collection_count = QSpinBox()
        self.content_collection_count.setRange(1, 50)  # 1~50개 범위 설정
        self.content_collection_count.setValue(20)  # 기본값 20
        
        content_collection_layout.addWidget(self.use_content_collection)
        content_collection_layout.addWidget(QLabel("수집할 게시글 수:"))
        content_collection_layout.addWidget(self.content_collection_count)
        content_collection_layout.addStretch()
        content_collection_group.setLayout(content_collection_layout)

        # 스타일 설정
        self.apply_styles()

        # 레이아웃에 위젯 추가
        layout.addWidget(prompt_group)
        layout.addWidget(length_group)
        layout.addWidget(content_collection_group)
        layout.addStretch()
        self.setLayout(layout)

    def apply_styles(self):
        # 스타일 설정 코드...
        pass

    def get_settings(self):
        """콘텐츠 설정 정보 반환"""
        return {
            'prompt': self.prompt.toPlainText(),
            'min_length': self.min_length.value(),
            'max_length': self.max_length.value(),
            'use_content_collection': self.use_content_collection.isChecked(),
            'content_collection_count': self.content_collection_count.value()
        }

    def load_settings(self, settings):
        """설정값 로드"""
        if not settings:
            return
            
        self.prompt.setPlainText(settings.get('prompt', ''))
        self.min_length.setValue(settings.get('min_length', 500))
        self.max_length.setValue(settings.get('max_length', 1000))
        
        # 콘텐츠 수집 설정 로드
        self.use_content_collection.setChecked(settings.get('use_content_collection', True))
        self.content_collection_count.setValue(settings.get('content_collection_count', 20)) 