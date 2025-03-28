import requests
import html
import logging
import traceback
from bs4 import BeautifulSoup
import random
import re  # 정규표현식 모듈 추가

class CafeAPI:
    def __init__(self, headers):
        self.headers = {k: v for k, v in headers.items() if not k.startswith('_')}
        
    def get_cafe_list(self):
        """가입된 카페 목록 조회"""
        api_url = "https://apis.naver.com/cafe-home-web/cafe-home/v1/cafes/join?page=1&perPage=1000&type=join&recentUpdates=true"
        response = requests.get(api_url, headers=self.headers)
        data = response.json()
        
        # 딕셔너리 형태로 반환
        return [
            {
                'cafe_id': cafe['cafeId'], 
                'cafe_url': cafe['cafeUrl'], 
                'cafe_name': cafe['cafeName']
            } 
            for cafe in data['message']['result']['cafes']
        ]


    def check_cafe_id(self, url:str, cafe_id = None):
        if cafe_id:
            return cafe_id
    
        try:
            if not url.startswith("https://"):
                url = url.replace("http://", "")
                url = "https://" + url

            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            input_tag = soup.find('input', {'name': 'clubid'})
            return input_tag['value'] if input_tag else None
        except:
            logging.error(f"Cafe ID 추출 Error :: {traceback.format_exc()}")
            return False

    def get_board_list(self, cafe_id):
        """게시판 목록 조회"""
        try:
            menu_list = []
            url = f"https://apis.naver.com/cafe-web/cafe2/SideMenuList?cafeId={cafe_id}"
            response = requests.get(url, headers=self.headers)

            response_json = response.json()
            if response.status_code == 200:
                for menu in response_json['message']['result']['menus']:
                    if menu['menuType'] != 'P' and menu['menuType'] != 'L' and menu['menuType'] != 'F' and menu['menuType'] != 'M' and menu['boardType'] != 'T':
                        menu_list.append({
                            'board_id': menu['menuId'],
                            'board_name': menu['menuName'],
                            'menu_type': menu['menuType'],
                            'board_type': menu.get('boardType', ''),
                            'sort': menu.get('sort', 0)
                        })
            return menu_list
        except Exception as e:
            logging.error(f"게시판 목록 조회 오류: {str(e)}")
            return []
        
    def get_cafe_info(self, cafe_id):
        """카페 정보 조회"""
        url = f'https://cafe.naver.com/{cafe_id}'
        response = requests.get(url, headers=self.headers)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        info = {
            'id': cafe_id,
            'name': soup.select_one('.cafe-name').text.strip() if soup.select_one('.cafe-name') else '',
            'description': soup.select_one('.cafe-description').text.strip() if soup.select_one('.cafe-description') else ''
        }
        
        return info 

    def get_nickname(self, cafe_id):
        """카페 닉네임 조회"""
        try:
            url = f"https://apis.naver.com/cafe-web/cafe-cafeinfo-api/v2.0/cafes/{cafe_id}/member-profile/config"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                return data['result']['nickName']
            else:
                print(f"닉네임 조회 실패 - 상태 코드: {response.status_code}")
                print(f"응답 내용: {response.text}")
                return None
                
        except Exception as e:
            print(f"닉네임 조회 중 오류 발생: {str(e)}")
            print(traceback.format_exc())
            return None
            
    def update_nickname(self, cafe_id, new_nickname):
        """카페 닉네임 변경"""
        try:
            # 먼저 현재 프로필 정보 가져오기
            url = f"https://apis.naver.com/cafe-web/cafe-cafeinfo-api/v2.0/cafes/{cafe_id}/member-profile/config"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                print(f"프로필 정보 조회 실패 - 상태 코드: {response.status_code}")
                return False
                
            current_profile = response.json()['result']
            
            # 프로필 업데이트 요청
            update_url = f"https://apis.naver.com/cafe-web/cafe-cafeinfo-api/v3.0/cafes/{cafe_id}/member-profile"
            
            payload = {
                "allowMemberAlarm": current_profile['allowMemberAlarm'],
                "allowPopularMember": current_profile['allowPopularMember'],
                "cafeProfileImagePath": current_profile['cafeProfileImagePath'],
                "introduction": current_profile['introduction'],
                "nickname": new_nickname,  # 새로운 닉네임으로 변경
                "realNameUse": current_profile['realNameUse'],
                "receivingWholeMail": current_profile['receivingWholeMail'],
                "showBlog": current_profile['showBlog'],
                "showSexAndAge": current_profile['showSexAndAge']
            }
            
            # 업데이트용 헤더 설정
            headers = self.headers.copy()
            headers.update({
                'Content-Type': 'application/json',
                'Referer': f'https://cafe.naver.com/ca-fe/cafes/{cafe_id}/member-profile/setting'
            })
            
            update_response = requests.post(update_url, headers=headers, json=payload)
            
            if update_response.status_code == 200:
                print(f"닉네임 변경 성공: {new_nickname}")
                return True
            else:
                print(f"닉네임 변경 실패 - 상태 코드: {update_response.status_code}")
                print(f"응답 내용: {update_response.text}")
                return False
                
        except Exception as e:
            print(f"닉네임 변경 중 오류 발생: {str(e)}")
            print(traceback.format_exc())
            return False
        
    # 게시글 수집
    # menu_id를 비우고 요청할 경우 전체 글 조회
    # 제목뿐만 아니라 내용도 가져와야함
    def call_board_list(self, cafe_id, menu_id, per_page=20):
        result = []

        url = f"https://apis.naver.com/cafe-web/cafe2/ArticleListV2dot1.json?search.clubid={cafe_id}&search.queryType=lastArticle&search.menuid={menu_id}&search.page={1}&search.perPage={per_page}&adUnit=MW_CAFE_ARTICLE_LIST_RS"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                response_json = response.json()
                article_list = response_json['message']['result']['articleList']
                article_list = sorted(article_list, key=lambda x:x['articleId'])
                for article in article_list:
                    article_id = article['articleId']
                    subject = article['subject']
                    writer = article['writerNickname']
                    result.append({"article_id": article_id, "subject": subject, "writer": writer})

            return result
        except:
            logging.error("게시글 수집 실패: ", response_json['message'])

    # 게시글 내용 GET
    def get_board_content(self, cafe_id, article_id, art_param=None):
        """게시글 내용 가져오기
        
        Args:
            cafe_id (str): 카페 ID
            article_id (str): 게시글 ID
            art_param (str, optional): URL의 art 매개변수. 기본값은 None.
            
        Returns:
            str: 게시글 HTML 내용
        """
        # art 매개변수가 있으면 추가
        art_query = f"&art={art_param}" if art_param else ""
        url = f"https://apis.naver.com/cafe-web/cafe-articleapi/v2.1/cafes/{cafe_id}/articles/{article_id}?useCafeId=true&requestFrom=A{art_query}"

        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                response_json = response.json()
                return response_json['result']['article']['contentHtml']
        except Exception as e:
            logging.error(f"게시글 내용 수집 실패: {str(e)}")
            logging.error(traceback.format_exc())
            return None

    # 네이버 API에서 리턴받은 html 파싱
    def get_parse_content_html(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        # 내용 추출
        elements = soup.select('.se-module-text .se-text-paragraph span')
        content = ' '.join([element.get_text(strip=True) for element in elements])

        return content

    def get_board_title_and_content(self, cafe_id, menu_id, per_page):
        """게시판의 게시글 제목과 내용을 가져옵니다.
        
        Args:
            cafe_id (str): 카페 ID
            menu_id (str): 메뉴 ID
            per_page (int): 가져올 게시글 수
            
        Returns:
            str: 게시글 제목과 내용 정보
        """
        result = ""

        response = self.call_board_list(cafe_id, menu_id, per_page)

        content_cnt = 1
        for res in response:
            try:
                board_content = self.get_board_content(cafe_id, res['article_id'])
                content = self.get_parse_content_html(board_content)
                
                # 내용이 너무 길면 요약
                if content and len(content) > 200:
                    content = content[:200] + "..."
                
                result += f"게시글 {content_cnt}:\n제목: {res['subject']}\n내용: {content}\n\n"
                content_cnt += 1
            except Exception as e:
                logging.error(f"게시글 내용 수집 실패: {str(e)}")
                continue
            
        return result
    
    def like_board(self, cafe_id, article_id, cafe_name):
        """게시글에 좋아요를 누릅니다.
        
        Args:
            cafe_id (str): 카페 ID
            article_id (str): 게시글 ID
            
        Returns:
            bool: 좋아요 성공 여부
        """
        try:
            # 카페 URL 가져오기
            cafe_url = f"https://cafe.naver.com/{cafe_name}"
            
            # 게스트 토큰 및 타임스탬프 가져오기
            guest_token, timestamp = self.get_like_guest_token(cafe_id, article_id, cafe_name)

            print(f"게스트 토큰: {guest_token}, 타임스탬프: {timestamp}")
            
            # 좋아요 적용
            result = self.apply_board_like(cafe_id, guest_token, timestamp, article_id, cafe_url)

            print(f"좋아요 적용 결과: {result}")
            
            return result
        except Exception as e:
            logging.error(f"게시글 좋아요 실패: {str(e)}")
            logging.error(traceback.format_exc())
            return False
            
    def get_like_guest_token(self, cafe_id, article_id, cafe_name):
        """좋아요를 위한 게스트 토큰을 가져옵니다."""
        try:
            params = {
                'suppress_response_codes': 'true',
                'q': f'CAFE[{cafe_id}_{cafe_name}_{article_id}]|CAFE-COMMENT[{cafe_id}-{article_id}]',
                'isDuplication': 'true',
                'cssIds': 'BASIC_PC,CAFE_PC',
            }

            # 요청 보내기
            response = requests.get(
                'https://cafe.like.naver.com/v1/search/contents',
                headers=self.headers,
                params=params
            )

            response_json = response.json()
            
            if 'guestToken' in response_json and 'timestamp' in response_json:
                return response_json['guestToken'], response_json['timestamp']
            else:
                logging.error(f"게스트 토큰 가져오기 실패: {response_json}")
                return None, None
                
        except Exception as e:
            logging.error(f"게스트 토큰 가져오기 중 오류 발생: {str(e)}")
            logging.error(traceback.format_exc())
            return None, None

    def apply_board_like(self, cafe_id, guest_token, request_time, article_id, cafe_url):
        """게시글에 좋아요를 적용합니다."""
        try:
            if not guest_token or not request_time:
                logging.error("게스트 토큰 또는 타임스탬프가 없습니다.")
                return False
                
            # 정규 표현식으로 com/ 뒤에 오는 문자열 추출
            match = re.search(r'com/([^/?]+)', cafe_url)

            # 추출된 결과가 있는지 확인
            if match:
                cafe_url_param = match.group(1)
            else:
                logging.error("좋아요에 실패했습니다. cafe URL을 확인해주세요. (https://cafe.naver.com/cafe_id) 와 같은 형식이어야합니다.")
                return False

            params = {
                'suppress_response_codes': 'true',
                '_method': 'POST',
                'displayId': 'CAFE',
                'reactionType': 'like',
                'categoryId': cafe_id,
                'guestToken': guest_token,
                'timestamp': request_time,
                '_ch': 'pcw',
                'isDuplication': 'true',
                'lang': 'ko',
                'countType': 'default',
                'count': '1',
                'history': '',
                'runtimeStatus': '',
                'isPostTimeline': 'false',
            }

            # 요청 보내기
            response = requests.get(
                f'https://cafe.like.naver.com/v1/services/CAFE/contents/{cafe_id}_{cafe_url_param}_{article_id}',
                headers=self.headers,
                params=params,
            )

            if response.status_code == 200:
                print(response.text)
                logging.info(f"좋아요 성공: {response.text}")
                return True
            else:
                logging.error(f"좋아요 실패 - 상태 코드: {response.status_code}")
                logging.error(f"응답 내용: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"좋아요 적용 중 오류 발생: {str(e)}")
            logging.error(traceback.format_exc())
            return False
            
    def test_nickname(self, cafe_id):
        """닉네임 관련 기능 테스트"""
        try:
            # 현재 닉네임 조회
            current_nick = self.get_nickname(cafe_id)
            if current_nick:
                print(f"현재 닉네임: {current_nick}")
                
                # 테스트용 닉네임으로 변경
                test_nicks = [
                    "행복한하루123",
                    "즐거운여행가",
                    "꿈꾸는나비99",
                    "달콤한초코칩",
                    "푸른하늘별",
                    "웃는해바라기",
                    "신나는음악가",
                    "따뜻한커피향",
                    "자유로운영혼",
                    "평화로운마음"
                ]
                test_nick = random.choice(test_nicks)
                if self.update_nickname(cafe_id, test_nick):
                    print("닉네임 변경 테스트 성공")
                    
                    new_nick = self.get_nickname(cafe_id)
                    if new_nick == test_nick:
                        print(f"변경된 닉네임: {new_nick}")
                    else:
                        print("닉네임 변경 테스트 실패")
                else:
                    print("닉네임 변경 테스트 실패")
            else:
                print("현재 닉네임 조회 실패")
                
            return True
            
        except Exception as e:
            print(f"닉네임 테스트 중 오류 발생: {str(e)}")
            return False 
        
if __name__ == "__main__":
    headers = {
        "referer": "https://cafe.naver.com",
        'Cookie': "NNB=2QP3YT6BPGMWI; ASID=31a8f9cc0000018978da1f5400000064; ncvid=#vid#_115.138.87.199IWS1; ba.uuid=a76ad3c1-5903-42bd-8399-3eb89840598c; tooltipDisplayed=true; _ga_6Z6DP60WFK=GS1.2.1726462403.1.0.1726462403.60.0.0; NFS=2; _ga_EFBDNNF91G=GS1.1.1732339996.1.0.1732339999.0.0.0; _ga_8P4PY65YZ2=GS1.1.1734265772.1.1.1734265776.56.0.0; nstore_session=uajHtGrn2P2hNissMDvcn+a3; nstore_pagesession=iI4S7lqW4vuF/ssL/6s-089597; _ga=GA1.2.877073880.1704979036; NAC=3u9QBgQ0igR4; NACT=1; SRT30=1743141766; SRT5=1743141766; page_uid=i+hJCsqosesssgcC6P0sssssto4-194872; nid_inf=1949115776; NID_AUT=8+zmUwk32jOJx1p0ofhEwAxjHO7eblG7Tp9qf1RyzUkDdCvgupodIUjhBOaBt8O+; NID_SES=AAABkUy03E8qErQxsTkguNiZudXYaou4QovWwujx5hsnzVjj/J3DyvVNvCdlkSeQQRHoqaFBKPLGn+JSwDaPZ1kzzA4SLwGqKjxSS1tCufakLrnN07YbPY0e4aZW1/5UJywoCisHyX5An1A1WPfCytQw4rbwRENbgJB+wpHSyou/7xYLdhVWODSbWQLiqptkbP8/7wkaDipvkNHNmuq6NGZ567LPtRpKXLMt1fbzNFmRVS36EdmZQ1CVr9yHatfmV2tbRWhRhpJNJcoL4FgHi1WfOf+gvkSL043DQquyCq4HfwG9pAquNJUVYgt7aqckPoPGEFu9oHY7ylSoqg83y6rcAL7qz86RBBp/kuHABKYifvPd37VV1wubQbD3aBzZHlhKR88qkTdFyP7PQ2wQFi1q6Uotwbl1H9/WWq8a9+gOQMMzc9hvIJFPQdBiAAuoT3C+GS1Ppc74SRXQYRRknzGKFBjC5Vt66ahxu332+fVT8rFmdhznZFA4qJh9ABJkoRG3uh+kDu2rVAJMDsUAwAibpPLkYE8Wo1kjlJj913R95/bj; NID_JKL=lMgrdwUp+pDlFmNt7cmh5G1egmno71yydy0tMMsCzN0=; ncu=8bb05b2d3f7a1fdefb3d7a7b80681e2cd8; nci4=be8e6c47561a77c39b75322528ddba806528d33a6d1cf308d226c4692a981db46fed585892e9e88cbf5aeda614c72dbe11afff0488d1aae0e8f7b77dd48c5f89136ffd9afde888b36680ea86ff80909aaf77131b65131e39201103025858535b232f163102323a3510370945323d184072544b486f4a7b3641507752632a5b5671586925555e796051736b664e6a5b101311090f040d0f78775e794a0c6d0209fd90e6f999eaf5e4; ncvc2=d8b84064300607b59a611f2c1aea86f04904f210357f9a25c41d25f64d6c89428b74b269b3841c3544d98f539f35924ca3d8a6a84f31226557962be82a10bd6b0d15090007766b6e031f02070504131a1c120c110a151d152f292b282a5d5e7e596b606f603e38363f21313734373d4f494853425f4248444058585e5f2e2104231c09040953536368726e68636360616266667b647b777c787070767840; BUC=kH1LHnrDpvPXKxAQ_5sZMqXm72lhfR5mLEmUfw_LYW0=",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }
    
    cafe_api = CafeAPI(headers)
    
    # 닉네임 테스트
    #cafe_api.test_nickname("31203823")
    #print(cafe_api.get_nickname("31203823"))
    
    # 좋아요 테스트
    # 테스트할 카페 ID와 게시글 ID 설정
    # test_cafe_id = "31203823"
    # test_article_id = "489"  # 테스트할 게시글 ID 입력
    
    # # 좋아요 테스트 실행
    # print(f"게시글 좋아요 테스트 시작 - 카페 ID: {test_cafe_id}, 게시글 ID: {test_article_id}")
    # like_result = cafe_api.like_board(test_cafe_id, test_article_id, "grayfvggv")
    # if like_result:
    #     print("게시글 좋아요 성공!")
    # else:
    #     print("게시글 좋아요 실패!")
    # print(cafe_api.get_board_list("31203823"))
    # menu_type = M : 메모 게시판
    # board_type = T : 상품 게시판

    board_content = cafe_api.get_board_content("14131753", "2231643", "ZXh0ZXJuYWwtc2VydmljZS1uYXZlci1zZWFyY2gtY2FmZS1wcg.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjYWZlVHlwZSI6IkNBRkVfVVJMIiwiY2FmZVVybCI6Im1wM3ZpbGdlIiwiYXJ0aWNsZUlkIjoyMjMxNjQzLCJpc3N1ZWRBdCI6MTc0MzE0MTc3NjQ1N30.itnYvf22jvr6SOctPNiPtTs_qTI1ad2uLxZ5VCG0CLo")
    print(cafe_api.get_parse_content_html(board_content))
