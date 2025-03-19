import os
from openai import OpenAI
import json
import time

class OpenAIGenerator:
    def __init__(self, api_key=None):
        """OpenAI API를 사용하여 텍스트를 생성하는 클래스"""
        # API 키 설정
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API 키가 필요합니다.")
        
        # OpenAI 클라이언트 초기화
        self.client = OpenAI(api_key=self.api_key)
    
    def validate_api_key(self):
        """
        API 키가 유효한지 확인합니다.
        
        Returns:
            tuple: (성공 여부(bool), 메시지(str))
        """
        try:
            # 간단한 요청으로 API 키 유효성 검사
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "API 키 검증 테스트입니다."}
                ],
                max_tokens=5
            )
            
            # 응답이 있으면 유효한 API 키
            if response and hasattr(response, 'choices') and len(response.choices) > 0:
                return True, "API 키가 유효합니다."
            else:
                return False, "API 키가 유효하지 않습니다."
                
        except Exception as e:
            error_message = str(e)
            if "Incorrect API key" in error_message or "Invalid API key" in error_message:
                return False, "잘못된 API 키입니다."
            elif "exceeded your current quota" in error_message:
                return False, "API 키 사용량이 한도를 초과했습니다."
            else:
                return False, f"API 키 검증 중 오류 발생: {error_message}"
    
    def generate_post(self, prompt, model="gpt-4o-mini", max_retries=3, temperature=0.7):
        """
        게시글 제목과 내용을 생성합니다.
        
        Args:
            prompt (str): 게시글 생성을 위한 프롬프트
            model (str): 사용할 OpenAI 모델
            max_retries (int): 최대 재시도 횟수
            temperature (float): 생성 다양성 조절 (0.0 ~ 1.0)
            
        Returns:
            dict: 생성된 제목과 내용을 포함하는 딕셔너리
        """
        system_message = """
        당신은 네이버 카페 게시글 작성을 도와주는 AI입니다.
        사용자의 요청에 따라 적절한 제목과 내용을 생성해주세요.
        응답은 반드시 다음 JSON 형식으로 제공해야 합니다:
        마크다운 문법은 사용하지않고 일반적인 텍스트로 작성해주세요.
        반드시 개행문자를 사용하여 자연스러운 게시글을 작성해주세요.
        {
            "title": "게시글 제목",
            "content": "게시글 내용"
        }
        """
        
        retry_count = 0
        while retry_count < max_retries:
            try:
                # gpt-4o-mini 모델은 response_format 파라미터를 지원하지 않을 수 있음
                if model == "gpt-4o-mini":
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=temperature
                    )
                else:
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=temperature,
                        response_format={"type": "json_object"}
                    )
                
                # 응답 파싱
                try:
                    result = json.loads(response.choices[0].message.content)
                except json.JSONDecodeError:
                    # JSON 파싱 실패 시 텍스트 응답에서 제목과 내용 추출 시도
                    content = response.choices[0].message.content
                    # 간단한 제목 추출 (첫 줄을 제목으로 사용)
                    lines = content.strip().split('\n')
                    title = lines[0].strip()
                    # 나머지를 내용으로 사용
                    content = '\n'.join(lines[1:]).strip()
                    result = {"title": title, "content": content}
                
                # 필수 필드 확인
                if "title" not in result or "content" not in result:
                    raise ValueError("응답에 필수 필드(title, content)가 없습니다.")
                
                return result
                
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise Exception(f"OpenAI API 호출 실패: {str(e)}")
                time.sleep(2)  # 재시도 전 대기
    
    def generate_title(self, prompt, model="gpt-4o-mini", max_retries=3, temperature=0.7):
        """게시글 제목만 생성합니다."""
        system_message = "당신은 네이버 카페 게시글 제목을 생성하는 AI입니다. 사용자의 요청에 따라 적절한 제목을 생성해주세요."
        
        retry_count = 0
        while retry_count < max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=50
                )
                
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise Exception(f"OpenAI API 호출 실패: {str(e)}")
                time.sleep(2)  # 재시도 전 대기
    
    def generate_content(self, prompt, model="gpt-4o-mini", max_retries=3, temperature=0.7):
        """게시글 내용만 생성합니다."""
        system_message = "당신은 네이버 카페 게시글 내용을 생성하는 AI입니다. 사용자의 요청에 따라 적절한 내용을 생성해주세요."
        
        retry_count = 0
        while retry_count < max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature
                )
                
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise Exception(f"OpenAI API 호출 실패: {str(e)}")
                time.sleep(2)  # 재시도 전 대기
    
    def generate_comment(self, prompt, comment_type='comment', model="gpt-4o-mini", max_retries=3, temperature=0.7):
        """댓글 내용을 생성합니다.
        
        Args:
            prompt (str): 댓글 생성을 위한 프롬프트
            comment_type (str): 댓글 유형 ('comment' 또는 'reply')
            model (str): 사용할 OpenAI 모델
            max_retries (int): 최대 재시도 횟수
            temperature (float): 생성 다양성 조절 (0.0 ~ 1.0)
            
        Returns:
            str: 생성된 댓글 내용
        """
        # 댓글 유형에 따른 시스템 메시지 설정
        if comment_type == 'comment':
            system_message = """
            당신은 네이버 카페의 댓글을 작성하는 AI입니다.
            게시글의 내용을 이해하고 이에 대한 의견이나 감상을 댓글로 작성해주세요.
            
            다음 사항을 반드시 지켜주세요:
            1. 게시글의 내용에 초점을 맞추어 댓글을 작성합니다.
            2. 게시글에서 언급된 주제나 내용에 대한 자신의 생각이나 경험을 공유합니다.
            3. 게시글 작성자의 의견이나 상황에 공감하는 내용을 포함합니다.
            4. 선택된 성향(말투)에 맞게 일관성 있게 작성합니다.
            5. JSON이나 다른 형식이 아닌, 순수한 댓글 텍스트만 반환합니다.
            """
        else:  # reply (대댓글)
            system_message = """
            당신은 네이버 카페의 대댓글을 작성하는 AI입니다.
            이전 댓글의 내용을 이해하고 이에 대한 반응이나 대화를 이어가는 대댓글을 작성해주세요.
            
            다음 사항을 반드시 지켜주세요:
            1. 이전 댓글의 내용에 초점을 맞추어 대댓글을 작성합니다.
            2. 이전 댓글에서 언급된 내용에 대한 동의/반대 의견이나 추가 질문을 포함합니다.
            3. 자연스러운 대화가 이어지도록 이전 댓글의 맥락을 유지합니다.
            4. 선택된 성향(말투)에 맞게 일관성 있게 작성합니다.
            5. JSON이나 다른 형식이 아닌, 순수한 댓글 텍스트만 반환합니다.
            6. 프롬프트에서 지정된 역할(댓글 작성자 또는 게시글 작성자)에 맞게 대화를 이어갑니다.
            7. 이전 댓글에 질문이 있다면 그 질문에 대한 답변을 포함합니다.
            8. 이전 대화 내용과 중복되지 않는 새로운 내용을 작성합니다.
            """
        
        retry_count = 0
        while retry_count < max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature
                )
                
                # 댓글 내용만 반환
                comment = response.choices[0].message.content.strip()
                
                # 댓글이 너무 길면 적절히 자르기
                # if len(comment) > 200:
                #     comment = comment[:200]
                
                return comment
                
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise Exception(f"OpenAI API 호출 실패: {str(e)}")
                time.sleep(2)  # 재시도 전 대기

    def generate_simple_comment(self, prompt, style_prompt, model="gpt-4o-mini", max_retries=3, temperature=0.7):
        """성향 및 말투가 적용된 일반 댓글 내용을 생성합니다.
        
        Args:
            prompt (str): 댓글 생성을 위한 프롬프트 (게시글 내용 등)
            style_prompt (str): 성향 및 말투를 지정하는 프롬프트
            model (str): 사용할 OpenAI 모델
            max_retries (int): 최대 재시도 횟수
            temperature (float): 생성 다양성 조절 (0.0 ~ 1.0)
            
        Returns:
            str: 생성된 댓글 내용
        """
        # 시스템 메시지 설정
        system_message = f"""
        당신은 네이버 카페의 일반적인 유저입니다.
        제공되는 게시글의 내용을 이해하고 이에 대한 댓글을 작성해주세요.
        
        아래의 성향과 말투에 맞춰 작성해주세요:
        {style_prompt}
        
        - JSON이나 다른 형식이 아닌, 순수한 댓글 텍스트만 반환합니다.
        """
        
        retry_count = 0
        while retry_count < max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature
                )
                
                # 댓글 내용만 반환
                comment = response.choices[0].message.content.strip()
                
                return comment
                
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise Exception(f"OpenAI API 호출 실패: {str(e)}")
                time.sleep(2)  # 재시도 전 대기 