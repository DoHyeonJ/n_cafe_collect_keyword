import requests
from bs4 import BeautifulSoup
import json
import re
import urllib.parse
import time
import openai


class NaverCafeSearchAPI:
    def __init__(self, openai_api_key=None):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://search.naver.com',
            'Connection': 'keep-alive',
            # 'Cookie': 'NAC=ekgyDYA9LgdUB; NNB=DHF7IQNKTWLGM; ASID=738a57c700000190da1fcdb600000080; _ga_TC04LC8Q7L=GS1.1.1733757606.1.0.1733757609.57.0.0; _ga=GA1.2.886919162.1733757607; nid_inf=1965653744; NID_JKL=BzKL5h+EyiF79AmgaRWdAsa6rKL8gSYz6MkGURPyBic=; NACT=1; SRT30=1742292300; SRT5=1742292300; _naver_usersession_=20EYiaO5Ww5Sqyqb6GYvYA==; page_uid=i9DbPlqVJLhsskCx+QsssssssFK-200120; BUC=s2QlWH-WIyFAatJttWhmcYMpFTYHfwb8e09_hP8Atsg='
        }
        # OpenAI API 설정
        if openai_api_key:
            self.openai_api_key = openai_api_key
            openai.api_key = openai_api_key
            self.openai_client = openai.OpenAI(api_key=openai_api_key)
        else:
            self.openai_client = None
            
        self.is_running = True  # 검색 중지 플래그 추가

    def stop_search(self):
        """검색 중지"""
        self.is_running = False

    def search(self, query, max_items=100, cafe_where='articleg', date_option=2, sort='rel', page_delay=1, progress_callback=None):
        """
        네이버 카페 검색 API
        
        params:
            query (str): 검색어
            max_items (int): 수집할 최대 항목 수 (기본값: 100)
            cafe_where (str): 검색 대상 ('articleg'=일반글, 'articlec'=거래글, 'article'=전체글, 'cafe'=카페명)
            date_option (int): 기간 옵션 (0=전체, 1=1시간, 2=1일, 3=1주, 4=1개월, 5=3개월, 6=6개월, 7=1년)
            sort (str): 정렬 방식 ('rel'=관련도순, 'date'=최신순)
            page_delay (int): 페이지 간 요청 딜레이(초) (기본값: 1초)
            progress_callback (callable): 진행상황 콜백 함수 (추가)
        
        returns:
            dict: 검색 결과
        """
        all_results = []
        current_page = 1
        items_per_page = 30  # 네이버 검색은 페이지당 30개 항목
        
        # 날짜 옵션에 따른 nso 파라미터 설정
        nso_periods = {
            0: 'all',  # 전체
            1: '1h',   # 1시간
            2: '1d',   # 1일
            3: '1w',   # 1주
            4: '1m',   # 1개월
            5: '3m',   # 3개월
            6: '6m',   # 6개월
            7: '1y',   # 1년
        }
        
        # 정렬 방식에 따른 st 및 nso:so 설정
        sort_options = {
            'rel': 'rel',  # 관련도순
            'date': 'date'  # 최신순
        }
        so_options = {
            'rel': 'r',
            'date': 'dd'
        }
        
        # 기본 URL 설정
        url = 'https://search.naver.com/search.naver'
        nso = f"so:{so_options.get(sort, 'r')},p:{nso_periods.get(date_option, '1d')}"
        
        print(f"검색어 '{query}'에 대해 최대 {max_items}개 항목 수집을 시작합니다...")
        self.is_running = True  # 검색 시작
        
        while len(all_results) < max_items and self.is_running:  # 중지 플래그 확인
            # 한 페이지의 시작 인덱스 계산
            start_index = (current_page - 1) * items_per_page + 1
            
            params = {
                'cafe_where': cafe_where,
                'date_option': date_option,
                'nso_open': 1,
                'prdtype': 0,
                'query': query,
                'sm': 'mtb_opt',
                'ssc': 'tab.cafe.all',
                'st': sort_options.get(sort, 'rel'),
                'stnm': 'rel',
                'opt_tab': 0,
                'nso': nso,
                'start': start_index  # 페이지네이션을 위한 시작 인덱스
            }
            
            try:
                print(f"페이지 {current_page} 수집 중... (현재 {len(all_results)}개 항목)")
                
                # 진행상황 콜백 호출
                if progress_callback:
                    progress_callback(current_page, len(all_results), True)
                
                response = self.session.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                
                # HTML 파싱
                page_results = self._parse_search_results(response.text)
                
                # 결과가 없으면 종료
                if page_results['total_count'] == 0:
                    print(f"더 이상 검색 결과가 없습니다. 수집 종료 (총 {len(all_results)}개 항목)")
                    break
                
                # 결과 추가
                all_results.extend(page_results['items'])
                
                # 최대 수집 개수 제한
                if len(all_results) >= max_items:
                    all_results = all_results[:max_items]
                    break
                
                # 다음 페이지로 이동
                current_page += 1
                
                # 과도한 요청 방지를 위한 딜레이
                if page_delay > 0 and self.is_running:  # 중지 플래그 확인
                    time.sleep(page_delay)
                
            except requests.RequestException as e:
                print(f"요청 중 오류 발생: {e}")
                return {'error': str(e), 'status': 'error', 'items': all_results}
                
            # 중지 플래그 확인
            if not self.is_running:
                print("검색이 중지되었습니다.")
                break
        
        # 최종 진행상황 콜백 호출
        if progress_callback:
            progress_callback(current_page, len(all_results), False)
        
        return {
            'status': 'success',
            'total_count': len(all_results),
            'items': all_results
        }
    
    def _parse_search_results(self, html_content):
        """HTML에서 카페 검색 결과를 파싱하는 함수"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 결과를 저장할 리스트
        search_results = []
        
        # 카페 검색 결과 항목 찾기
        cafe_posts = soup.select('ul.lst_view li.bx')
        
        for post in cafe_posts:
            # 기본 데이터 구조 설정
            post_data = {
                'title': '',
                'content': '',
                'url': '',
                'cafe_name': '',
                'cafe_url': '',
                'post_date': '',
                'cafe_id': '',
                'article_id': '',
                'comments': []
            }
            
            # 게시글 제목
            title_element = post.select_one('.title_link')
            if title_element:
                post_data['title'] = title_element.get_text(strip=True)
                post_data['url'] = title_element.get('href', '')
                
                # cafe_id와 article_id 추출
                if post_data['url']:
                    match = re.search(r'cafe\.naver\.com/([^/]+)/(\d+)', post_data['url'])
                    if match:
                        post_data['cafe_id'] = match.group(1)
                        post_data['article_id'] = match.group(2)
            
            # 게시글 내용
            content_element = post.select_one('.dsc_link')
            if content_element:
                post_data['content'] = content_element.get_text(strip=True)
            
            # 카페 정보
            cafe_element = post.select_one('.user_info .name')
            if cafe_element:
                post_data['cafe_name'] = cafe_element.get_text(strip=True)
                post_data['cafe_url'] = cafe_element.get('href', '')
            
            # 게시글 작성 날짜
            date_element = post.select_one('.user_info .sub')
            if date_element:
                post_data['post_date'] = date_element.get_text(strip=True)
            
            # 댓글 정보
            comments = post.select('.comment_box .flick_bx')
            for comment in comments:
                comment_text = comment.select_one('.txt')
                if comment_text:
                    post_data['comments'].append(comment_text.get_text(strip=True))
            
            search_results.append(post_data)
        
        return {
            'status': 'success',
            'total_count': len(search_results),
            'items': search_results
        }
    
    def filter_victims_posts(self, search_results, batch_size=10):
        """
        OpenAI API를 사용하여 사고 피해자가 직접 작성한 게시글만 필터링하는 함수
        
        params:
            search_results (dict): 검색 결과
            batch_size (int): 한 번에 AI 분석할 게시글 수 (API 비용 절감을 위함)
            
        returns:
            dict: 피해자가 작성한 게시글만 포함된 결과
        """
        if not self.openai_client:
            print("OpenAI API 키가 설정되지 않아 필터링을 수행할 수 없습니다.")
            return search_results
        
        if search_results['status'] != 'success' or search_results['total_count'] == 0:
            return search_results
        
        # 분석할 게시글 수
        total_items = len(search_results['items'])
        victim_posts = []
        
        print(f"\n총 {total_items}개 게시글에 대해 피해자 작성 여부를 분석합니다...")
        
        # 게시글을 배치 단위로 처리
        for i in range(0, total_items, batch_size):
            batch_items = search_results['items'][i:i+batch_size]
            batch_texts = []
            
            # 배치 내 각 게시글의 정보 구성
            for item in batch_items:
                post_text = f"제목: {item['title']}\n내용: {item['content']}"
                batch_texts.append(post_text)
            
            print(f"배치 분석 중: {i+1}~{min(i+batch_size, total_items)}/{total_items} 게시글")
            
            # 구분자 정의 (f-string 내에서 백슬래시 사용 문제 해결)
            separator = "\n\n---\n\n"
            user_content = "다음 게시글들이 사고 피해자가 직접 작성한 것인지 분석해주세요. 각 게시글마다 'true' 또는 'false'로만 응답해주세요.\n\n" + separator.join(batch_texts)
            
            # OpenAI API 호출
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "당신은 게시글 분석 전문가입니다. 게시글이 차량 사고 피해자가 직접 작성한 것인지 분석해야 합니다. 피해자가 작성한 경우에만 'true'를, 그렇지 않으면 'false'를 반환하세요. 피해자는 사고로 인해 직접적인 피해를 입은 사람을 의미합니다."},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.1,
                    max_tokens=1500
                )
                
                # API 응답 처리
                ai_analysis = response.choices[0].message.content
                
                # 결과에서 true/false 추출
                results = re.findall(r'true|false', ai_analysis.lower())
                
                # 피해자 게시글만 필터링
                for j, result in enumerate(results):
                    if j < len(batch_items) and result.lower() == 'true':
                        # 피해자가 작성한 게시글로 판단된 경우
                        victim_posts.append(batch_items[j])
                        print(f"✓ 피해자 게시글 발견: {batch_items[j]['title']}")
                
                # API 요청 사이에 딜레이 추가
                time.sleep(1)
                
            except Exception as e:
                print(f"OpenAI API 호출 중 오류 발생: {e}")
                continue
        
        # 피해자 게시글만 포함된 결과 반환
        return {
            'status': 'success',
            'total_count': len(victim_posts),
            'items': victim_posts
        }


# 사용 예시
if __name__ == "__main__":
    # OpenAI API 키 설정 - 환경 변수 또는 직접 입력
    import os
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    
    if not OPENAI_API_KEY:
        OPENAI_API_KEY = input("OpenAI API 키를 입력하세요: ")
    
    # 네이버 API 클래스 초기화 (OpenAI API 키 전달)
    naver_api = NaverCafeSearchAPI(openai_api_key=OPENAI_API_KEY)
    
    # 검색어 '사고'로 100개 항목 수집
    results = naver_api.search(
        query='사고', 
        max_items=10000,  # 최대 100개 항목 수집
        cafe_where='articleg', 
        date_option=2, 
        sort='rel',
        page_delay=0.5  # 페이지 간 1초 딜레이
    )
    
    # 전체 검색 결과 저장
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    all_results_filename = f'naver_cafe_all_results_{timestamp}.json'
    
    with open(all_results_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n전체 검색 결과가 {all_results_filename} 파일로 저장되었습니다.")
    
    # 피해자가 작성한 게시글만 필터링
    victim_results = naver_api.filter_victims_posts(results, batch_size=5)
    
    # 피해자 게시글 결과 출력
    if victim_results['status'] == 'success':
        print(f"\n총 {victim_results['total_count']}개의 사고 피해자 게시글을 찾았습니다.")
        
        for idx, item in enumerate(victim_results['items'], 1):
            print(f"\n[{idx}] {item['title']}")
            print(f"카페: {item['cafe_name']}")
            print(f"게시글 ID: {item['article_id']}")
            print(f"카페 ID: {item['cafe_id']}")
            print(f"내용: {item['content'][:100]}..." if len(item['content']) > 100 else f"내용: {item['content']}")
            print(f"날짜: {item['post_date']}")
            print(f"URL: {item['url']}")
            
            if item['comments']:
                print(f"댓글 ({len(item['comments'])}개):")
                for comment in item['comments'][:3]:  # 댓글 최대 3개만 출력
                    print(f"- {comment[:50]}..." if len(comment) > 50 else f"- {comment}")
    else:
        print(f"오류 발생: {victim_results.get('error', '알 수 없는 오류')}")
    
    # 피해자 게시글만 JSON 파일로 저장
    victim_filename = f'naver_cafe_victim_results_{timestamp}.json'
    
    with open(victim_filename, 'w', encoding='utf-8') as f:
        json.dump(victim_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n피해자 게시글 결과가 {victim_filename} 파일로 저장되었습니다.")