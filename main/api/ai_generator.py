from main.utils.openai_utils import OpenAIGenerator
import os
import openai

class AIGenerator:
    def __init__(self, api_key=None):
        """AI 생성기 초기화
        
        Args:
            api_key (str, optional): OpenAI API 키. 기본값은 None.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.generator = OpenAIGenerator(api_key=self.api_key)
    
    def validate_api_key(self):
        """API 키 유효성 검사
        
        Returns:
            tuple: (is_valid, message)
                - is_valid (bool): API 키 유효 여부
                - message (str): 결과 메시지
        """
        if not self.api_key:
            return False, "API 키가 입력되지 않았습니다."
            
        try:
            # OpenAI 클라이언트 설정
            openai.api_key = self.api_key
            
            # API 키 검증을 위한 간단한 요청
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            
            # 응답이 성공적으로 왔다면 API 키가 유효한 것
            return True, "API 키가 유효합니다."
            
        except openai.AuthenticationError:
            return False, "유효하지 않은 API 키입니다."
        except openai.RateLimitError:
            return False, "API 사용량이 한도를 초과했습니다."
        except Exception as e:
            return False, f"API 키 검증 중 오류 발생: {str(e)}"
    
    def analyze_post_with_command(self, title, content, command):
        """제목과 게시글 내용을 분석하여 주어진 명령에 맞는 글인지 분석
        
        Args:
            title (str): 게시글 제목
            content (str): 게시글 내용
            command (str): 필터링 명령 (예: "자동차 사고글 피해자의 글만 추출")
        
        Returns:
            dict: 분석 결과
                - is_relevant (bool): 명령과의 관련성 여부 (True/False)
                - matched_keywords (list): 매칭된 키워드 목록
                - analysis (str): 분석 내용 요약
        """
        try:
            # OpenAI 클라이언트 설정
            openai.api_key = self.api_key
            
            # 분석 프롬프트 구성
            prompt = f"""
            제목: {title}
            내용: {content}
            
            명령: {command}
            
            위 명령에 따라 이 게시글이 해당 조건에 맞는지 분석해주세요.
            이 게시글이 명령 조건에 맞는지 정확히 True 또는 False로만 판단해주세요.
            
            다음 형식으로 응답해주세요:
            1. 관련성: [True/False]
            2. 매칭된 키워드: [매칭된 핵심 개념들]
            3. 분석: [판단 근거에 대한 간략한 설명]
            """
            
            # OpenAI API 호출
            response = openai.chat.completions.create(
                model="gpt-4o-mini",  # 또는 다른 적절한 모델
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # 더 결정적인 응답을 위해 temperature 낮춤
                max_tokens=500
            )
            
            # 응답 처리
            analysis_text = response.choices[0].message.content.strip()
            
            # 응답 파싱
            lines = analysis_text.split('\n')
            
            # 관련성 추출 (True/False)
            is_relevant = False
            if len(lines) > 0:
                relevance_line = lines[0].lower()
                is_relevant = 'true' in relevance_line
            
            # 매칭된 키워드 추출
            matched_keywords = []
            if len(lines) > 1:
                keywords_line = lines[1]
                if ':' in keywords_line:
                    keywords_text = keywords_line.split(':')[1].strip()
                    matched_keywords = [k.strip() for k in keywords_text.split(',')]
            
            # 분석 내용 추출
            analysis = ""
            if len(lines) > 2:
                analysis_line = ' '.join(lines[2:])
                if ':' in analysis_line:
                    analysis = analysis_line.split(':')[1].strip()
            
            return {
                "is_relevant": is_relevant,
                "matched_keywords": matched_keywords,
                "analysis": analysis
            }
            
        except Exception as e:
            return {
                "is_relevant": False,
                "matched_keywords": [],
                "analysis": f"분석 중 오류 발생: {str(e)}"
            }
