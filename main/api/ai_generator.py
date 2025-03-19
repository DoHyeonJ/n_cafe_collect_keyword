from main.utils.openai_utils import OpenAIGenerator
import os

class AIGenerator:
    def __init__(self, api_key=None):
        """AI 생성기 초기화
        
        Args:
            api_key (str, optional): OpenAI API 키. 기본값은 None.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.generator = OpenAIGenerator(api_key=self.api_key)
    
    def validate_api_key(self):
        """API 키가 유효한지 확인합니다.
        
        Returns:
            tuple: (성공 여부(bool), 메시지(str))
        """
        try:
            return self.generator.validate_api_key()
        except Exception as e:
            return False, f"API 키 검증 중 오류 발생: {str(e)}"
    
    def generate_content(self, prompt, min_length=300, max_length=1000, model="gpt-4o-mini", temperature=0.7):
        """제목과 내용 생성
        
        Args:
            prompt (str): 생성 프롬프트
            min_length (int, optional): 최소 글자수. 기본값은 300.
            max_length (int, optional): 최대 글자수. 기본값은 1000.
            model (str, optional): 사용할 모델. 기본값은 "gpt-4o-mini".
            temperature (float, optional): 생성 다양성. 기본값은 0.7.
            
        Returns:
            dict: 생성된 제목과 내용을 포함하는 딕셔너리
        """
        # 프롬프트에 글자수 제한 추가
        full_prompt = f"{prompt}\n\n글자수 제한: {min_length}~{max_length}자 사이로 작성해주세요."
        
        # 최근 게시글 정보가 포함된 경우 추가 지시사항
        if "[최근 게시글 정보]" in prompt:
            full_prompt += """: 중요 :
        1. 최근 게시글들과 주제나 내용이 중복되지않게 우회해서 작성해주세요 (단, 프롬프트 요구사항의 주제에 맞춰서 작성되어야함)
        2. 최근 게시글에서 다루지 않은 관점이나 정보를 포함하세요.
        3. 최근 게시글의 제목과 유사하지 않은 독창적인 제목을 만드세요.
        4. 최근 게시글의 내용을 참고하되, 직접적인 복사나 유사한 표현은 피하세요."""
        
        try:
            # 게시글 생성 (제목 + 내용)
            result = self.generator.generate_post(full_prompt, model=model, temperature=temperature)
            
            # 결과 확인 및 반환
            if isinstance(result, dict) and 'title' in result and 'content' in result:
                return result
            else:
                # 응답 형식이 예상과 다른 경우 직접 생성
                title = self.generator.generate_title(f"{prompt}\n\n짧고 매력적인 제목을 생성해주세요.", model=model)
                content = self.generator.generate_content(full_prompt, model=model)
                return {
                    "title": title,
                    "content": content
                }
                
        except Exception as e:
            # 오류 발생 시 개별 생성 시도
            print(f"게시글 생성 중 오류 발생: {str(e)}")
            try:
                title = self.generator.generate_title(f"{prompt}\n\n짧고 매력적인 제목을 생성해주세요.", model=model)
                content = self.generator.generate_content(full_prompt, model=model)
                return {
                    "title": title,
                    "content": content
                }
            except Exception as e2:
                raise Exception(f"콘텐츠 생성 실패: {str(e2)}") 