from main.utils.openai_utils import OpenAIGenerator
import os
import openai
import json
import time
import logging

class AIGenerator:
    def __init__(self, api_key=None):
        """AI 생성기 초기화
        
        Args:
            api_key (str, optional): OpenAI API 키. 기본값은 None.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.generator = OpenAIGenerator(api_key=self.api_key)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("AIGenerator")
    
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
            self.logger.info("API 키 검증 중...")
            openai.api_key = self.api_key
            
            # API 키 검증을 위한 간단한 요청
            start_time = time.time()
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            elapsed_time = time.time() - start_time
            
            # 응답이 성공적으로 왔다면 API 키가 유효한 것
            self.logger.info(f"API 키 검증 성공 (응답 시간: {elapsed_time:.2f}초)")
            return True, f"API 키가 유효합니다. (응답 시간: {elapsed_time:.2f}초)"
            
        except openai.AuthenticationError:
            self.logger.error("API 키 인증 오류: 유효하지 않은 API 키")
            return False, "유효하지 않은 API 키입니다."
        except openai.RateLimitError:
            self.logger.error("API 키 오류: 사용량 한도 초과")
            return False, "API 사용량이 한도를 초과했습니다."
        except Exception as e:
            self.logger.error(f"API 키 검증 중 오류 발생: {str(e)}")
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
            # 로깅 시작
            self.logger.info(f"게시글 분석 시작: 제목=\"{title}\"")
            
            # 내용 요약: 너무 긴 내용은 일부만 로깅
            content_summary = content[:1000] + "..." if len(content) > 1000 else content
            self.logger.info(f"분석 내용 요약: {content_summary}")
            self.logger.info(f"분석 명령: {command}")
            
            # OpenAI 클라이언트 설정
            openai.api_key = self.api_key
            
            # 분석 프롬프트 구성
            prompt = f"""
            제목: {title}
            내용: {content}
            
            추출 조건: {command}
            
            당신은 엄격한 게시글 필터입니다. 아래 기준에 따라 게시글이 추출 조건에 정확히 부합하는지 판단하세요:
            
            1. 추출 조건을 매우 엄격하게 해석하세요.
            2. 모호하거나 간접적인 관련성만 있는 글은 반드시 False로 처리하세요.
            3. 관련 키워드가 단순히 언급되었다고 해서 True가 아닙니다.
            4. 게시글 내용이 추출 조건과 "100% 명확하게" 일치해야만 True입니다.
            5. 조금이라도 관련이 없거나 의심스러운 경우 반드시 False 처리하세요.
            
            최종 판단 과정:
            1. 게시글의 내용이 추출 조건에서 요구하는 정확한 주제/상황/조건과 완벽히 일치하는가?
            2. 게시글 내용이 조건에서 요구하는 모든 요소를 포함하고 있는가?
            3. 조금이라도 불일치하거나 불확실한 부분이 있다면 False 처리하세요.
            
            다음 형식으로 응답해주세요:
            1. 관련성: [True/False]
            2. 매칭된 키워드: [매칭된 핵심 개념들]
            3. 분석: [판단 근거에 대한 간략한 설명]
            """
            
            # OpenAI API 호출
            self.logger.info("OpenAI API 호출 중...")
            start_time = time.time()
            response = openai.chat.completions.create(
                model="gpt-4o-mini",  # 또는 다른 적절한 모델
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # 더 결정적인 응답을 위해 temperature 낮춤
                max_tokens=500
            )
            elapsed_time = time.time() - start_time
            self.logger.info(f"API 응답 완료 (소요 시간: {elapsed_time:.2f}초)")
            
            # 응답 처리
            analysis_text = response.choices[0].message.content.strip()
            self.logger.info(f"원본 응답:\n{analysis_text}")
            
            # 응답 파싱
            lines = analysis_text.split('\n')
            
            # 관련성 추출 (True/False)
            is_relevant = False
            if len(lines) > 0:
                relevance_line = lines[0].lower()
                is_relevant = 'true' in relevance_line
                self.logger.info(f"관련성 판단: {is_relevant}")
            
            # 매칭된 키워드 추출
            matched_keywords = []
            if len(lines) > 1:
                keywords_line = lines[1]
                if ':' in keywords_line:
                    keywords_text = keywords_line.split(':')[1].strip()
                    matched_keywords = [k.strip() for k in keywords_text.split(',')]
                    self.logger.info(f"매칭된 키워드: {matched_keywords}")
            
            # 분석 내용 추출
            analysis = ""
            if len(lines) > 2:
                analysis_line = ' '.join(lines[2:])
                if ':' in analysis_line:
                    analysis = analysis_line.split(':')[1].strip()
                    self.logger.info(f"분석 내용: {analysis}")
            
            # 최종 분석 결과
            result = {
                "is_relevant": is_relevant,
                "matched_keywords": matched_keywords,
                "analysis": analysis
            }
            
            self.logger.info(f"분석 결과: {json.dumps(result, ensure_ascii=False)}")
            return result
            
        except Exception as e:
            self.logger.error(f"분석 중 오류 발생: {str(e)}")
            return {
                "is_relevant": False,
                "matched_keywords": [],
                "analysis": f"분석 중 오류 발생: {str(e)}"
            }

if __name__ == "__main__":
    ai_generator = AIGenerator()
    result = ai_generator.analyze_post_with_command("테스트 제목", "테스트 내용", "테스트 명령")
    print(result)

