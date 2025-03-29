from PyQt5.QtCore import QThread, pyqtSignal
from .api.search import NaverCafeSearchAPI
from .api.cafe import CafeAPI
from .api.ai_generator import AIGenerator
import time
import traceback

# 작업관리에서 작업 리스트를 가져오고 작업에 맞는 설정값들은 스케줄러를 만들고 별도로 관리한다.

class Worker(QThread):
    log_message = pyqtSignal(dict)  # 로그 메시지 시그널
    post_found = pyqtSignal(dict)   # 게시글 발견 시그널
    next_task_info = pyqtSignal(dict)  # 다음 작업 정보 시그널
    tasks_completed = pyqtSignal(bool)  # 작업 완료 시그널 (True: 정상 완료, False: 오류/취소)
    progress_updated = pyqtSignal(dict)  # 진행상황 업데이트 시그널 (추가)
    
    def __init__(self, headers=None, search_keyword=None, api_key=None, options=None):
        """
        Worker 클래스 초기화
        
        Args:
            headers (dict): 로그인된 계정의 헤더 정보
            search_keyword (str): 검색 키워드
            api_key (str): OpenAI API 키
            options (dict): 검색 옵션
                - cafe_where (str): 검색 대상
                - sort (str): 정렬 방식
                - date_option (int): 기간 옵션
                - max_items (int): 최대 수집 개수
                - page_delay (int): 페이지 간 딜레이
                - ai_filter_command (str): AI 분석 명령어
                - filter_keywords (list): 필터 키워드 목록 (추가됨)
        """
        super().__init__()
        self.headers = headers
        self.search_keyword = search_keyword
        self.api_key = api_key
        self.options = options or {}
        self.is_running = False
        self.post_count = 0
        self.collected_titles = []  # 중복 제거를 위한 제목 저장 리스트
        self.collected_ids_content_pairs = set()  # 중복 제거를 위한 (아이디, 내용) 쌍 저장 집합
        self.search_api = None  # NaverCafeSearchAPI 인스턴스 저장용 (추가)

    def set_headers(self, headers):
        """헤더 설정"""
        self.headers = headers
        
    def set_search_keyword(self, keyword):
        """검색 키워드 설정"""
        self.search_keyword = keyword
        
    def set_api_key(self, api_key):
        """OpenAI API 키 설정"""
        self.api_key = api_key
        
    def set_options(self, options):
        """검색 옵션 설정"""
        self.options = options
        
    def stop(self):
        """작업 중지"""
        self.is_running = False
        # 검색 API 인스턴스가 있으면 중지 신호 전달 (추가)
        if self.search_api:
            self.search_api.stop_search()
        self.log_message.emit({"message": "작업이 중지되었습니다.", "color": "red"})
        
    def run(self):
        """작업 실행"""
        try:
            self.is_running = True
            
            # 01. 로그인된 계정의 헤더 정보를 가져온다.
            if not self.headers:
                self.log_message.emit({"message": "로그인된 계정 정보가 없습니다. 계정을 먼저 로그인해주세요.", "color": "red"})
                self.is_running = False
                self.tasks_completed.emit(False)  # 작업 실패 시그널 발생
                return
            else:
                self.log_message.emit({"message": "로그인된 계정 정보가 확인되었습니다.", "color": "green"})
                
            # 검색 키워드 확인
            if not self.search_keyword:
                self.log_message.emit({"message": "검색 키워드가 설정되지 않았습니다.", "color": "red"})
                self.is_running = False
                self.tasks_completed.emit(False)  # 작업 실패 시그널 발생
                return
            else:
                self.log_message.emit({"message": f"검색 키워드: '{self.search_keyword}'", "color": "blue"})
                
            # API 키 확인
            if not self.api_key:
                self.log_message.emit({"message": "OpenAI API 키가 설정되지 않았습니다.", "color": "red"})
                self.is_running = False
                self.tasks_completed.emit(False)  # 작업 실패 시그널 발생
                return
                
            # API 키 검증
            self.log_message.emit({"message": "OpenAI API 키 검증 중...", "color": "blue"})
            ai_generator = AIGenerator(api_key=self.api_key)
            is_valid, message = ai_generator.validate_api_key()
            
            if not is_valid:
                self.log_message.emit({"message": f"API 키 검증 실패: {message}", "color": "red"})
                self.is_running = False
                self.tasks_completed.emit(False)  # 작업 실패 시그널 발생
                return
            else:
                self.log_message.emit({"message": f"API 키 검증 성공: {message}", "color": "green"})
                
            self.log_message.emit({"message": "작업을 시작합니다.", "color": "green"})
            
            # 02. 설정에 맞춰서 네이버 카페 검색을 한다. search.py의 search함수 사용
            self.log_message.emit({"message": f"'{self.search_keyword}' 키워드로 네이버 카페 검색을 시작합니다.", "color": "blue"})
            
            # 검색 옵션 설정
            max_items = self.options.get("max_items", 100)
            cafe_where = self.options.get("cafe_where", "articleg")  # 기본값: 일반글
            date_option = self.options.get("date_option", 2)  # 기본값: 1일
            sort = self.options.get("sort", "rel")  # 기본값: 관련도순
            page_delay = self.options.get("page_delay", 1)  # 기본값: 1초
            
            # 옵션 디버깅용 로그 출력
            self.log_message.emit({
                "message": f"작업 설정: {self.options}", 
                "color": "gray"
            })
            
            # NaverCafeSearchAPI 인스턴스 생성 및 저장
            self.search_api = NaverCafeSearchAPI()
            
            # 진행상황 초기화
            self.progress_updated.emit({
                "status": "검색 시작",
                "current_page": 0,
                "total_items": 0,
                "progress": 0
            })
            
            # 검색 실행 (콜백 함수 추가)
            search_results = self.search_api.search(
                query=self.search_keyword,
                max_items=max_items,
                cafe_where=cafe_where,
                date_option=date_option,
                sort=sort,
                page_delay=page_delay,
                progress_callback=self.update_search_progress  # 콜백 함수 추가
            )
            
            # 03. 검색된 결과를 가져온다.
            if search_results["status"] != "success":
                self.log_message.emit({"message": "검색 결과를 가져오는데 실패했습니다.", "color": "red"})
                self.is_running = False
                self.tasks_completed.emit(False)  # 작업 실패 시그널 발생
                return
                
            total_count = search_results["total_count"]
            self.log_message.emit({"message": f"총 {total_count}개의 게시글을 검색했습니다.", "color": "blue"})
            
            # CafeAPI 인스턴스 생성 (헤더 전달)
            cafe_api = CafeAPI(self.headers)
            
            # 기존 수집된 제목 가져오기
            existing_titles = []
            existing_id_content_pairs = set()
            try:
                from PyQt5.QtWidgets import QTableWidgetItem
                if hasattr(self, 'routine_tab') and hasattr(self.routine_tab, 'task_monitor'):
                    for row in range(self.routine_tab.task_monitor.rowCount()):
                        # 제목(내용) 가져오기
                        content_item = self.routine_tab.task_monitor.item(row, 2)
                        # 아이디 가져오기
                        id_item = self.routine_tab.task_monitor.item(row, 1)
                        
                        if content_item and id_item:
                            content_text = content_item.text()
                            id_text = id_item.text()
                            existing_titles.append(content_text)
                            existing_id_content_pairs.add((id_text, content_text))
            except Exception as e:
                self.log_message.emit({"message": f"기존 게시글 확인 중 오류 발생: {str(e)}. 중복 체크를 건너뜁니다.", "color": "yellow"})
            
            # 04. 가져올 때 AI 분석 키워드가 있다면 분석 키워드로 필터해서 가져온다
            ai_filter_command = self.options.get("ai_filter_command", "")
            filter_keywords = self.options.get("filter_keywords", [])
            
            self.log_message.emit({
                "message": f"총 검색된 게시글: {len(search_results['items'])}개, 필터 키워드: {filter_keywords if filter_keywords else '없음'}, AI 분석 필터: {ai_filter_command if ai_filter_command else '없음'}", 
                "color": "blue"
            })
            
            # ------------------------------------------------
            # 04-1. 키워드 필터 - 필터 키워드가 있으면 1차 필터링 진행
            # ------------------------------------------------
            filtered_by_keywords = []  # 키워드 필터링된 게시글 저장
            
            if filter_keywords:
                self.log_message.emit({"message": f"필터 키워드: {', '.join(filter_keywords)}", "color": "blue"})
                
                for item in search_results["items"]:
                    title = item["title"].strip()
                    content = item["content"].strip()
                    
                    # 제목이나 내용에 필터 키워드가 포함되어 있는지 확인
                    for keyword in filter_keywords:
                        keyword = keyword.strip()
                        if keyword in title or keyword in content:
                            self.log_message.emit({
                                "message": f"✅ 필터 키워드 '{keyword}' 발견: {title}", 
                                "color": "green"
                            })
                            
                            # 중복 게시글 확인 (제목 및 아이디+내용 조합으로 중복 체크)
                            is_duplicate = False
                            
                            # 제목 중복 확인
                            if title in self.collected_titles or title in existing_titles:
                                self.log_message.emit({"message": f"⚠️ 중복 게시글(제목) 건너뜀: {title}", "color": "yellow"})
                                is_duplicate = True
                            
                            # 아이디+내용 조합 중복 확인
                            id_content_pair = (item["cafe_id"], title)
                            if id_content_pair in self.collected_ids_content_pairs or id_content_pair in existing_id_content_pairs:
                                self.log_message.emit({"message": f"⚠️ 중복 게시글(아이디+내용) 건너뜀: {title}", "color": "yellow"})
                                is_duplicate = True
                            
                            # 중복인 경우 다음 게시글로
                            if is_duplicate:
                                continue
                            
                            # 필터링된 게시글 목록에 추가
                            filtered_by_keywords.append(item)
                            
                            # 중복 확인을 위해 수집된 제목 및 아이디+내용 조합 저장
                            # 중복 확인을 위한 조합 저장은 AI 분석 키워드가 있는 경우에만 진행
                            self.collected_titles.append(title)
                            self.collected_ids_content_pairs.add((item["cafe_id"], title))
                            
                            break  # 하나의 키워드라도 매칭되면 다음 게시글로
                
                self.log_message.emit({
                    "message": f"필터 키워드로 {len(filtered_by_keywords)}개의 게시글이 1차 필터링되었습니다.", 
                    "color": "blue"
                })
            else:
                # 필터 키워드가 없는 경우 모든 게시글을 1차 필터 통과로 처리
                filtered_by_keywords = search_results["items"]
                self.log_message.emit({
                    "message": "필터 키워드가 설정되지 않아 모든 게시글이 1차 필터를 통과했습니다.", 
                    "color": "blue"
                })
            
            # ------------------------------------------------
            # 04-2. AI 필터 - AI 명령어가 있으면 2차 필터링 진행
            # ------------------------------------------------
            if ai_filter_command and filtered_by_keywords:  # 1차 필터링된 게시글이 있는 경우에만 AI 분석 진행
                self.log_message.emit({"message": f"AI 분석 필터: '{ai_filter_command}'로 1차 필터링된 게시글을 분석합니다.", "color": "blue"})
                
                # 배치 처리를 위한 크기 설정
                batch_size = 20  # 한 번에 처리할 게시글 수
                total_items = len(filtered_by_keywords)
                
                self.log_message.emit({"message": f"총 {total_items}개 게시글에 대해 AI 배치 분석을 시작합니다.", "color": "blue"})
                
                if total_items > 0:
                    # 1단계: 게시글 내용 수집 단계
                    self.log_message.emit({"message": "1단계: AI 분석을 위한 게시글 내용 수집 중...", "color": "blue"})
                    
                    # 진행상황 초기화 - 게시글 내용 수집 시작
                    self.progress_updated.emit({
                        "status": "AI 분석을 위한 게시글 내용 수집 중",
                        "current_page": 0,
                        "total_items": 0,
                        "progress": 0
                    })
                    
                    # 분석용 게시글 준비
                    posts_for_analysis = []
                    
                    # 게시글 내용 수집 (1차 필터링된 게시글만)
                    for idx, item in enumerate(filtered_by_keywords):
                        if not self.is_running:
                            break
                        
                        try:
                            # 게시글 제목
                            title = item["title"]
                            
                            # 진행상황 업데이트
                            progress_pct = ((idx + 1) / total_items) * 40  # 내용 수집은 전체 진행의 40%
                            self.progress_updated.emit({
                                "status": "AI 분석을 위한 게시글 내용 수집 중",
                                "current_page": 0,
                                "total_items": idx + 1,
                                "progress": int(progress_pct)
                            })
                            
                            # 게시글 내용
                            cafe_url_id = item["cafe_id"]
                            article_id = item["article_id"]
                            
                            try:
                                # URL에서 art 매개변수 추출
                                url = item["url"]
                                art_param = None
                                if "art=" in url:
                                    art_param = url.split("art=")[1].split("&")[0]
                                
                                # 카페 정보를 가져와서 실제 카페 ID 얻기
                                cafe_info = cafe_api.get_cafe_info(cafe_url_id)
                                real_cafe_id = cafe_info["id"]
                                
                                # 게시글 내용 가져오기 (art 매개변수 전달)
                                content_html = cafe_api.get_board_content(real_cafe_id, article_id, art_param)
                                content = cafe_api.get_parse_content_html(content_html) if content_html else item["content"]
                            except (ConnectionResetError, ConnectionAbortedError, ConnectionRefusedError, ConnectionError) as e:
                                self.log_message.emit({"message": f"네트워크 연결 오류 발생: {str(e)}. 재시도 중...", "color": "yellow"})
                                # 잠시 대기 후 재시도
                                time.sleep(5)  # 연결 오류 시 더 긴 대기 시간 (2초 → 5초)
                                try:
                                    # 재시도: 카페 정보
                                    cafe_info = cafe_api.get_cafe_info(cafe_url_id)
                                    real_cafe_id = cafe_info["id"]
                                    
                                    # 재시도: 게시글 내용 가져오기 (art 매개변수 전달)
                                    content_html = cafe_api.get_board_content(real_cafe_id, article_id, art_param)
                                    content = cafe_api.get_parse_content_html(content_html) if content_html else item["content"]
                                    
                                    self.log_message.emit({"message": "재시도 성공: 게시글 내용을 가져왔습니다.", "color": "green"})
                                except Exception as retry_e:
                                    self.log_message.emit({"message": f"재시도 실패 ({type(retry_e).__name__}): {str(retry_e)}. 기본 내용 사용", "color": "red"})
                                    # 기본 내용 사용
                                    content = item["content"]
                            except Exception as e:
                                error_type = type(e).__name__
                                self.log_message.emit({"message": f"AI 분석용 게시글 내용 가져오기 실패 ({error_type}): {str(e)}. 기본 내용 사용", "color": "red"})
                                # 기본 내용 사용
                                content = item["content"]
                            
                            # 분석용 데이터 추가
                            posts_for_analysis.append({
                                'idx': idx,
                                'item': item,
                                'title': title,
                                'content': content[:300] if len(content) > 300 else content,  # 내용을 300자로 제한
                                'cafe_url_id': cafe_url_id
                            })
                            
                            # 로그 메시지
                            if (idx + 1) % 10 == 0 or idx + 1 == total_items:
                                self.log_message.emit({
                                    "message": f"AI 분석을 위한 게시글 내용 수집 중: {idx + 1}/{total_items}", 
                                    "color": "blue"
                                })
                            
                        except Exception as e:
                            self.log_message.emit({"message": f"AI 분석을 위한 게시글 내용 수집 중 오류 발생: {str(e)}", "color": "red"})
                            continue
                    
                    # 수집된 게시글이 있는 경우에만 배치 분석 수행
                    if posts_for_analysis and self.is_running:
                        self.log_message.emit({
                            "message": f"2단계: AI 배치 분석 시작 - 총 {len(posts_for_analysis)}개 게시글, 배치 크기: {batch_size}", 
                            "color": "blue"
                        })
                        
                        # 진행상황 업데이트 - AI 분석 시작 (40% 지점부터 시작)
                        self.progress_updated.emit({
                            "status": "AI 분석 중",
                            "current_page": 0,
                            "total_items": len(posts_for_analysis),
                            "progress": 40
                        })
                        
                        # 배치 분석용 데이터 준비 - 이미 짧게 자른 내용 사용
                        batch_posts = [{'title': p['title'], 'content': p['content']} for p in posts_for_analysis]
                        
                        # 디버깅용 로그
                        self.log_message.emit({
                            "message": f"AI 분석 시작: 배치 크기={batch_size}, 분석할 게시글 수={len(batch_posts)}, AI 명령어='{ai_filter_command}'", 
                            "color": "blue"
                        })
                        
                        # 배치 분석 수행
                        analysis_results = ai_generator.analyze_posts_batch(
                            batch_posts, 
                            ai_filter_command, 
                            batch_size,
                            progress_callback=self.update_batch_progress
                        )
                        
                        # 디버깅용 로그
                        self.log_message.emit({
                            "message": f"AI 분석 결과 받음: 총 {len(analysis_results)}개 결과", 
                            "color": "blue"
                        })
                        
                        # 3단계: 분석 결과에 따라 게시글 수집
                        self.log_message.emit({
                            "message": f"3단계: 분석 결과 처리 - AI 분석 완료, 결과 수집 중", 
                            "color": "blue"
                        })
                        
                        # 진행상황 업데이트 - 결과 처리 시작 (80% 지점부터 시작)
                        self.progress_updated.emit({
                            "status": "분석 결과 처리 중",
                            "current_page": 0,
                            "total_items": len(analysis_results),
                            "progress": 80
                        })
                        
                        # 분석 결과에 따라 게시글 수집
                        filtered_items = []
                        matched_count = 0
                        for i, is_relevant in enumerate(analysis_results):
                            if not self.is_running:
                                break
                                
                            post_data = posts_for_analysis[i]
                            title = post_data['title']
                            
                            # 진행상황 업데이트
                            progress_pct = 80 + ((i + 1) / len(analysis_results)) * 20  # 결과 처리는 80-100%
                            self.progress_updated.emit({
                                "status": "분석 결과 저장 중",
                                "current_page": 0,
                                "total_items": i + 1,
                                "progress": int(progress_pct)
                            })
                            
                            # 분석 결과가 참인 경우만 수집
                            if is_relevant:
                                self.log_message.emit({"message": f"✅ 일치 게시글 발견: {title}", "color": "green"})
                                
                                # 필터링된 게시글 목록에 추가
                                filtered_items.append(post_data['item'])
                                
                                # 중복 확인을 위해 수집된 제목 및 아이디+내용 조합 저장
                                self.collected_titles.append(title)
                                self.collected_ids_content_pairs.add((post_data['cafe_url_id'], title))
                                
                                # 게시글 발견 시그널 발생
                                self.post_found.emit({
                                    "no": self.post_count + 1,
                                    "id": post_data['cafe_url_id'],
                                    "content": title,
                                    "url": post_data['item']["url"] if post_data['item']["url"].startswith(("http://", "https://")) else "https://" + post_data['item']["url"]
                                })
                                
                                self.post_count += 1
                                matched_count += 1
                            else:
                                # 일치하지 않는 경우는 간단히 로깅만
                                if (i + 1) % 10 == 0 or i + 1 == len(analysis_results):
                                    self.log_message.emit({
                                        "message": f"AI 분석 결과 처리 중: {i + 1}/{len(analysis_results)}", 
                                        "color": "gray"
                                    })
                        
                        # 필터링된 결과 업데이트
                        search_results["items"] = filtered_items
                        search_results["total_count"] = len(filtered_items)
                        
                        self.log_message.emit({
                            "message": f"AI 분석 완료: 총 {len(posts_for_analysis)}개 중 {matched_count}개의 게시글이 조건과 일치합니다.", 
                            "color": "green"
                        })
                        
                        # 진행상황 업데이트 - 모든 과정 완료 (100%)
                        self.progress_updated.emit({
                            "status": "분석 완료",
                            "current_page": 0,
                            "total_items": matched_count,
                            "progress": 100
                        })
            
            elif ai_filter_command and len(search_results["items"]) == 0:
                # AI 명령어는 있지만 분석할 게시글이 없는 경우 (모두 키워드 필터로 처리됨)
                self.log_message.emit({
                    "message": "AI 분석 대상 게시글이 없습니다. 모든 게시글이 필터 키워드로 이미 처리되었습니다.",
                    "color": "yellow"
                })
            
            elif not ai_filter_command:
                # AI 필터 명령어가 없는 경우 - 1차 필터링된 게시글 직접 수집
                self.log_message.emit({
                    "message": "AI 분석 필터가 설정되지 않았습니다. 1차 필터링된 게시글을 직접 수집합니다.", 
                    "color": "yellow"
                })
                
                # 1차 필터링된 게시글 처리
                for idx, item in enumerate(filtered_by_keywords):
                    if not self.is_running:
                        break
                        
                    try:
                        # 제목 가져오기
                        title = item["title"]
                        
                        # 중복 게시글 확인 (제목 및 아이디+내용 조합으로 중복 체크)
                        is_duplicate = False
                        
                        # 제목 중복 확인
                        if title in self.collected_titles or title in existing_titles:
                            self.log_message.emit({"message": f"⚠️ 중복 게시글(제목) 건너뜀: {title}", "color": "yellow"})
                            is_duplicate = True
                        
                        # 아이디+내용 조합 중복 확인
                        id_content_pair = (item["cafe_id"], title)
                        if id_content_pair in self.collected_ids_content_pairs or id_content_pair in existing_id_content_pairs:
                            self.log_message.emit({"message": f"⚠️ 중복 게시글(아이디+내용) 건너뜀: {title}", "color": "yellow"})
                            is_duplicate = True
                        
                        # 중복인 경우 다음 게시글로
                        if is_duplicate:
                            continue
                            
                        # 게시글 발견 시그널 발생
                        self.post_found.emit({
                            "no": self.post_count + 1,
                            "id": item["cafe_id"],
                            "content": title,
                            "url": item["url"] if item["url"].startswith(("http://", "https://")) else "https://" + item["url"]
                        })
                        
                        # 중복 확인을 위해 수집된 제목 및 아이디+내용 조합 저장
                        self.collected_titles.append(title)
                        self.collected_ids_content_pairs.add((item["cafe_id"], title))
                        
                        self.post_count += 1
                        
                        # 작업 간 딜레이
                        time.sleep(0.1)
                        
                    except Exception as e:
                        self.log_message.emit({"message": f"게시글 처리 중 오류 발생: {str(e)}", "color": "red"})
                        continue
            
            # 05. 수집된 정보를 모니터에 넣는다. (시그널로 전달)
            self.log_message.emit({"message": f"작업이 완료되었습니다. 총 {self.post_count}개의 게시글이 수집되었습니다.", "color": "green"})
            
            # 작업 완료 시그널 발생
            self.tasks_completed.emit(True)
            
        except Exception as e:
            self.log_message.emit({"message": f"작업 실행 중 오류 발생: {str(e)}", "color": "red"})
            self.log_message.emit({"message": traceback.format_exc(), "color": "red"})
            self.tasks_completed.emit(False)  # 작업 실패 시그널 발생
        finally:
            self.is_running = False
            # 진행상황 초기화
            self.progress_updated.emit({
                "status": "대기 중",
                "current_page": 0,
                "total_items": 0,
                "progress": 0
            })

    def update_search_progress(self, current_page, total_items, is_searching):
        """검색 진행상황 업데이트 콜백
        
        Args:
            current_page (int): 현재 페이지 번호
            total_items (int): 현재까지 수집된 총 항목 수
            is_searching (bool): 검색 진행 중 여부
        """
        if not self.is_running:
            return
            
        status = "검색 중" if is_searching else "검색 완료"
        progress = min(int((total_items / self.options.get("max_items", 100)) * 100), 100)
        
        self.progress_updated.emit({
            "status": status,
            "current_page": current_page,
            "total_items": total_items,
            "progress": progress
        })
        
    def update_batch_progress(self, batch_index, batch_count, is_processing):
        """배치 분석 진행상황 업데이트 콜백
        
        Args:
            batch_index (int): 현재 배치 인덱스
            batch_count (int): 전체 배치 수
            is_processing (bool): 배치 처리 중 여부
        """
        if not self.is_running:
            return
            
        # 진행률 계산 (40%~80% 사이에서 진행)
        batch_progress = (batch_index / batch_count) * 40
        progress = 40 + batch_progress
        
        status_text = f"AI 분석 중 ({batch_index}/{batch_count} 배치)"
        if not is_processing and batch_index == batch_count:
            status_text = "AI 분석 완료"
            
        self.progress_updated.emit({
            "status": status_text,
            "current_page": batch_index,
            "total_items": batch_count,
            "progress": int(progress)
        })