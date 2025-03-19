from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QComboBox, QCheckBox, QGroupBox,
                           QSpinBox, QPushButton, QMessageBox, QDialog, QListWidget, QFrame)
from PyQt5.QtCore import Qt
from ..utils.log import Log
from .styles import DARK_STYLE
from ..api.cafe import CafeAPI

class CafeWidget(QWidget):
    def __init__(self, log):
        super().__init__()
        self.log = log
        self.cafe_list = []
        self.headers = None
        self.current_boards = []
        self.current_headers = None
        self.current_cafe_id = None 
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 카페 선택
        cafe_label = QLabel("카페 선택")
        cafe_label.setStyleSheet("color: white; font-weight: bold;")
        
        self.cafe_combo = QComboBox()
        self.cafe_combo.setMinimumWidth(250)  # 너비 축소
        self.cafe_combo.currentIndexChanged.connect(self.on_cafe_selected)
        
        # 게시판 선택
        board_label = QLabel("게시판 선택")
        board_label.setStyleSheet("color: white; font-weight: bold;")
        
        self.board_combo = QComboBox()
        self.board_combo.setMinimumWidth(250)  # 너비 축소
        
        # 기본 레이아웃 구성
        basic_layout = QVBoxLayout()
        basic_layout.addWidget(cafe_label)
        basic_layout.addWidget(self.cafe_combo)
        basic_layout.addWidget(board_label)
        basic_layout.addWidget(self.board_combo)
        
        # 구분선 추가
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #3d3d3d;")
        
        # 작업 설정 그룹박스
        work_settings = QGroupBox("작업 설정")
        work_settings.setStyleSheet("""
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
        
        work_layout = QVBoxLayout()
        
        # 1. 게시판별 수집 게시글 수
        post_count_layout = QHBoxLayout()
        post_count_label = QLabel("게시판별 수집 게시글 수:")
        post_count_label.setStyleSheet("color: white;")
        
        self.post_count_spin = QSpinBox()
        self.post_count_spin.setRange(1, 100)
        self.post_count_spin.setValue(10)
        self.post_count_spin.setStyleSheet("""
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
        
        post_count_layout.addWidget(post_count_label)
        post_count_layout.addWidget(self.post_count_spin)
        post_count_layout.addStretch()
        
        # 2. 게시글별 댓글 작업 수
        comment_count_layout = QHBoxLayout()
        comment_count_label = QLabel("게시글별 댓글 작업 수:")
        comment_count_label.setStyleSheet("color: white;")
        
        self.comment_count_spin = QSpinBox()
        self.comment_count_spin.setRange(0, 50)
        self.comment_count_spin.setValue(5)
        self.comment_count_spin.setStyleSheet("""
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
        
        comment_range_label = QLabel("범위(±):")
        comment_range_label.setStyleSheet("color: white;")
        
        self.comment_range_spin = QSpinBox()
        self.comment_range_spin.setRange(0, 10)
        self.comment_range_spin.setValue(2)
        self.comment_range_spin.setStyleSheet("""
            QSpinBox {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
                min-width: 60px;
            }
            QSpinBox:hover {
                border: 1px solid #5c85d6;
            }
        """)
        
        # comment_range_info = QLabel("(3~7 랜덤)")
        # comment_range_info.setStyleSheet("color: #aaaaaa; font-style: italic;")
        
        comment_count_layout.addWidget(comment_count_label)
        comment_count_layout.addWidget(self.comment_count_spin)
        comment_count_layout.addWidget(comment_range_label)
        comment_count_layout.addWidget(self.comment_range_spin)
        # comment_count_layout.addWidget(comment_range_info)
        comment_count_layout.addStretch()
        
        # 댓글 범위 변경 시 정보 업데이트
        self.comment_count_spin.valueChanged.connect(self.update_comment_range_info)
        self.comment_range_spin.valueChanged.connect(self.update_comment_range_info)
        
        # 3. 게시글별 좋아요 작업 수
        like_count_layout = QHBoxLayout()
        like_count_label = QLabel("게시글별 좋아요 작업 수:")
        like_count_label.setStyleSheet("color: white;")
        
        self.like_count_spin = QSpinBox()
        self.like_count_spin.setRange(0, 50)
        self.like_count_spin.setValue(3)
        self.like_count_spin.setStyleSheet("""
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
        
        like_range_label = QLabel("범위(±):")
        like_range_label.setStyleSheet("color: white;")
        
        self.like_range_spin = QSpinBox()
        self.like_range_spin.setRange(0, 10)
        self.like_range_spin.setValue(1)
        self.like_range_spin.setStyleSheet("""
            QSpinBox {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
                min-width: 60px;
            }
            QSpinBox:hover {
                border: 1px solid #5c85d6;
            }
        """)
        
        # like_range_info = QLabel("(2~4 랜덤)")
        # like_range_info.setStyleSheet("color: #aaaaaa; font-style: italic;")
        
        like_count_layout.addWidget(like_count_label)
        like_count_layout.addWidget(self.like_count_spin)
        like_count_layout.addWidget(like_range_label)
        like_count_layout.addWidget(self.like_range_spin)
        # like_count_layout.addWidget(like_range_info)
        like_count_layout.addStretch()
        
        # 좋아요 범위 변경 시 정보 업데이트
        self.like_count_spin.valueChanged.connect(self.update_like_range_info)
        self.like_range_spin.valueChanged.connect(self.update_like_range_info)
        
        # 작업 설정 레이아웃에 추가
        work_layout.addLayout(post_count_layout)
        work_layout.addLayout(comment_count_layout)
        work_layout.addLayout(like_count_layout)
        
        work_settings.setLayout(work_layout)
        
        # 메인 레이아웃에 추가
        layout.addLayout(basic_layout)
        layout.addWidget(separator)
        layout.addWidget(work_settings)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # 초기 범위 정보 업데이트
        self.update_comment_range_info()
        self.update_like_range_info()
    
    def update_comment_range_info(self):
        """댓글 범위 정보 업데이트"""
        base = self.comment_count_spin.value()
        range_val = self.comment_range_spin.value()
        min_val = max(0, base - range_val)
        max_val = base + range_val
        
        # 레이아웃에서 정보 라벨 찾기
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if isinstance(item, QHBoxLayout):
                for j in range(item.count()):
                    widget = item.itemAt(j).widget()
                    if isinstance(widget, QLabel) and "(3~7 랜덤)" in widget.text():
                        widget.setText(f"({min_val}~{max_val} 랜덤)")
                        return
    
    def update_like_range_info(self):
        """좋아요 범위 정보 업데이트"""
        base = self.like_count_spin.value()
        range_val = self.like_range_spin.value()
        min_val = max(0, base - range_val)
        max_val = base + range_val
        
        # 레이아웃에서 정보 라벨 찾기
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if isinstance(item, QHBoxLayout):
                for j in range(item.count()):
                    widget = item.itemAt(j).widget()
                    if isinstance(widget, QLabel) and "(2~4 랜덤)" in widget.text():
                        widget.setText(f"({min_val}~{max_val} 랜덤)")
                        return
    
    def update_cafe_list(self, cafe_list, headers):
        """카페 목록 업데이트"""
        self.cafe_list = cafe_list
        self.headers = headers
        
        # 카페 콤보박스 초기화
        self.cafe_combo.clear()
        
        # 카페 목록 추가
        if cafe_list:
            # 데이터 형식 확인
            if isinstance(cafe_list[0], tuple):
                # 튜플 형식 (cafe_id, cafe_url, cafe_name)
                for cafe_id, cafe_url, cafe_name in cafe_list:
                    self.cafe_combo.addItem(cafe_name, cafe_id)
                    # 내부 저장용 리스트 형식 변환
                    if not isinstance(self.cafe_list[0], dict):
                        self.cafe_list = [
                            {'cafe_id': cid, 'cafe_url': curl, 'cafe_name': cname}
                            for cid, curl, cname in cafe_list
                        ]
            else:
                # 딕셔너리 형식
                for cafe in cafe_list:
                    self.cafe_combo.addItem(cafe['cafe_name'], cafe['cafe_id'])
            
        # 첫 번째 카페 선택 (있는 경우)
        if self.cafe_combo.count() > 0:
            self.cafe_combo.setCurrentIndex(0)
            self.on_cafe_selected(0)
    
    def on_cafe_selected(self, index):
        """카페 선택 시 게시판 목록 업데이트"""
        if index < 0 or not self.headers:
            return
            
        cafe_id = self.cafe_combo.currentData()
        if not cafe_id:
            return
            
        self.current_cafe_id = cafe_id
        
        # 게시판 목록 가져오기
        cafe_api = CafeAPI(self.headers)
        board_list = cafe_api.get_board_list(cafe_id)
        
        # 게시판 목록 업데이트
        self.board_combo.clear()
        self.current_boards = board_list
        
        if board_list:
            for board in board_list:
                self.board_combo.addItem(board['board_name'], board['board_id'])
    
    def get_selected_cafe(self):
        """선택된 카페 정보 반환"""
        if self.cafe_combo.count() == 0:
            return None
            
        cafe_id = self.cafe_combo.currentData()
        cafe_name = self.cafe_combo.currentText()
        
        for cafe in self.cafe_list:
            if cafe['cafe_id'] == cafe_id:
                return cafe
                
        return None
    
    def get_selected_board(self):
        """선택된 게시판 정보 반환"""
        if self.board_combo.count() == 0:
            return None
            
        board_id = self.board_combo.currentData()
        board_name = self.board_combo.currentText()
        
        if not self.current_boards:
            return None
            
        for board in self.current_boards:
            if board['board_id'] == board_id:
                return board
                
        return None
    
    def get_settings(self):
        """카페 설정 정보 반환"""
        selected_cafe = self.get_selected_cafe()
        selected_board = self.get_selected_board()
        
        if not selected_cafe or not selected_board:
            return {}
            
        # 댓글 범위 계산
        comment_base = self.comment_count_spin.value()
        comment_range = self.comment_range_spin.value()
        comment_min = max(0, comment_base - comment_range)
        comment_max = comment_base + comment_range
        
        # 좋아요 범위 계산
        like_base = self.like_count_spin.value()
        like_range = self.like_range_spin.value()
        like_min = max(0, like_base - like_range)
        like_max = like_base + like_range
        
        return {
            'cafe_id': selected_cafe['cafe_id'],
            'cafe_name': selected_cafe['cafe_name'],
            'cafe_url': selected_cafe['cafe_url'],
            'board_id': selected_board['board_id'],
            'board_name': selected_board['board_name'],
            'post_count': self.post_count_spin.value(),
            'comment_count': {
                'base': comment_base,
                'range': comment_range,
                'min': comment_min,
                'max': comment_max
            },
            'like_count': {
                'base': like_base,
                'range': like_range,
                'min': like_min,
                'max': like_max
            }
        }
    
    def load_settings(self, settings):
        """설정값 로드"""
        # 카페 설정
        cafe_name = settings.get('cafe_name', '')
        index = self.cafe_combo.findText(cafe_name)
        if index >= 0:
            self.cafe_combo.setCurrentIndex(index)
        
        # 게시판 설정
        board_name = settings.get('board_name', '')
        index = self.board_combo.findText(board_name)
        if index >= 0:
            self.board_combo.setCurrentIndex(index)
            
        # 게시글 수 설정
        self.post_count_spin.setValue(settings.get('post_count', 10))
        
        # 댓글 작업 수 설정
        comment_count = settings.get('comment_count', {})
        self.comment_count_spin.setValue(comment_count.get('base', 5))
        self.comment_range_spin.setValue(comment_count.get('range', 2))
        
        # 좋아요 작업 수 설정
        like_count = settings.get('like_count', {})
        self.like_count_spin.setValue(like_count.get('base', 3))
        self.like_range_spin.setValue(like_count.get('range', 1))
    
    def clear_settings(self):
        """설정 초기화"""
        self.cafe_combo.clear()
        self.board_combo.clear()
        self.cafe_list = []
        self.headers = None
        self.current_boards = []
        self.current_headers = None
        self.current_cafe_id = None
        
        # 작업 설정 초기화
        self.post_count_spin.setValue(10)
        self.comment_count_spin.setValue(5)
        self.comment_range_spin.setValue(2)
        self.like_count_spin.setValue(3)
        self.like_range_spin.setValue(1) 