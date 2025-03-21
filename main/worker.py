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
    
    def __init__(self, headers=None, search_keyword=None, api_key=None, options=None):
        """
        Worker 클래스 초기화
        
        Args:
            headers (dict): 로그인된 계정의 헤더 정보
            search_keyword (str): 검색 키워드
            api_key (str): OpenAI API 키
            options (dict): 검색 옵션
        """
        super().__init__()
        self.headers = headers
        self.search_keyword = search_keyword
        self.api_key = api_key
        self.options = options or {}
        self.is_running = False
        self.post_count = 0

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
        self.log_message.emit({"message": "작업이 중지되었습니다.", "color": "red"})
        
    def run(self):
        """작업 실행"""
        try:
            self.is_running = True
            
            # 01. 로그인된 계정의 헤더 정보를 가져온다.
            if not self.headers:
                self.log_message.emit({"message": "로그인된 계정 정보가 없습니다. 계정을 먼저 로그인해주세요.", "color": "red"})
                self.is_running = False
                return
            else:
                self.log_message.emit({"message": "로그인된 계정 정보가 확인되었습니다.", "color": "green"})
                
            # 검색 키워드 확인
            if not self.search_keyword:
                self.log_message.emit({"message": "검색 키워드가 설정되지 않았습니다.", "color": "red"})
                self.is_running = False
                return
            else:
                self.log_message.emit({"message": f"검색 키워드: '{self.search_keyword}'", "color": "blue"})
                
            # API 키 확인
            if not self.api_key:
                self.log_message.emit({"message": "OpenAI API 키가 설정되지 않았습니다.", "color": "red"})
                self.is_running = False
                return
                
            # API 키 검증
            self.log_message.emit({"message": "OpenAI API 키 검증 중...", "color": "blue"})
            ai_generator = AIGenerator(api_key=self.api_key)
            is_valid, message = ai_generator.validate_api_key()
            
            if not is_valid:
                self.log_message.emit({"message": f"API 키 검증 실패: {message}", "color": "red"})
                self.is_running = False
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
            
            # NaverCafeSearchAPI 인스턴스 생성 (headers 전달, OpenAI API 키는 전달하지 않음)
            search_api = NaverCafeSearchAPI()
            
            # 검색 실행
            search_results = search_api.search(
                query=self.search_keyword,
                max_items=max_items,
                cafe_where=cafe_where,
                date_option=date_option,
                sort=sort,
                page_delay=page_delay
            )
            
            # 03. 검색된 결과를 가져온다.
            if search_results["status"] != "success":
                self.log_message.emit({"message": "검색 결과를 가져오는데 실패했습니다.", "color": "red"})
                self.is_running = False
                return
                
            total_count = search_results["total_count"]
            self.log_message.emit({"message": f"총 {total_count}개의 게시글을 검색했습니다.", "color": "blue"})
            
            # CafeAPI 인스턴스 생성 (헤더 전달)
            cafe_api = CafeAPI(self.headers)
            
            # 04. 가져올 때 AI 분석 키워드가 있다면 분석 키워드로 필터해서 가져온다
            ai_filter_command = self.options.get("ai_filter_command", "")
            
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
                        content_preview = content[:100] + "..." if len(content) > 100 else content
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
                        # 게시글 발견 시그널 발생
                        self.post_found.emit({
                            "no": self.post_count + 1,
                            "id": item["cafe_id"],
                            "content": item["title"],
                            "url": item["url"] if item["url"].startswith(("http://", "https://")) else "https://" + item["url"]
                        })
                        
                        self.post_count += 1
                        
                        # 작업 간 딜레이
                        time.sleep(0.1)
                        
                    except Exception as e:
                        self.log_message.emit({"message": f"게시글 처리 중 오류 발생: {str(e)}", "color": "red"})
                        continue
            
            # 05. 수집된 정보를 모니터에 넣는다. (시그널로 전달)
            self.log_message.emit({"message": f"작업이 완료되었습니다. 총 {self.post_count}개의 게시글이 수집되었습니다.", "color": "green"})
            
        except Exception as e:
            self.log_message.emit({"message": f"작업 실행 중 오류 발생: {str(e)}", "color": "red"})
            self.log_message.emit({"message": traceback.format_exc(), "color": "red"})
        finally:
            self.is_running = False