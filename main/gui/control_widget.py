from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, 
                           QHBoxLayout, QGroupBox, QRadioButton,
                           QListWidget, QSpinBox, QLabel)
from ..utils.log import Log

class ControlWidget(QWidget):
    def __init__(self, log: Log):
        super().__init__()
        self.log = log
        self.init_ui()

    def init_ui(self):
        group_box = QGroupBox()
        layout = QVBoxLayout()

        # 작업 모드 선택 레이아웃
        mode_layout = QHBoxLayout()
        self.normal_work_btn = QRadioButton('ID별 작업 스크립트 설정')
        self.routine_work_btn = QRadioButton('메인 작업 실행')
        self.normal_work_btn.setChecked(True)
        
        mode_layout.addWidget(self.normal_work_btn)
        mode_layout.addWidget(self.routine_work_btn)
        layout.addLayout(mode_layout)

        # 스크립트 실행 설정
        script_layout = QVBoxLayout()
        self.script_label = QLabel('실행 스크립트 선택')
        self.script_list = QListWidget()
        self.script_list.setSelectionMode(QListWidget.MultiSelection)
        
        # 실행 간격 설정
        interval_layout = QHBoxLayout()
        self.interval_label = QLabel('ID별 스크립트 실행 간격(분)')
        self.min_interval_label = QLabel('MIN')
        self.min_interval_input = QSpinBox()
        self.min_interval_input.setRange(1, 1440)
        self.min_interval_input.setValue(1)
        
        self.max_interval_label = QLabel('MAX')
        self.max_interval_input = QSpinBox()
        self.max_interval_input.setRange(1, 1440)
        self.max_interval_input.setValue(30)

        interval_layout.addWidget(self.min_interval_label)
        interval_layout.addWidget(self.min_interval_input)
        interval_layout.addWidget(self.max_interval_label)
        interval_layout.addWidget(self.max_interval_input)

        # 게시글 생성 제한
        limit_layout = QHBoxLayout()
        self.limit_label = QLabel('게시글 생성 제한 수(개)')
        self.limit_input = QSpinBox()
        self.limit_input.setRange(1, 10000)
        self.limit_input.setValue(1)
        
        limit_layout.addWidget(self.limit_label)
        limit_layout.addWidget(self.limit_input)

        # 실행 모드 선택
        mode_select_layout = QHBoxLayout()
        self.sequential_btn = QRadioButton('순차실행')
        self.concurrent_btn = QRadioButton('동시실행')
        self.concurrent_btn.setChecked(True)
        
        mode_select_layout.addWidget(self.concurrent_btn)
        mode_select_layout.addWidget(self.sequential_btn)

        script_layout.addWidget(self.script_label)
        script_layout.addWidget(self.script_list)
        script_layout.addLayout(interval_layout)
        script_layout.addLayout(limit_layout)
        script_layout.addLayout(mode_select_layout)
        layout.addLayout(script_layout)

        # 실행/정지 버튼 레이아웃
        execute_layout = QHBoxLayout()
        self.execute_btn = QPushButton('실행')
        self.execute_btn.setObjectName('execute')
        self.execute_btn.setFixedHeight(40)
        
        self.stop_btn = QPushButton('정지')
        self.stop_btn.setObjectName('stop')
        self.stop_btn.setFixedHeight(40)

        execute_layout.addWidget(self.execute_btn)
        execute_layout.addWidget(self.stop_btn)

        layout.addLayout(execute_layout)
        
        group_box.setLayout(layout)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(group_box)
        self.setLayout(main_layout)

        # 작업 모드 변경 시 UI 업데이트
        self.normal_work_btn.toggled.connect(self.toggle_work_mode)
        self.routine_work_btn.toggled.connect(self.toggle_work_mode)

    def toggle_work_mode(self, checked):
        # 스크립트 실행 관련 위젯들의 표시 여부 설정
        widgets = [self.script_label, self.script_list, 
                  self.interval_label, self.min_interval_label, self.min_interval_input,
                  self.max_interval_label, self.max_interval_input,
                  self.limit_label, self.limit_input,
                  self.sequential_btn, self.concurrent_btn]
        
        for widget in widgets:
            widget.setVisible(self.routine_work_btn.isChecked()) 