import logging
import os
from datetime import datetime

class Log:
    def __init__(self):
        self.messages = []
        self.board_logs = {}  # {cafe_id: {article_id: {subject, writer}}}
        self.task_logs = []  # [{subject, cafe_id, content, ...}]
        self.row_positions = {}  # {task_id: row_position}
        
        # 로그 파일 설정
        self.setup_file_logger()
        
    def setup_file_logger(self):
        """파일 로깅 설정"""
        try:
            # 현재 날짜 가져오기
            now = datetime.now()
            year = now.strftime("%Y")
            month = now.strftime("%m")
            date = now.strftime("%Y-%m-%d")
            
            # 로그 디렉토리 생성
            log_dir = os.path.join("logs", f"{year}-{month}")
            os.makedirs(log_dir, exist_ok=True)
            
            # 로그 파일 경로
            log_file = os.path.join(log_dir, f"sys_log_{date}.log")
            
            # 로거 설정
            self.file_logger = logging.getLogger('SystemLogger')
            self.file_logger.setLevel(logging.DEBUG)  # DEBUG 레벨로 설정하여 모든 로그 수집
            
            # 기존 핸들러 제거 (중복 방지)
            if self.file_logger.handlers:
                self.file_logger.handlers.clear()
            
            # 파일 핸들러 추가 - UTF-8 인코딩 설정
            file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # 로그 포맷 설정
            formatter = logging.Formatter(
                '[%(asctime)s] %(levelname)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            self.file_logger.addHandler(file_handler)
            
            # 초기 로그 메시지
            self.file_logger.info("=== 로그 시스템 초기화 ===")
            self.file_logger.info(f"로그 파일 경로: {os.path.abspath(log_file)}")
            self.file_logger.info(f"로그 레벨: DEBUG")
            
        except Exception as e:
            import traceback
            print(f"로거 설정 실패: {traceback.format_exc()}")
            raise

    def add_log(self, message, color="black"):
        """일반 로그 메시지 추가"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = {
                'timestamp': timestamp,
                'message': message,
                'color': color
            }
            self.messages.append(log_entry)
            
            # 파일에 로그 기록
            try:
                # 메시지를 문자열로 변환하고 명시적으로 인코딩 처리
                message_str = str(message)
                if color == "red":
                    self.file_logger.error(message_str)
                elif color == "orange" or color == "yellow":
                    self.file_logger.warning(message_str)
                elif color == "green":
                    self.file_logger.info(f"[성공] {message_str}")
                elif color == "blue":
                    self.file_logger.info(f"[정보] {message_str}")
                else:
                    self.file_logger.info(message_str)
            except Exception as e:
                print(f"로그 기록 실패: {str(e)}")
                
            return log_entry
        except Exception as e:
            print(f"로그 추가 중 오류 발생: {str(e)}")
            return {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'message': str(message),
                'color': color
            }

    def info(self, message):
        """정보 로그 추가 (파란색)"""
        return self.add_log(message, "blue")

    def error(self, message):
        """에러 로그 추가 (빨간색)"""
        return self.add_log(message, "red")

    def warning(self, message):
        """경고 로그 추가 (주황색)"""
        return self.add_log(message, "orange")

    def success(self, message):
        """성공 로그 추가 (녹색)"""
        return self.add_log(message, "green")

    def add_board_log(self, cafe_id, article_id, subject, writer):
        """게시판 로그 추가"""
        if cafe_id not in self.board_logs:
            self.board_logs[cafe_id] = {}
        
        self.board_logs[cafe_id][article_id] = {
            'subject': subject,
            'writer': writer
        }
        
        # 파일에 로그 기록
        try:
            self.file_logger.info(f"게시판 로그: 카페ID={cafe_id}, 게시글ID={article_id}, 제목={subject}, 작성자={writer}")
        except Exception as e:
            print(f"게시판 로그 기록 실패: {str(e)}")

    def add_task_log(self, subject, cafe_id, content, reply_id="", reply_content="", 
                     reply_writer="", reply_pw="", article_url="", row_position=None):
        """작업 로그 추가"""
        task_log = {
            'subject': subject,
            'cafe_id': cafe_id,
            'content': content,
            'reply_id': reply_id,
            'reply_content': reply_content,
            'reply_writer': reply_writer,
            'reply_pw': reply_pw,
            'article_url': article_url,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if row_position is not None:
            self.row_positions[len(self.task_logs)] = row_position
            
        self.task_logs.append(task_log)
        
        # 파일에 로그 기록
        try:
            self.file_logger.info(f"작업 로그: 제목={subject}, 카페ID={cafe_id}, URL={article_url}")
        except Exception as e:
            print(f"작업 로그 기록 실패: {str(e)}")
        
        return row_position

    def set_read_onry_col(self, row_position, col, value):
        """특정 셀을 읽기 전용으로 설정"""
        # GUI 구현에서 사용될 메서드
        pass

    def get_messages(self):
        """모든 로그 메시지 반환"""
        return self.messages

    def get_board_logs(self, cafe_id):
        """특정 카페의 게시판 로그 반환"""
        return self.board_logs.get(cafe_id, {})

    def get_task_logs(self):
        """모든 작업 로그 반환"""
        return self.task_logs 