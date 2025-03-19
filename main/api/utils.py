import json
from urllib.parse import urlencode

def get_csrf_token(soup):
    """CSRF 토큰 추출"""
    token_input = soup.find('input', {'name': 'csrf_token'})
    return token_input.get('value') if token_input else None
    
def encode_params(params):
    """파라미터 인코딩"""
    return urlencode(params, encoding='utf-8')
    
def handle_response(response):
    """API 응답 처리"""
    try:
        result = response.json()
        
        # 게시글 작성 응답 처리
        if response.status_code == 200 and 'result' in result:
            article_data = result.get('result', {})
            
            # 게시글 작성 응답인 경우
            if 'cafeId' in article_data and 'articleId' in article_data:
                cafe_id = article_data.get('cafeId')
                article_id = article_data.get('articleId')
                
                # 기본 카페 URL 생성 (이전 형식)
                article_url = f"https://cafe.naver.com/cafes/{cafe_id}/articles/{article_id}"
                
                # 응답 데이터 구성
                response_data = {
                    'success': True,
                    'article_id': article_id,
                    'cafe_id': cafe_id,
                    'article_url': article_url
                }
                
                # 추가 정보가 있는 경우 (카페 이름 등)
                if hasattr(response, 'request') and hasattr(response.request, 'headers'):
                    headers = response.request.headers
                    if 'referer' in headers:
                        referer = headers['referer']
                        if 'cafe.naver.com/' in referer:
                            # 카페 이름 추출 시도
                            try:
                                cafe_name_part = referer.split('cafe.naver.com/')[1].split('/')[0].split('?')[0]
                                if cafe_name_part and cafe_name_part != 'ArticleRead.nhn':
                                    # 카페 이름이 있는 경우 URL 형식 변경
                                    response_data['article_url'] = f"https://cafe.naver.com/{cafe_name_part}/{article_id}"
                            except:
                                pass
                
                return response_data
        
        return result
    except json.JSONDecodeError:
        return {'success': False, 'message': 'Invalid response format'} 