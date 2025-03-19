from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QCheckBox, QPushButton, QDialog,
                           QTableWidget, QTableWidgetItem, QHeaderView,
                           QTextEdit, QMessageBox, QGroupBox, QGridLayout,
                           QLineEdit, QComboBox, QSizePolicy, QRadioButton,
                           QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class ReplyScenarioDialog(QDialog):
    def __init__(self, parent=None, scenario=None):
        super().__init__(parent)
        self.scenario = scenario or []
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('댓글 시나리오 설정')
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)  # 최소 높이 설정
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 시나리오 테이블
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(['작성자', '내용'])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)  # 행 번호 숨기기
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # 행 단위 선택
        self.table.setSelectionMode(QTableWidget.SingleSelection)  # 단일 선택만 가능
        
        # 테이블 크기 정책 설정
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 테이블 스타일 설정
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b;
                color: white;
                gridline-color: #3d3d3d;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #353535;
                color: white;
                padding: 5px;
                border: 1px solid #3d3d3d;
                font-weight: bold;
            }
            QTableWidget::item {
                color: white;
                padding: 5px;
                border-bottom: 1px solid #3d3d3d;
            }
            QTableWidget::item:selected {
                background-color: #4a6fb8;
                color: white;
            }
            QTableWidget::item:focus {
                color: white;
                selection-color: white;
            }
        """)
        
        # 기존 시나리오 로드
        for step in self.scenario:  # 저장된 시나리오만 로드
            self.add_row(step['writer'], step['content'], step['type'])
        
        # 댓글/대댓글 추가 영역
        input_group = QGroupBox("댓글/대댓글 추가")
        input_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                margin-top: 8px;
                padding: 15px;
            }
        """)
        
        input_layout = QVBoxLayout()
        input_layout.setSpacing(10)
        
        # 상단 선택 영역
        select_layout = QHBoxLayout()
        
        # 댓글 유형 선택
        self.type_combo = QComboBox()
        self.type_combo.addItems(['댓글', '대댓글'])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        
        # 작성자 선택 (대댓글용)
        self.writer_combo = QComboBox()
        self.writer_combo.addItems(['댓글 작성자', '게시글 작성자'])
        self.writer_combo.hide()  # 초기에는 숨김
        
        # 콤보박스 스타일
        combo_style = """
            QComboBox {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3d3d3d;
                padding: 5px;
                min-width: 120px;
                min-height: 30px;
            }
            QComboBox:hover {
                border: 1px solid #5c85d6;
            }
        """
        self.type_combo.setStyleSheet(combo_style)
        self.writer_combo.setStyleSheet(combo_style)
        
        select_layout.addWidget(self.type_combo)
        select_layout.addWidget(self.writer_combo)
        select_layout.addStretch()
        
        # 댓글 타입 선택 라디오 버튼 추가
        type_group = QGroupBox("댓글 작성 방식")
        type_layout = QHBoxLayout()
        
        self.manual_radio = QRadioButton("수동 작성")
        self.ai_radio = QRadioButton("AI 작성")
        self.manual_radio.setChecked(True)  # 기본값은 수동 작성
        
        type_layout.addWidget(self.manual_radio)
        type_layout.addWidget(self.ai_radio)
        type_group.setLayout(type_layout)
        
        # 내용 입력 영역
        content_group = QGroupBox("내용 입력")
        content_layout = QVBoxLayout()
        
        # 직접 입력 영역
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("내용을 입력하세요...")
        self.content_input.setMaximumHeight(80)
        
        # AI 생성 옵션 영역
        self.ai_options = QWidget()
        ai_options_layout = QVBoxLayout()
        
        tone_layout = QHBoxLayout()
        tone_label = QLabel("톤앤매너:")
        self.tone_combo = QComboBox()
        self.tone_combo.addItems(['친근한', '전문적인', '열정적인', '신중한'])
        self.tone_combo.setStyleSheet(combo_style)
        tone_layout.addWidget(tone_label)
        tone_layout.addWidget(self.tone_combo)
        tone_layout.addStretch()
        
        length_layout = QHBoxLayout()
        length_label = QLabel("길이:")
        self.length_combo = QComboBox()
        self.length_combo.addItems(['짧게', '보통', '길게'])
        self.length_combo.setStyleSheet(combo_style)
        length_layout.addWidget(length_label)
        length_layout.addWidget(self.length_combo)
        length_layout.addStretch()
        
        ai_options_layout.addLayout(tone_layout)
        ai_options_layout.addLayout(length_layout)
        self.ai_options.setLayout(ai_options_layout)
        self.ai_options.hide()
        
        content_layout.addWidget(type_group)
        content_layout.addWidget(self.content_input)
        content_layout.addWidget(self.ai_options)
        content_group.setLayout(content_layout)
        
        # 추가 버튼
        add_btn = QPushButton('추가')
        add_btn.setMinimumWidth(80)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #5c85d6;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #4a6fb8;
            }
        """)
        add_btn.clicked.connect(self.add_content)
        
        input_layout.addLayout(select_layout)
        input_layout.addWidget(content_group)
        input_layout.addWidget(add_btn, alignment=Qt.AlignRight)
        input_group.setLayout(input_layout)
        
        # 하단 버튼 영역
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        remove_btn = QPushButton('선택 삭제')
        save_btn = QPushButton('저장')
        cancel_btn = QPushButton('취소')
        
        for btn in [remove_btn, save_btn, cancel_btn]:
            btn.setMinimumWidth(80)
            btn.setMinimumHeight(30)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #353535;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #404040;
                }
                QPushButton:disabled {
                    background-color: #2b2b2b;
                    color: #808080;
                }
            """)
        
        save_btn.setStyleSheet(save_btn.styleSheet().replace("#353535", "#5c85d6").replace("#404040", "#4a6fb8"))
        
        remove_btn.clicked.connect(self.remove_selected_row)
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        remove_btn.setEnabled(False)
        self.remove_btn = remove_btn
        
        btn_layout.addWidget(remove_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        # 메인 레이아웃에 위젯 추가
        layout.addWidget(self.table)
        layout.addWidget(input_group)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # 테이블 선택 이벤트 연결
        self.table.itemSelectionChanged.connect(self.on_selection_changed)

    def on_input_type_changed(self, checked):
        self.content_input.setVisible(self.manual_radio.isChecked())
        self.ai_options.setVisible(self.ai_radio.isChecked())

    def on_type_changed(self, text):
        # 대댓글 선택 시에만 작성자 선택 표시
        self.writer_combo.setVisible(text == '대댓글')

    def add_content(self):
        content_type = self.type_combo.currentText()
        
        # 내용 가져오기
        if self.manual_radio.isChecked():
            content = self.content_input.toPlainText().strip()
            if not content:
                QMessageBox.warning(self, '경고', '내용을 입력해주세요.')
                return
        else:
            # AI 생성 로직
            tone = self.tone_combo.currentText()
            length = self.length_combo.currentText()
            content = f"AI가 생성한 {tone}톤의 {length} 댓글" # 임시
        
        # 선택된 행 다음에 추가
        current_row = self.table.currentRow()
        insert_row = current_row + 1 if current_row >= 0 else self.table.rowCount()
        
        if content_type == '댓글':
            writer = '댓글 작성자'
        else:
            writer = self.writer_combo.currentText()
            content = f'└ {content}'  # 대댓글 들여쓰기
        
        self.add_row(writer, content, 'reply' if content_type == '대댓글' else 'comment', insert_row)
        self.table.selectRow(insert_row)
        
        # 입력 필드 초기화
        self.content_input.clear()

    def add_row(self, writer, content, content_type, row=None):
        if row is None:
            row = self.table.rowCount()
        
        self.table.insertRow(row)
        
        # 작성자 항목 생성 및 편집 불가 설정
        writer_item = QTableWidgetItem(writer)
        writer_item.setFlags(writer_item.flags() & ~Qt.ItemIsEditable)
        writer_item.setTextAlignment(Qt.AlignCenter)
        writer_item.setForeground(Qt.white)
        
        # 내용 항목 생성
        content_item = QTableWidgetItem(content)
        content_item.setForeground(Qt.white)
        
        # 작성자와 내용을 테이블에 설정
        self.table.setItem(row, 0, writer_item)
        self.table.setItem(row, 1, content_item)
        
        # 스타일 설정
        if writer == '게시글 작성자':
            writer_item.setBackground(Qt.darkGreen)
        else:  # 댓글 작성자
            writer_item.setBackground(Qt.darkBlue)

    def remove_selected_row(self):
        if selected_items := self.table.selectedItems():
            row = selected_items[0].row()
            self.table.removeRow(row)
            
            # 삭제 후 이전 행 선택
            new_row = min(row, self.table.rowCount() - 1)
            if new_row >= 0:
                self.table.selectRow(new_row)

    def on_selection_changed(self):
        # 모든 행 삭제 가능하도록 수정
        selected = bool(self.table.selectedItems())
        self.remove_btn.setEnabled(selected)

    def get_scenario(self):
        scenario = []
        for row in range(self.table.rowCount()):
            writer = self.table.item(row, 0).text()
            content = self.table.item(row, 1).text()
            # 대댓글 여부는 내용의 시작 문자로 판단
            content_type = 'reply' if content.startswith('└') else 'comment'
            scenario.append({
                'writer': writer,
                'content': content,
                'type': content_type
            })
        return scenario

    def add_comment(self):
        """댓글 추가"""
        content = self.content_input.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, '경고', '댓글 내용을 입력해주세요.')
            return
            
        # 댓글 타입 결정
        comment_type = "comment-ai" if self.ai_radio.isChecked() else "comment-manual"
        
        # 댓글 정보 생성
        comment = {
            'type': comment_type,
            'content': content,
            'nickname': self.nickname_input.text() if self.use_nickname.isChecked() else ""
        }
        
        # 시나리오에 추가
        self.scenario.append(comment)
        
        # 목록에 표시
        item = QListWidgetItem(f"[댓글] {content[:30]}..." if len(content) > 30 else f"[댓글] {content}")
        if comment_type == "comment-ai":
            item.setIcon(QIcon("icons/ai_icon.png"))  # AI 아이콘 추가
        self.comment_list.addItem(item)
        
        # 입력 필드 초기화
        self.content_input.clear()
        self.nickname_input.clear()
        
    def add_reply(self):
        """대댓글 추가"""
        if not self.comment_list.currentItem():
            QMessageBox.warning(self, '경고', '대댓글을 달 댓글을 선택해주세요.')
            return
            
        content = self.content_input.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, '경고', '대댓글 내용을 입력해주세요.')
            return
            
        # 선택된 댓글 인덱스
        parent_idx = self.comment_list.currentRow()
        
        # 대댓글 타입 결정
        reply_type = "reply-ai" if self.ai_radio.isChecked() else "reply-manual"
        
        # 대댓글 정보 생성
        reply = {
            'type': reply_type,
            'parent_idx': parent_idx,
            'content': content,
            'nickname': self.nickname_input.text() if self.use_nickname.isChecked() else ""
        }
        
        # 시나리오에 추가
        self.scenario.append(reply)
        
        # 목록에 표시 (들여쓰기로 대댓글 표시)
        item = QListWidgetItem(f"  ↳ [대댓글] {content[:30]}..." if len(content) > 30 else f"  ↳ [대댓글] {content}")
        if reply_type == "reply-ai":
            item.setIcon(QIcon("icons/ai_icon.png"))  # AI 아이콘 추가
        self.comment_list.addItem(item)
        
        # 입력 필드 초기화
        self.content_input.clear()
        self.nickname_input.clear()

