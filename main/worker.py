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
            try:
                from PyQt5.QtWidgets import QTableWidgetItem
                if hasattr(self, 'routine_tab') and hasattr(self.routine_tab, 'task_monitor'):
                    for row in range(self.routine_tab.task_monitor.rowCount()):
                        content_item = self.routine_tab.task_monitor.item(row, 2)
                        if content_item:
                            existing_titles.append(content_item.text())
            except Exception as e:
                self.log_message.emit({"message": f"기존 게시글 확인 중 오류 발생: {str(e)}. 중복 체크를 건너뜁니다.", "color": "yellow"})
            
            # 04. 가져올 때 AI 분석 키워드가 있다면 분석 키워드로 필터해서 가져온다
            ai_filter_command = self.options.get("ai_filter_command", "")
            filter_keywords = self.options.get("filter_keywords", [])
            
            # 필터 키워드가 있는 경우, 먼저 필터 키워드로 필터링
            if filter_keywords:
                self.log_message.emit({"message": f"필터 키워드: {', '.join(filter_keywords)}", "color": "blue"})
                filtered_by_keywords = []
                
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
                            
                            # 중복 게시글 확인
                            if title in self.collected_titles or title in existing_titles:
                                self.log_message.emit({
                                    "message": f"⚠️ 중복 게시글 건너뜀: {title}", 
                                    "color": "yellow"
                                })
                                continue
                            
                            # 게시글 발견 시그널 발생
                            self.post_found.emit({
                                "no": self.post_count + 1,
                                "id": item["cafe_id"],
                                "content": title,
                                "url": item["url"] if item["url"].startswith(("http://", "https://")) else "https://" + item["url"]
                            })
                            
                            # 중복 확인을 위해 수집된 제목 저장
                            self.collected_titles.append(title)
                            self.post_count += 1
                            
                            # 필터링된 게시글 목록에 추가
                            filtered_by_keywords.append(item)
                            break  # 하나의 키워드라도 매칭되면 다음 게시글로
                
                # 필터 키워드로 필터링된 게시글을 제외한 나머지 게시글만 AI 분석 대상으로 설정
                remaining_items = [item for item in search_results["items"] if item not in filtered_by_keywords]
                search_results["items"] = remaining_items
                
                self.log_message.emit({
                    "message": f"필터 키워드로 {len(filtered_by_keywords)}개의 게시글이 수집되었습니다.", 
                    "color": "blue"
                })
            
            if ai_filter_command:
                self.log_message.emit({"message": f"AI 분석 필터: '{ai_filter_command}'로 게시글을 분석합니다.", "color": "blue"})
                
                # 게시글 분석 처리
                filtered_items = []
                
                total_items = len(search_results["items"])
                self.log_message.emit({"message": f"총 {total_items}개 게시글에 대해 AI 분석을 시작합니다.", "color": "blue"})
                
                for idx, item in enumerate(search_results["items"]):
                    if not self.is_running:
                        break
                        
                    try:
                        # 작업 정보 업데이트
                        self.next_task_info.emit({
                            "next_task_number": idx + 1,
                            "next_execution_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "wait_time": "0초",
                            "current_task": {
                                "task_id": f"게시글_{idx+1}",
                                "action": "AI 분석 중"
                            }
                        })
                        
                        # 게시글 제목
                        title = item["title"]
                        
                        # 중복 게시글 확인
                        if title in self.collected_titles or title in existing_titles:
                            self.log_message.emit({"message": f"⚠️ 중복 게시글 건너뜀: {title}", "color": "yellow"})
                            continue
                            
                        self.log_message.emit({"message": f"[{idx+1}/{total_items}] 게시글 분석 중: {title}", "color": "blue"})
                        
                        # 게시글 내용
                        cafe_url_id = item["cafe_id"]  # URL에서 추출한 카페 값
                        article_id = item["article_id"]
                        
                        # 카페 정보를 가져와서 실제 카페 ID 얻기
                        self.log_message.emit({"message": f"카페 정보 가져오는 중: {cafe_url_id}", "color": "gray"})
                        cafe_info = cafe_api.get_cafe_info(cafe_url_id)
                        real_cafe_id = cafe_info["id"]  # 실제 카페 ID
                        
                        # 게시글 내용 가져오기
                        self.log_message.emit({"message": f"게시글 내용 가져오는 중: {article_id}", "color": "gray"})
                        content_html = cafe_api.get_board_content(real_cafe_id, article_id)
                        content = cafe_api.get_parse_content_html(content_html) if content_html else item["content"]
                        
                        # 내용 길이 확인
                        content_preview = content[:10000] + "..." if len(content) > 10000 else content
                        self.log_message.emit({"message": f"게시글 내용 미리보기: {content_preview}", "color": "gray"})
                        
                        # AI 분석 수행
                        self.log_message.emit({"message": f"OpenAI API 호출하여 게시글 분석 중...", "color": "blue"})
                        analysis_result = ai_generator.analyze_post_with_command(title, content, ai_filter_command)
                        
                        # 분석 결과 로그 출력
                        analysis_summary = analysis_result.get("analysis", "분석 내용 없음")
                        matched_keywords = ", ".join(analysis_result.get("matched_keywords", []))
                        
                        # 분석 결과가 조건과 일치하는 경우
                        if analysis_result["is_relevant"]:
                            self.log_message.emit({"message": f"✅ 일치 게시글 발견: {title}", "color": "green"})
                            self.log_message.emit({"message": f"  - 매칭된 키워드: {matched_keywords}", "color": "green"})
                            self.log_message.emit({"message": f"  - 분석 결과: {analysis_summary}", "color": "green"})
                            
                            # 게시글 정보 업데이트
                            item["full_content"] = content
                            item["analysis_result"] = analysis_result
                            
                            # 필터링된 게시글 목록에 추가
                            filtered_items.append(item)
                            
                            # 게시글 발견 시그널 발생
                            self.post_found.emit({
                                "no": self.post_count + 1,
                                "id": cafe_url_id,  # 원래 카페 ID 유지
                                "content": title,
                                "url": item["url"] if item["url"].startswith(("http://", "https://")) else "https://" + item["url"]
                            })
                            
                            # 중복 확인을 위해 수집된 제목 저장
                            self.collected_titles.append(title)
                            
                            self.post_count += 1
                        else:
                            # 조건과 일치하지 않는 경우에도 로그 추가
                            self.log_message.emit({"message": f"❌ 조건 불일치 게시글: {title}", "color": "gray"})
                            self.log_message.emit({"message": f"  - 확인된 키워드: {matched_keywords}", "color": "gray"})
                            self.log_message.emit({"message": f"  - 불일치 사유: {analysis_summary}", "color": "gray"})
                        
                        # 작업 진행률 표시
                        progress_pct = ((idx + 1) / total_items) * 100
                        self.log_message.emit({"message": f"AI 분석 진행률: {progress_pct:.1f}% ({idx + 1}/{total_items})", "color": "blue"})
                        
                        # 작업 간 딜레이
                        time.sleep(0.5)
                        
                    except Exception as e:
                        self.log_message.emit({"message": f"게시글 분석 중 오류 발생: {str(e)}", "color": "red"})
                        continue
                
                # 필터링된 결과 업데이트
                search_results["items"] = filtered_items
                search_results["total_count"] = len(filtered_items)
                
                self.log_message.emit({"message": f"AI 분석 완료: 총 {total_items}개 중 {len(filtered_items)}개의 게시글이 조건과 일치합니다.", "color": "green"})
            
            else:
                # AI 필터 없이 모든 게시글 처리
                self.log_message.emit({"message": "AI 분석 필터가 설정되지 않았습니다. 모든 게시글을 가져옵니다.", "color": "yellow"})
                
                for idx, item in enumerate(search_results["items"]):
                    if not self.is_running:
                        break
                        
                    try:
                        # 제목 가져오기
                        title = item["title"]
                        
                        # 중복 게시글 확인
                        if title in self.collected_titles or title in existing_titles:
                            self.log_message.emit({"message": f"⚠️ 중복 게시글 건너뜀: {title}", "color": "yellow"})
                            continue
                            
                        # 게시글 발견 시그널 발생
                        self.post_found.emit({
                            "no": self.post_count + 1,
                            "id": item["cafe_id"],
                            "content": title,
                            "url": item["url"] if item["url"].startswith(("http://", "https://")) else "https://" + item["url"]
                        })
                        
                        # 중복 확인을 위해 수집된 제목 저장
                        self.collected_titles.append(title)
                        
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