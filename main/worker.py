from main.api.auth import NaverAuth
from main.api.ai_generator import AIGenerator
from main.api.image import ImageAPI
from main.api.cafe import CafeAPI
from main.utils.log import Log
from main.api.reply import ReplyAPI
from main.utils.openai_utils import OpenAIGenerator
from main.api.ip_manage import change_ip
import traceback
import os
import random
from datetime import datetime, timedelta
import json
from PyQt5.QtCore import QThread, pyqtSignal, QMetaObject, Qt, Q_ARG, QVariant
import time
from main.api.ip_manage import is_tethering_enabled

# 작업관리에서 작업 리스트를 가져오고 작업에 맞는 설정값들은 스케줄러를 만들고 별도로 관리한다.

class Worker(QThread):
    # 시그널 정의
    task_started = pyqtSignal(dict)  # 작업 시작 시그널
    task_completed = pyqtSignal(dict)  # 작업 완료 시그널
    task_error = pyqtSignal(dict, str)  # 작업 오류 시그널
    log_message = pyqtSignal(dict)  # 로그 메시지 시그널
    post_completed = pyqtSignal(dict)  # 게시글 등록 완료 시그널 (추가)
    next_task_info = pyqtSignal(dict)  # 다음 작업 정보 시그널 (추가)
    all_tasks_completed = pyqtSignal(bool)  # 모든 작업 완료 시그널 (추가) - bool 파라미터는 정상 완료 여부
    ip_changed = pyqtSignal(str)  # IP 변경 시그널 (추가) - 새 IP 주소를 전달
    
    def __init__(self, main_window=None):
        super().__init__()
        self.tasks = []
        self.is_running = False
        self.main_window = main_window
        self.min_interval = 5  # 기본값 5분
        self.max_interval = 15  # 기본값 15분
        self.logger = Log()  # Log 클래스 인스턴스 생성
        
        # 작업 반복 설정 초기화
        self.repeat_tasks = False
        
        # IP 테더링 관련 설정 초기화
        self.use_ip_tethering = False
        self.ip_change_success_count = 0
        self.ip_change_fail_count = 0
        
    def set_tasks(self, tasks):
        """작업 리스트 설정
        
        Args:
            tasks (list): 실행할 작업 리스트
        """
        self.tasks = tasks
        
    def set_main_window(self, main_window):
        """메인 윈도우 설정
        
        Args:
            main_window: MainWindow 인스턴스
        """
        self.main_window = main_window
        
    def stop(self):
        """작업 실행 중지"""
        if self.is_running:
            self.add_log_message({
                'message': "[작업 중지 요청] 작업 중지가 요청되었습니다.",
                'color': 'yellow'
            })
            self.is_running = False
            self.add_log_message({
                'message': "[작업 중지 처리] is_running 상태가 False로 변경되었습니다.",
                'color': 'yellow'
            })
            self.wait()  # 스레드가 종료될 때까지 대기

    def add_log_message(self, message_data):
        """로그 메시지 추가 및 시그널 발생
        
        Args:
            message_data (dict): 로그 메시지 데이터
                - message (str): 로그 메시지
                - color (str, optional): 메시지 색상 (기본값: 'black')
        """
        try:
            # 로그 메시지 시그널 발생
            self.log_message.emit(message_data)
            
            # 로그 출력 (디버깅용)
            message = message_data.get('message', '')
            color = message_data.get('color', 'black')
            
            # 콘솔에 로그 출력
            print(f"[Worker] {message}")
            
            # 파일에 로그 기록 (예외 처리)
            try:
                if color == "red":
                    self.logger.error(message)
                elif color == "yellow":
                    self.logger.warning(message)
                elif color == "blue":
                    self.logger.info(message)
                elif color == "green":
                    self.logger.info(message)
                else:
                    self.logger.info(message)
            except Exception as log_error:
                print(f"로그 파일 기록 중 오류 발생: {str(log_error)}")
                
        except Exception as e:
            # 로그 추가 중 오류 발생 시 콘솔에만 출력
            print(f"로그 추가 중 오류 발생: {str(e)}")
        
        # 메인 윈도우 직접 접근 방식은 제거 (스레드 안전을 위해 시그널만 사용)

    def set_intervals(self, min_interval, max_interval):
        """작업 간 대기 시간 간격 설정
        
        Args:
            min_interval (int): 최소 대기 시간 (분)
            max_interval (int): 최대 대기 시간 (분)
        """
        self.min_interval = min_interval
        self.max_interval = max_interval
        
    def set_ip_tethering(self, use_ip_tethering):
        """IP 테더링 사용 여부 설정
        
        Args:
            use_ip_tethering (bool): IP 테더링 사용 여부
        """
        self.use_ip_tethering = use_ip_tethering
        self.add_log_message({
            'message': f"IP 테더링 설정이 {'활성화' if use_ip_tethering else '비활성화'}되었습니다.",
            'color': 'blue'
        })
        
        # 테더링 상태 확인
        if use_ip_tethering:
            try:
                tethering_enabled = is_tethering_enabled()
                if not tethering_enabled:
                    self.add_log_message({
                        'message': "테더링이 활성화되어 있지 않습니다. 설정을 확인해주세요.",
                        'color': 'yellow'
                    })
                else:
                    self.add_log_message({
                        'message': "테더링이 정상적으로 활성화되어 있습니다.",
                        'color': 'green'
                    })
            except Exception as e:
                self.add_log_message({
                    'message': f"테더링 상태 확인 중 오류 발생: {str(e)}",
                    'color': 'red'
                })

    def set_repeat_tasks(self, repeat_tasks):
        """작업 반복 설정
        
        Args:
            repeat_tasks (bool): 작업 반복 여부
        """
        self.repeat_tasks = repeat_tasks
        self.add_log_message({
            'message': f"작업 반복 설정이 {'활성화' if repeat_tasks else '비활성화'}되었습니다.",
            'color': 'blue'
        })

    def get_random_wait_time(self):
        """최소/최대 간격 사이의 랜덤한 대기 시간(초) 반환"""
        min_seconds = self.min_interval * 60
        max_seconds = self.max_interval * 60
        return random.randint(min_seconds, max_seconds)
        
    def get_comment_wait_time(self):
        """댓글 작업 간 랜덤한 대기 시간(초) 반환"""
        # 댓글 작업 간 간격은 10~60초 사이 랜덤
        return random.randint(10, 60)

    def get_like_wait_time(self):
        """좋아요 작업 간 랜덤한 대기 시간(초) 반환"""
        # 좋아요 작업 간 간격은 10~60초 사이 랜덤
        return random.randint(10, 60)

    def format_time_remaining(self, seconds):
        """남은 시간을 분:초 형식으로 변환"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}분 {seconds}초"

    def get_next_execution_time(self, wait_seconds):
        """다음 실행 시간을 계산"""
        next_time = datetime.now() + timedelta(seconds=wait_seconds)
        return next_time.strftime("%H:%M:%S")

    def get_next_pending_task_index(self):
        """다음 실행할 작업의 인덱스를 반환합니다.
        
        Returns:
            int: 다음 실행할 작업의 인덱스 (0부터 시작)
        """
        for i, task in enumerate(self.tasks):
            if task.get('status') != 'completed':
                return i
        return 0  # 모든 작업이 완료된 경우 0 반환

    def run(self):
        """작업 실행 (QThread에서 오버라이드)"""
        self.is_running = True
        
        try:
            # 작업 리스트가 비어있는지 확인
            if not self.tasks:
                self.add_log_message({
                    'message': "실행할 작업이 없습니다. 작업 실행이 중지됩니다.",
                    'color': 'red'
                })
                # 작업이 없는 경우도 완료 시그널 발생 (정상 완료)
                self.all_tasks_completed.emit(True)
                self.is_running = False
                return
            
            # 작업 반복 설정 확인 (안전하게 처리)
            repeat_tasks = False
            try:
                # 직접 전달받은 repeat_tasks 속성이 있는지 확인
                if hasattr(self, 'repeat_tasks'):
                    repeat_tasks = self.repeat_tasks
                # 기존 방식으로 설정 확인 (하위 호환성 유지)
                elif self.main_window:
                    # MainWindow 객체에서 설정 값을 가져오는 방식을 수정
                    # 여러 가능한 속성 이름을 시도
                    if hasattr(self.main_window, 'settings'):
                        repeat_tasks = self.main_window.settings.get('repeat_tasks', False)
                        # IP 테더링 설정 가져오기
                        self.use_ip_tethering = self.main_window.settings.get('use_ip_tethering', False)
                    elif hasattr(self.main_window, 'config'):
                        repeat_tasks = self.main_window.config.get('repeat_tasks', False)
                        # IP 테더링 설정 가져오기
                        self.use_ip_tethering = self.main_window.config.get('use_ip_tethering', False)
                    elif hasattr(self.main_window, 'app_settings'):
                        repeat_tasks = self.main_window.app_settings.get('repeat_tasks', False)
                        # IP 테더링 설정 가져오기
                        self.use_ip_tethering = self.main_window.app_settings.get('use_ip_tethering', False)
                    else:
                        # 속성을 찾을 수 없는 경우 기본값 사용
                        self.add_log_message({
                            'message': "설정 정보를 찾을 수 없어 기본값을 사용합니다.",
                            'color': 'yellow'
                        })
            except Exception as e:
                self.add_log_message({
                    'message': f"설정 정보 로드 중 오류 발생: {str(e)}",
                    'color': 'yellow'
                })
            
            # IP 테더링 설정 로그 출력
            self.add_log_message({
                'message': f"IP 테더링 설정: {'활성화' if self.use_ip_tethering else '비활성화'}",
                'color': 'blue'
            })
            
            # 작업 반복 설정 로그 출력
            self.add_log_message({
                'message': f"작업 반복 설정: {'활성화' if repeat_tasks else '비활성화'}",
                'color': 'blue'
            })
            
            # IP 테더링이 활성화된 경우 테더링 상태 확인
            if self.use_ip_tethering:
                try:
                    tethering_enabled = is_tethering_enabled()
                    if not tethering_enabled:
                        self.add_log_message({
                            'message': "테더링이 활성화되어 있지 않습니다. 설정을 확인해주세요.",
                            'color': 'yellow'
                        })
                    else:
                        self.add_log_message({
                            'message': "테더링이 정상적으로 활성화되어 있습니다.",
                            'color': 'green'
                        })
                except Exception as e:
                    self.add_log_message({
                        'message': f"테더링 상태 확인 중 오류 발생: {str(e)}",
                        'color': 'red'
                    })
            
            # 중복 댓글 방지를 위한 파일 로드
            duplicate_file = 'duplicate_comments.json'
            duplicate_comments = {}
            if os.path.exists(duplicate_file):
                try:
                    with open(duplicate_file, 'r', encoding='utf-8') as f:
                        duplicate_comments = json.load(f)
                except Exception as e:
                    self.add_log_message({
                        'message': f"중복 댓글 파일 로드 실패: {str(e)}",
                        'color': 'yellow'
                    })
            
            # OpenAI API 초기화 (안전하게 처리)
            openai_api_key = ''
            try:
                # MainWindow 객체에서 API 키 가져오기 시도
                if self.main_window:
                    if hasattr(self.main_window, 'ai_api_key'):
                        openai_api_key = self.main_window.ai_api_key
                
            except Exception as e:
                self.add_log_message({
                    'message': f"API 키 로드 중 오류 발생: {str(e)}",
                    'color': 'yellow'
                })
                
            # API 키가 없는 경우 메시지 표시
            if not openai_api_key:
                self.add_log_message({
                    'message': "OpenAI API 키가 설정되지 않았습니다. AI 기능이 제한됩니다.",
                    'color': 'yellow'
                })
            
            # OpenAI 생성기 초기화
            openai_generator = None
            if openai_api_key:
                try:
                    openai_generator = OpenAIGenerator(api_key=openai_api_key)
                    # API 키 유효성 검사
                    is_valid, message = openai_generator.validate_api_key()
                    if not is_valid:
                        self.add_log_message({
                            'message': f"OpenAI API 키 검증 실패: {message}",
                            'color': 'yellow'
                        })
                        openai_generator = None
                    else:
                        self.add_log_message({
                            'message': "OpenAI API 키 검증 성공",
                            'color': 'green'
                        })
                except Exception as e:
                    self.add_log_message({
                        'message': f"OpenAI 초기화 실패: {str(e)}",
                        'color': 'yellow'
                    })
                    openai_generator = None
            
            # 작업 반복 루프
            while self.is_running:
                # 모든 작업 처리
                for task_index, task in enumerate(self.tasks):
                    if not self.is_running:
                        break
                    
                    # 작업 상태 확인
                    if task.get('status') == 'completed':
                        continue
                    
                    # 작업 시작 로그
                    self.add_log_message({
                        'message': f"작업 시작: {task.get('id')} - 카페: {task.get('cafe_info', {}).get('cafe_name')}",
                        'color': 'blue'
                    })
                    
                    # 작업 시작 시그널 발생
                    self.task_started.emit(task)
                    
                    try:
                        # 작업 정보 추출
                        account_id = task.get('account_id')
                        all_accounts = task.get('all_accounts', [])
                        cafe_settings = task.get('cafe_settings', {})
                        comment_settings = task.get('comment_settings', {})
                        
                        # 카페 및 게시판 정보 가져오기
                        cafe_info = self.get_cafe_and_board_info(cafe_settings)
                        
                        # 계정 헤더 정보 가져오기
                        headers = self.get_account_header_info(account_id)
                        
                        # 카페 API 초기화
                        cafe_api = CafeAPI(headers)
                        
                        # 게시글 수집
                        post_count = cafe_settings.get('post_count', 10)
                        self.add_log_message({
                            'message': f"게시글 수집 시작: {cafe_info['cafe_name']} - {cafe_info['board_name']} ({post_count}개)",
                            'color': 'blue'
                        })
                        
                        # 게시글 목록 가져오기 (초기 수집)
                        articles = cafe_api.call_board_list(
                            cafe_id=cafe_info['cafe_id'],
                            menu_id=cafe_info['board_id'],
                            per_page=post_count
                        )
                        
                        if not articles:
                            self.add_log_message({
                                'message': f"게시글 수집 실패: {cafe_info['cafe_name']} - {cafe_info['board_name']}",
                                'color': 'red'
                            })
                            continue
                        
                        self.add_log_message({
                            'message': f"게시글 수집 완료: {len(articles)}개",
                            'color': 'green'
                        })
                        
                        # 사용된 계정 추적
                        used_accounts = []
                        
                        # 중복 댓글 방지 확인
                        prevent_duplicate = comment_settings.get('prevent_duplicate', True)
                        cafe_id_str = str(cafe_info['cafe_id'])
                        
                        # 처리할 게시글 목록 (중복 제외)
                        valid_articles = []
                        duplicate_count = 0
                        
                        # 중복 확인 및 유효한 게시글 필터링
                        for article in articles:
                            article_id_str = str(article.get('article_id'))
                            
                            # 중복 확인
                            if prevent_duplicate and cafe_id_str in duplicate_comments and article_id_str in duplicate_comments[cafe_id_str]:
                                self.add_log_message({
                                    'message': f"이미 댓글을 작성한 게시글입니다. 건너뜁니다: {article.get('subject')}",
                                    'color': 'yellow'
                                })
                                duplicate_count += 1
                                continue
                            
                            # 유효한 게시글 추가
                            valid_articles.append(article)
                        
                        # 중복 게시글이 있는 경우 추가 수집 시도
                        if duplicate_count > 0 and len(valid_articles) < post_count:
                            additional_needed = post_count - len(valid_articles)
                            self.add_log_message({
                                'message': f"중복 게시글 {duplicate_count}개 발견. 추가 게시글 {additional_needed}개 수집 시도",
                                'color': 'blue'
                            })
                            
                            # 추가 게시글 수집 (더 많은 게시글 요청)
                            try:
                                additional_articles = cafe_api.call_board_list(
                                    cafe_id=cafe_info['cafe_id'],
                                    menu_id=cafe_info['board_id'],
                                    per_page=post_count + additional_needed + 10  # 여유있게 더 많이 요청
                                )
                                
                                if additional_articles and len(additional_articles) > len(articles):
                                    # 기존에 확인하지 않은 게시글만 필터링
                                    new_articles = additional_articles[len(articles):]
                                    
                                    # 추가 게시글 중복 확인 및 유효한 게시글 추가
                                    for article in new_articles:
                                        if len(valid_articles) >= post_count:
                                            break  # 필요한 수만큼 확보했으면 중단
                                            
                                        article_id_str = str(article.get('article_id'))
                                        
                                        # 중복 확인
                                        if prevent_duplicate and cafe_id_str in duplicate_comments and article_id_str in duplicate_comments[cafe_id_str]:
                                            continue  # 중복 게시글 건너뛰기
                                        
                                        # 유효한 게시글 추가
                                        valid_articles.append(article)
                                    
                                    self.add_log_message({
                                        'message': f"추가 게시글 수집 완료: 총 {len(valid_articles)}개 유효 게시글",
                                        'color': 'green'
                                    })
                                else:
                                    self.add_log_message({
                                        'message': f"추가 게시글 수집 실패 또는 더 이상 게시글이 없습니다.",
                                        'color': 'yellow'
                                    })
                            except Exception as e:
                                self.add_log_message({
                                    'message': f"추가 게시글 수집 중 오류 발생: {str(e)}",
                                    'color': 'red'
                                })
                        
                        # 유효한 게시글이 없는 경우 작업 중단
                        if not valid_articles:
                            self.add_log_message({
                                'message': f"처리할 유효한 게시글이 없습니다. 모두 중복이거나 게시글이 없습니다.",
                                'color': 'yellow'
                            })
                            continue
                        
                        # 각 게시글에 대한 작업 수행
                        for article in valid_articles:
                            if not self.is_running:
                                break
                            
                            article_id = article.get('article_id')
                            subject = article.get('subject')
                            writer = article.get('writer')
                            
                            # 게시글 정보 로그
                            self.add_log_message({
                                'message': f"게시글 처리: {subject} (ID: {article_id})",
                                'color': 'blue'
                            })
                            
                            # 게시글 내용 가져오기
                            content_html = cafe_api.get_board_content(cafe_info['cafe_id'], article_id)
                            content_text = cafe_api.get_parse_content_html(content_html) if content_html else ""
                            
                            # 댓글 수 결정 (범위 내 랜덤)
                            comment_count_settings = cafe_settings.get('comment_count', {'base': 5, 'range': 2, 'min': 3, 'max': 7})
                            base_comment_count = comment_count_settings.get('base', 5)
                            comment_range = comment_count_settings.get('range', 2)
                            min_comments = comment_count_settings.get('min', base_comment_count - comment_range)
                            max_comments = comment_count_settings.get('max', base_comment_count + comment_range)
                            
                            comment_count = random.randint(min_comments, max_comments)
                            
                            self.add_log_message({
                                'message': f"댓글 작성 예정: {comment_count}개",
                                'color': 'blue'
                            })
                            
                            # 좋아요 수 결정 (범위 내 랜덤)
                            like_count_settings = cafe_settings.get('like_count', {'base': 3, 'range': 1, 'min': 2, 'max': 4})
                            base_like_count = like_count_settings.get('base', 3)
                            like_range = like_count_settings.get('range', 1)
                            min_likes = like_count_settings.get('min', base_like_count - like_range)
                            max_likes = like_count_settings.get('max', base_like_count + like_range)
                            
                            like_count = random.randint(min_likes, max_likes)
                            
                            # 댓글 작성
                            comments_written = 0
                            
                            # 사용 가능한 계정 목록 (아직 사용하지 않은 계정)
                            available_accounts = [acc for acc in all_accounts if acc not in used_accounts]
                            
                            # 모든 계정을 사용했다면 다시 초기화
                            if not available_accounts:
                                used_accounts = []
                                available_accounts = all_accounts.copy()
                            
                            # 댓글 프롬프트 목록
                            prompts = comment_settings.get('prompts', ['테스트 프롬프트'])
                            used_prompts = []
                            
                            # 댓글 간격 설정
                            comment_interval_settings = comment_settings.get('interval', {'base': 60, 'range': 15, 'min': 45, 'max': 75})
                            base_interval = comment_interval_settings.get('base', 60)
                            interval_range = comment_interval_settings.get('range', 15)
                            min_interval = comment_interval_settings.get('min', base_interval - interval_range)
                            max_interval = comment_interval_settings.get('max', base_interval + interval_range)
                            
                            # 키워드 사용 여부
                            use_keywords = comment_settings.get('use_keywords', True)
                            
                            for i in range(comment_count):
                                if not self.is_running:
                                    break
                                
                                # 사용할 계정 선택
                                if not available_accounts:
                                    used_accounts = []
                                    available_accounts = all_accounts.copy()
                                
                                comment_account = random.choice(available_accounts)
                                available_accounts.remove(comment_account)
                                used_accounts.append(comment_account)
                                
                                # 계정 헤더 정보 가져오기
                                try:
                                    comment_headers = self.get_account_header_info(comment_account)
                                except Exception as e:
                                    self.add_log_message({
                                        'message': f"계정 헤더 정보 가져오기 실패: {str(e)}",
                                        'color': 'red'
                                    })
                                    continue
                                
                                # 댓글 API 초기화
                                reply_api = ReplyAPI(comment_headers)
                                
                                # 사용할 프롬프트 선택
                                if not prompts:
                                    self.add_log_message({
                                        'message': "사용 가능한 프롬프트가 없습니다.",
                                        'color': 'yellow'
                                    })
                                    break
                                
                                # 사용 가능한 프롬프트 목록 (아직 사용하지 않은 프롬프트)
                                available_prompts = [p for p in prompts if p not in used_prompts]
                                
                                # 모든 프롬프트를 사용했다면 다시 초기화
                                if not available_prompts:
                                    used_prompts = []
                                    available_prompts = prompts.copy()
                                
                                selected_prompt = random.choice(available_prompts)
                                used_prompts.append(selected_prompt)
                                
                                # 기본 댓글 목록 정의 (항상 사용 가능하도록)
                                default_comments = [
                                    f"게시글 잘 보고 갑니다! {subject} 정보 감사합니다.",
                                    f"좋은 정보 공유해주셔서 감사합니다. 많은 도움이 되었어요.",
                                    f"이런 내용 찾고 있었는데 잘 보고 갑니다.",
                                    f"정말 유익한 글이네요. 감사합니다!",
                                    f"오늘도 좋은 하루 되세요. 글 잘 봤습니다.",
                                    f"항상 좋은 정보 감사합니다. 자주 들러볼게요.",
                                    f"처음 알게 된 내용이네요. 감사합니다!",
                                    f"이런 정보 정말 필요했어요. 감사합니다!",
                                    f"글 정말 잘 읽었습니다. 도움이 많이 되었어요.",
                                    f"좋은 글 공유해주셔서 감사합니다.",
                                    f"이 주제에 관심이 많았는데 잘 보고 갑니다.",
                                    f"정보 감사합니다. 많은 도움이 되었어요.",
                                    f"이런 내용 찾기 어려웠는데 감사합니다.",
                                    f"글 잘 봤습니다. 다음 글도 기대할게요.",
                                    f"유익한 정보 감사합니다. 자주 방문할게요.",
                                    f"좋은 내용 공유해주셔서 감사합니다.",
                                    f"이 글 덕분에 많이 배웠습니다. 감사합니다!",
                                    f"정말 도움이 많이 되는 글이네요. 감사합니다.",
                                    f"잘 보고 갑니다. 좋은 하루 되세요!",
                                    f"항상 좋은 글 감사합니다. 응원합니다!"
                                ]
                                
                                # 댓글 내용 초기화 (기본값 설정)
                                comment_text = random.choice(default_comments)
                                
                                # OpenAI 생성기가 있으면 AI로 댓글 생성 시도
                                if openai_generator:
                                    try:
                                        # 선택된 프롬프트를 스타일 프롬프트로 사용
                                        style_prompt = selected_prompt
                                        
                                        # 게시글 내용 요약 (너무 길면 잘라내기)
                                        if len(content_text) > 1000:
                                            content_text = content_text[:1000] + "..."
                                        
                                        # 댓글 생성 프롬프트 구성
                                        comment_prompt = f"""
                                        게시글 제목: {subject}
                                        게시글 내용: {content_text}
                                        
                                        위 게시글에 대한 댓글을 작성해주세요.
                                        """
                                        
                                        # 키워드 사용 여부에 따라 프롬프트 수정
                                        if use_keywords:
                                            comment_prompt += " 게시글 본문에서 주요 키워드를 분석하고 해당 키워드를 댓글에서 언급해주세요."
                                        
                                        # 댓글 생성
                                        ai_comment = openai_generator.generate_simple_comment(
                                            prompt=comment_prompt,
                                            style_prompt=style_prompt
                                        )
                                        
                                        # AI 생성 댓글이 비어있지 않으면 사용
                                        if ai_comment and len(ai_comment.strip()) > 0:
                                            comment_text = ai_comment
                                            self.add_log_message({
                                                'message': f"AI 댓글 생성 성공: {comment_text[:30]}...",
                                                'color': 'green'
                                            })
                                        else:
                                            self.add_log_message({
                                                'message': "AI가 빈 댓글을 생성했습니다. 기본 댓글을 사용합니다.",
                                                'color': 'yellow'
                                            })
                                    except Exception as e:
                                        self.add_log_message({
                                            'message': f"AI 댓글 생성 실패: {str(e)}. 기본 댓글을 사용합니다.",
                                            'color': 'red'
                                        })
                                else:
                                    self.add_log_message({
                                        'message': f"AI 생성기가 없어 기본 댓글을 사용합니다: {comment_text[:30]}...",
                                        'color': 'yellow'
                                    })
                                
                                # 댓글 내용이 비어있는지 최종 확인
                                if not comment_text or len(comment_text.strip()) == 0:
                                    comment_text = random.choice(default_comments)
                                    self.add_log_message({
                                        'message': "댓글 내용이 비어있어 기본 댓글로 대체합니다.",
                                        'color': 'yellow'
                                    })

                                # 댓글 작성
                                try:
                                    comment_id = reply_api.write_reply(
                                        cafe_id=cafe_info['cafe_id'],
                                        article_id=article_id,
                                        content=comment_text
                                    )
                                    
                                    if comment_id:
                                        comments_written += 1
                                        self.add_log_message({
                                            'message': f"댓글 작성 성공: {comment_account} - {comment_text[:30]}...",
                                            'color': 'green'
                                        })
                                        
                                        # 중복 댓글 방지를 위한 기록
                                        if prevent_duplicate:
                                            article_id_str = str(article_id)
                                            if cafe_id_str not in duplicate_comments:
                                                duplicate_comments[cafe_id_str] = []
                                            if article_id_str not in duplicate_comments[cafe_id_str]:
                                                duplicate_comments[cafe_id_str].append(article_id_str)
                                                
                                            # 파일에 저장
                                            try:
                                                with open(duplicate_file, 'w', encoding='utf-8') as f:
                                                    json.dump(duplicate_comments, f, ensure_ascii=False, indent=2)
                                            except Exception as e:
                                                self.add_log_message({
                                                    'message': f"중복 댓글 파일 저장 실패: {str(e)}",
                                                    'color': 'yellow'
                                                })
                                        
                                        # 댓글 작성 성공 시 post_completed 시그널 발생
                                        monitor_data = {
                                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            'account_id': comment_account,
                                            'content': comment_text,
                                            'url': f"https://cafe.naver.com/{cafe_info['cafe_url']}/{article_id}"
                                        }
                                        self.post_completed.emit(monitor_data)
                                    else:
                                        self.add_log_message({
                                            'message': f"댓글 작성 실패: {comment_account}",
                                            'color': 'red'
                                        })
                                except Exception as e:
                                    self.add_log_message({
                                        'message': f"댓글 작성 중 오류 발생: {str(e)}",
                                        'color': 'red'
                                    })
                                
                                # IP 테더링 적용
                                if self.use_ip_tethering:
                                    try:
                                        self.add_log_message({
                                            'message': "IP 테더링 적용 중...",
                                            'color': 'blue'
                                        })
                                        
                                        # IP 변경 실행
                                        is_changed, old_ip, new_ip = change_ip()
                                        
                                        # IP 변경 시그널 발생 (성공 여부와 관계없이 현재 IP 정보 전달)
                                        self.ip_changed.emit(new_ip)
                                        
                                        if is_changed:
                                            self.ip_change_success_count += 1
                                            self.add_log_message({
                                                'message': f"IP 변경 성공: {old_ip} → {new_ip} (성공: {self.ip_change_success_count}회)",
                                                'color': 'green'
                                            })
                                        else:
                                            self.ip_change_fail_count += 1
                                            self.add_log_message({
                                                'message': f"IP 변경 실패 또는 동일한 IP 할당됨: {old_ip} (실패: {self.ip_change_fail_count}회)",
                                                'color': 'yellow'
                                            })
                                    except Exception as e:
                                        self.ip_change_fail_count += 1
                                        self.add_log_message({
                                            'message': f"IP 테더링 적용 중 오류 발생: {str(e)} (실패: {self.ip_change_fail_count}회)",
                                            'color': 'red'
                                        })
                                
                                # 다음 댓글 작성 전 대기
                                if i < comment_count - 1:
                                    # 댓글 작업 간 일정 간격 설정
                                    wait_time = self.get_comment_wait_time()
                                    self.add_log_message({
                                        'message': f"다음 댓글 작성까지 대기: {self.format_time_remaining(wait_time)}",
                                        'color': 'blue'
                                    })
                                    
                                    # 다음 작업 정보 표시
                                    next_task_index = self.get_next_pending_task_index()
                                    next_task = self.tasks[next_task_index] if next_task_index < len(self.tasks) else {}
                                    next_task_id = next_task.get('id', '')
                                    next_task_cafe_info = next_task.get('cafe_settings', {})
                                    next_task_cafe_name = next_task_cafe_info.get('cafe_name', '')
                                    next_task_board_name = next_task_cafe_info.get('board_name', '')
                                    
                                    next_task_info = {
                                        'next_task_number': next_task_index + 1,
                                        'next_execution_time': self.get_next_execution_time(wait_time),
                                        'wait_time': self.format_time_remaining(wait_time),
                                        'current_task': {
                                            'task_id': next_task_id,
                                            'cafe_name': next_task_cafe_name,
                                            'board_name': next_task_board_name,
                                            'article_title': '',
                                            'article_id': '',
                                            'account_id': '',
                                            'progress': '다음 작업 대기 중',
                                            'action': '대기'
                                        }
                                    }
                                    self.next_task_info.emit(next_task_info)
                                    
                                    # 대기 시간 동안 중지 여부 확인
                                    for _ in range(wait_time):
                                        if not self.is_running:
                                            break
                                        time.sleep(1)
                            
                            # 작업 완료 로그
                            self.add_log_message({
                                'message': f"게시글 작업 완료: {subject} - 댓글 {comments_written}개 작성",
                                'color': 'green'
                            })
                            
                            # 좋아요 작업 수행
                            try:
                                # 좋아요 API 초기화 (실제 구현은 별도 클래스나 함수로 처리해야 함)
                                # 여기서는 로그만 출력
                                self.add_log_message({
                                    'message': f"좋아요 작업 시작: {subject} - 예정 좋아요 수: {like_count}개",
                                    'color': 'blue'
                                })
                                
                                # 좋아요 작업 수행
                                likes_applied = 0
                                
                                # 사용 가능한 계정 목록 (아직 사용하지 않은 계정)
                                like_available_accounts = [acc for acc in all_accounts if acc not in used_accounts]
                                
                                # 모든 계정을 사용했다면 다시 초기화
                                if not like_available_accounts:
                                    used_accounts = []
                                    like_available_accounts = all_accounts.copy()
                                
                                for i in range(like_count):
                                    if not self.is_running:
                                        break
                                    
                                    # 사용할 계정 선택
                                    if not like_available_accounts:
                                        used_accounts = []
                                        like_available_accounts = all_accounts.copy()
                                    
                                    like_account = random.choice(like_available_accounts)
                                    like_available_accounts.remove(like_account)
                                    used_accounts.append(like_account)
                                    
                                    # 계정 헤더 정보 가져오기
                                    try:
                                        like_headers = self.get_account_header_info(like_account)
                                    except Exception as e:
                                        self.add_log_message({
                                            'message': f"좋아요 계정 헤더 정보 가져오기 실패: {str(e)}",
                                            'color': 'red'
                                        })
                                        continue
                                    
                                    # 좋아요 API 초기화
                                    like_api = CafeAPI(like_headers)
                                    
                                    # IP 테더링 적용
                                    if self.use_ip_tethering:
                                        try:
                                            self.add_log_message({
                                                'message': "좋아요 작업 전 IP 테더링 적용 중...",
                                                'color': 'blue'
                                            })
                                            
                                            # IP 변경 실행
                                            is_changed, old_ip, new_ip = change_ip()
                                            
                                            if is_changed:
                                                self.ip_change_success_count += 1
                                                self.add_log_message({
                                                    'message': f"IP 변경 성공: {old_ip} → {new_ip} (성공: {self.ip_change_success_count}회)",
                                                    'color': 'green'
                                                })
                                            else:
                                                self.ip_change_fail_count += 1
                                                self.add_log_message({
                                                    'message': f"IP 변경 실패 또는 동일한 IP 할당됨: {old_ip} (실패: {self.ip_change_fail_count}회)",
                                                    'color': 'yellow'
                                                })
                                        except Exception as e:
                                            self.ip_change_fail_count += 1
                                            self.add_log_message({
                                                'message': f"IP 테더링 적용 중 오류 발생: {str(e)} (실패: {self.ip_change_fail_count}회)",
                                                'color': 'red'
                                            })
                                    
                                    # 좋아요 적용
                                    try:
                                        # 카페 이름 가져오기 (URL 파라미터로 사용)
                                        cafe_url_name = cafe_info.get('cafe_url', '')
                                        
                                        # 좋아요 적용
                                        like_result = like_api.like_board(
                                            cafe_id=cafe_info['cafe_id'],
                                            article_id=article_id,
                                            cafe_name=cafe_url_name
                                        )
                                        
                                        if like_result:
                                            likes_applied += 1
                                            self.add_log_message({
                                                'message': f"좋아요 적용 성공: {like_account} - 게시글 ID: {article_id}",
                                                'color': 'green'
                                            })
                                        else:
                                            self.add_log_message({
                                                'message': f"좋아요 적용 실패: {like_account} - 게시글 ID: {article_id}",
                                                'color': 'red'
                                            })
                                    except Exception as e:
                                        self.add_log_message({
                                            'message': f"좋아요 적용 중 오류 발생: {str(e)}",
                                            'color': 'red'
                                        })
                                    
                                    # 다음 좋아요 적용 전 대기
                                    if i < like_count - 1:
                                        # 좋아요 작업 간 일정 간격 설정
                                        like_wait_time = self.get_like_wait_time()
                                        self.add_log_message({
                                            'message': f"다음 좋아요 적용까지 대기: {self.format_time_remaining(like_wait_time)}",
                                            'color': 'blue'
                                        })
                                        
                                        # 대기 시간 동안 중지 여부 확인
                                        for _ in range(like_wait_time):
                                            if not self.is_running:
                                                break
                                            time.sleep(1)
                                        
                                        # 좋아요 작업 정보 표시
                                        like_task_info = {
                                            'next_task_number': task_index + 1,
                                            'next_execution_time': self.get_next_execution_time(like_wait_time),
                                            'wait_time': self.format_time_remaining(like_wait_time),
                                            'current_task': {
                                                'task_id': task.get('id', ''),
                                                'cafe_name': cafe_info['cafe_name'],
                                                'board_name': cafe_info['board_name'],
                                                'article_title': subject,
                                                'article_id': article_id,
                                                'account_id': like_account,
                                                'progress': f"{i+1}/{like_count} 좋아요 작업 중",
                                                'action': "좋아요 작업"
                                            }
                                        }
                                        self.next_task_info.emit(like_task_info)
                                
                                self.add_log_message({
                                    'message': f"좋아요 작업 완료: {subject} - 좋아요 {likes_applied}개 처리",
                                    'color': 'green'
                                })
                                
                                # 작업 모니터에 추가
                                monitor_data = {
                                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'account_id': account_id,
                                    'content': f"좋아요: {subject} - {likes_applied}개",
                                    'url': f"https://cafe.naver.com/{cafe_info['cafe_url']}/{article_id}"
                                }
                                self.post_completed.emit(monitor_data)
                            except Exception as e:
                                self.add_log_message({
                                    'message': f"좋아요 작업 중 오류 발생: {str(e)}",
                                    'color': 'red'
                                })
                        
                        # 작업 완료 처리
                        task['status'] = 'completed'
                        task['completed_count'] = len(valid_articles)
                        
                        # 작업 완료 시그널 발생
                        self.task_completed.emit(task)
                        
                    except Exception as e:
                        # 작업 오류 처리
                        error_msg = f"작업 실행 중 오류 발생: {str(e)}"
                        self.add_log_message({
                            'message': error_msg,
                            'color': 'red'
                        })
                        
                        # 작업 오류 시그널 발생
                        self.task_error.emit(task, error_msg)
                        
                        # 작업 상태 업데이트
                        task['status'] = 'error'
                        task['error_count'] = task.get('error_count', 0) + 1
                
                # 모든 작업 완료 후 처리
                all_completed = all(task.get('status') == 'completed' for task in self.tasks)
                
                if all_completed:
                    self.add_log_message({
                        'message': "모든 작업이 완료되었습니다.",
                        'color': 'green'
                    })
                    
                    # 작업 반복 설정에 따라 처리
                    if repeat_tasks:
                        self.add_log_message({
                            'message': "작업 반복 설정에 따라 작업을 다시 시작합니다.",
                            'color': 'blue'
                        })
                        
                        # 작업 상태 초기화
                        for task in self.tasks:
                            task['status'] = 'pending'
                            task['progress'] = 0
                            task['completed_count'] = 0
                            task['error_count'] = 0
                        
                        # 작업 다시 시작 (재귀 호출 대신 continue 사용)
                        continue
                    else:
                        # 모든 작업 완료 시그널 발생 (정상 완료)
                        self.all_tasks_completed.emit(True)
                        break
                else:
                    # 아직 완료되지 않은 작업이 있는 경우
                    wait_time = self.get_random_wait_time()
                    self.add_log_message({
                        'message': f"다음 작업(task) 실행까지 대기: {self.format_time_remaining(wait_time)} (랜덤 간격)",
                        'color': 'blue'
                    })
                    
                    # 다음 작업 정보 표시
                    next_task_index = self.get_next_pending_task_index()
                    next_task = self.tasks[next_task_index] if next_task_index < len(self.tasks) else {}
                    next_task_id = next_task.get('id', '')
                    next_task_cafe_name = next_task.get('cafe_info', {}).get('cafe_name', '')
                    next_task_board_name = next_task.get('cafe_info', {}).get('board_name', '')
                    
                    next_task_info = {
                        'next_task_number': next_task_index + 1,
                        'next_execution_time': self.get_next_execution_time(wait_time),
                        'wait_time': self.format_time_remaining(wait_time),
                        'current_task': {
                            'task_id': next_task_id,
                            'cafe_name': next_task_cafe_name,
                            'board_name': next_task_board_name,
                            'article_title': '',
                            'article_id': '',
                            'account_id': '',
                            'progress': '다음 작업 대기 중',
                            'action': '대기'
                        }
                    }
                    self.next_task_info.emit(next_task_info)
                    
                    # 대기 시간 동안 중지 여부 확인
                    for _ in range(wait_time):
                        if not self.is_running:
                            break
                        time.sleep(1)

        except Exception as e:
            # 예외 발생 시 로그 추가 및 작업 중지
            error_msg = f"작업 실행 중 오류 발생: {traceback.format_exc()}"
            print(error_msg)  # 콘솔에 출력
            
            try:
                self.add_log_message({
                    'message': error_msg,
                    'color': 'red'
                })
            except:
                print("로그 메시지 추가 중 추가 오류 발생")
                
            self.is_running = False
            self.all_tasks_completed.emit(False)
        
        finally:
            # 작업 종료 처리
            self.is_running = False

    def get_account_header_info(self, account_id):
        """계정 헤더 정보 가져오기
        
        Args:
            account_id (str): 계정 ID
            
        Returns:
            dict: 계정 헤더 정보
        """
        # 메인 윈도우 객체 확인
        if not self.main_window:
            raise ValueError("MainWindow 인스턴스가 설정되지 않았습니다.")
            
        # 계정 정보 확인
        if account_id not in self.main_window.accounts:
            raise ValueError(f"계정 '{account_id}'를 찾을 수 없습니다.")
            
        # 헤더 정보 가져오기
        headers = self.main_window.accounts[account_id].get('headers', {})
        
        # 헤더 유효성 검사 (12시간 이내인지)
        if not self.main_window.is_header_valid(headers):
            # 헤더가 유효하지 않은 경우 (12시간 초과)
            # 로그 메시지 추가
            self.add_log_message({
                'message': f"계정 '{account_id}'의 헤더 정보가 만료되었습니다. 재로그인이 필요합니다.",
                'color': 'red'
            })
            
            # 계정 비밀번호 가져오기
            password = self.main_window.accounts[account_id].get('pw', '')
            if not password:
                raise ValueError(f"계정 '{account_id}'의 비밀번호 정보가 없습니다.")
                
            # 재로그인 시도
            self.add_log_message({
                'message': f"계정 '{account_id}' 재로그인 시도 중...",
                'color': 'blue'
            })
            
            # NaverAuth 인스턴스 생성 및 로그인
            auth = NaverAuth()
            auth.set_credentials(account_id, password)
            success = auth.login()
            
            if success:
                # 로그인 성공 시 헤더 정보 업데이트
                headers = auth.get_headers()
                self.main_window.accounts[account_id]['headers'] = headers
                
                self.add_log_message({
                    'message': f"계정 '{account_id}' 재로그인 성공!",
                    'color': 'green'
                })
            else:
                # 로그인 실패
                self.add_log_message({
                    'message': f"계정 '{account_id}' 재로그인 실패",
                    'color': 'red'
                })
                raise ValueError(f"계정 '{account_id}' 재로그인에 실패했습니다.")
        
        # 기본 헤더 설정
        default_headers = {
            "origin": "https://cafe.naver.com",
            "referer": "https://cafe.naver.com",
            "x-cafe-product": "pc",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }
        
        # 헤더 병합 (기본 헤더 + 계정 헤더)
        merged_headers = default_headers.copy()
        for key, value in headers.items():
            if not key.startswith('_'):  # 내부 사용 필드는 제외
                if isinstance(value, (str, bytes)):
                    merged_headers[key] = value
                else:
                    merged_headers[key] = str(value)

        # 로그 메시지 추가
        self.add_log_message({
            'message': f"계정 '{account_id}'의 헤더 정보를 성공적으로 가져왔습니다.",
            'color': 'green'
        })
            
        return merged_headers

    def get_cafe_and_board_info(self, cafe_settings):
        """카페 및 게시판 정보 가져오기
        
        Args:
            cafe_settings (dict): 카페 설정 정보
            
        Returns:
            dict: 카페 및 게시판 정보
        """
        # 필수 정보 확인
        if not cafe_settings:
            raise ValueError("카페 설정 정보가 없습니다.")
            
        # 필수 필드 확인
        required_fields = ['cafe_name', 'cafe_id', 'board_name', 'board_id']
        for field in required_fields:
            if field not in cafe_settings:
                raise ValueError(f"카페 설정에 필수 필드 '{field}'가 없습니다.")
        
        # 카페 및 게시판 정보 구성
        cafe_info = {
            'cafe_id': cafe_settings['cafe_id'],
            'cafe_name': cafe_settings['cafe_name'],
            'cafe_url': cafe_settings.get('cafe_url', cafe_settings['cafe_name']),  # cafe_url이 없으면 cafe_name을 사용
            'board_id': cafe_settings['board_id'],
            'board_name': cafe_settings['board_name'],
        }
        
        # 추가 설정이 있으면 포함
        for key, value in cafe_settings.items():
            if key not in cafe_info:
                cafe_info[key] = value
                
        # 로그 메시지 추가
        self.add_log_message({
            'message': f"카페 정보 로드: {cafe_info['cafe_name']} - {cafe_info['board_name']}",
            'color': 'blue'
        })
        
        return cafe_info