class ReplySettingWidget(QWidget):
    def __init__(self, log):
        super().__init__()
        self.log = log
        self.scenario = []  # 댓글 시나리오 저장
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 체크박스 스타일 통일
        checkbox_style = """
            QCheckBox {
                color: white;
                spacing: 8px;
                min-height: 30px;
                min-width: 150px;
                padding: 5px 10px;
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
            }
            QCheckBox:hover {
                background-color: #353535;
                border: 1px solid #5c85d6;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #5c85d6;
                background: transparent;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #5c85d6;
                background: #5c85d6;
                border-radius: 4px;
            }
        """
        
        # 체크박스 컨테이너
        checkbox_container = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_container)
        checkbox_layout.setContentsMargins(0, 5, 0, 5)
        checkbox_layout.setSpacing(10)
        
        # 댓글 사용 여부 & 닉네임 변경
        self.use_reply = QCheckBox("댓글 기능 사용")
        self.use_reply.setStyleSheet(checkbox_style)
        
        self.use_nickname = QCheckBox("닉네임 변경 사용")
        self.use_nickname.setChecked(True)
        self.use_nickname.setStyleSheet(checkbox_style)
        
        # 체크박스 레이아웃에 추가
        checkbox_layout.addWidget(self.use_reply)
        checkbox_layout.addWidget(self.use_nickname)
        checkbox_layout.addStretch()
        
        # 댓글 설정 영역
        self.reply_settings = QWidget()
        reply_settings_layout = QVBoxLayout()
        
        # 댓글 계정 설정
        account_group = QGroupBox("댓글 작성 계정")
        account_layout = QGridLayout()
        
        # ID 입력
        id_label = QLabel("아이디:")
        self.id_input = QLineEdit()
        account_layout.addWidget(id_label, 0, 0)
        account_layout.addWidget(self.id_input, 0, 1)
        
        # PW 입력
        pw_label = QLabel("비밀번호:")
        self.pw_input = QLineEdit()
        self.pw_input.setEchoMode(QLineEdit.Password)
        account_layout.addWidget(pw_label, 1, 0)
        account_layout.addWidget(self.pw_input, 1, 1)
        
        account_group.setLayout(account_layout)
        
        # 시나리오 설정 버튼
        self.scenario_btn = QPushButton("시나리오 상세 설정")
        self.scenario_btn.setStyleSheet("""
            QPushButton {
                background-color: #5c85d6;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #4a6fb8;
            }
            QPushButton:disabled {
                background-color: #3d3d3d;
                color: #808080;
            }
        """)
        self.scenario_btn.clicked.connect(self.show_scenario_dialog)
        
        reply_settings_layout.addWidget(account_group)
        reply_settings_layout.addWidget(self.scenario_btn)
        self.reply_settings.setLayout(reply_settings_layout)
        
        # 초기 상태 설정
        self.reply_settings.setEnabled(False)
        self.use_reply.stateChanged.connect(self.on_use_reply_changed)
        
        layout.addWidget(checkbox_container)
        layout.addWidget(self.reply_settings)
        layout.addStretch()
        self.setLayout(layout)

    def get_settings(self):
        """댓글 설정 정보 반환"""
        return {
            'use_reply': self.use_reply.isChecked(),
            'use_nickname': self.use_nickname.isChecked(),
            'account': {
                'id': self.id_input.text(),
                'pw': self.pw_input.text()
            },
            'scenario': self.scenario
        }

    def load_settings(self, settings):
        self.use_reply.setChecked(settings.get('use_reply', False))
        self.use_nickname.setChecked(settings.get('use_nickname', True))
        account = settings.get('account', {})
        self.id_input.setText(account.get('id', ''))
        self.pw_input.setText(account.get('pw', ''))
        self.scenario = settings.get('scenario', [])

    def show_scenario_dialog(self):
        dialog = ReplyScenarioDialog(self, self.scenario)
        if dialog.exec_():
            self.scenario = dialog.get_scenario()

    def on_use_reply_changed(self, state):
        self.reply_settings.setEnabled(state == Qt.Checked)

    def get_settings(self):
        return {
            'use_reply': self.use_reply.isChecked(),
            'use_nickname': self.use_nickname.isChecked(),
            'account': {
                'id': self.id_input.text(),
                'pw': self.pw_input.text()
            },
            'scenario': self.scenario
        }

    def load_settings(self, settings):
        self.use_reply.setChecked(settings.get('use_reply', False))
        self.use_nickname.setChecked(settings.get('use_nickname', True))
        account = settings.get('account', {})
        self.id_input.setText(account.get('id', ''))
        self.pw_input.setText(account.get('pw', ''))
        self.scenario = settings.get('scenario', []) 