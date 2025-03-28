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
                model="gpt-4o-mini",
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

    def analyze_posts_batch(self, posts, command, batch_size=20, progress_callback=None):
        """여러 게시글을 배치로 처리하여 분석
        
        Args:
            posts (list): 분석할 게시글 목록 (각 항목은 {'title': '제목', 'content': '내용'} 형태)
            command (str): 필터링 명령 (예: "자동차 사고글 피해자의 글만 추출")
            batch_size (int): 한 번에 처리할 게시글 수 (기본값: 20)
            progress_callback (callable, optional): 진행 상황 콜백 함수
                - 호출 시 (batch_index, batch_count, is_processing) 전달
            
        Returns:
            list: 각 게시글의 분석 결과 (True/False)
        """
        try:
            self.logger.info(f"배치 분석 시작: {len(posts)}개 게시글, 배치 크기: {batch_size}")
            
            # 결과 저장용 리스트
            results = []
            
            # 전체 배치 수 계산
            batch_count = (len(posts) + batch_size - 1) // batch_size
            
            # 배치 단위로 처리
            for i in range(0, len(posts), batch_size):
                batch_index = i // batch_size + 1
                batch = posts[i:i+batch_size]
                self.logger.info(f"배치 처리 중: {i+1}~{min(i+batch_size, len(posts))}/{len(posts)}")
                
                # 진행 상황 콜백 호출
                if progress_callback:
                    progress_callback(batch_index, batch_count, True)
                
                # 배치 내 각 게시글 정보 구성
                batch_texts = []
                for post in batch:
                    title = post.get('title', '')
                    content = post.get('content', '')
                    # 내용은 300자로 제한하여 분석 속도 향상
                    content_preview = content[:300] if content else ""
                    post_text = f"제목: {title}\n내용: {content_preview}"
                    batch_texts.append(post_text)
                
                # OpenAI API 설정
                openai.api_key = self.api_key
                
                # 배치 분석 프롬프트 구성
                batch_prompt = f"""
                다음 게시글들이 "{command}" 조건에 맞는지 판단하세요.
                
                각 게시글마다 True 또는 False로만 답변하세요. 이유나 설명은 쓰지 마세요.
                조건과 정확히 일치하는 경우만 True, 불확실하면 False로 응답하세요.
                
                게시글:
                """
                
                for idx, text in enumerate(batch_texts):
                    batch_prompt += f"\n게시글 {idx+1}:\n{text}\n"
                
                batch_prompt += "\n결과 (True 또는 False만 입력):\n"
                
                # OpenAI API 호출
                self.logger.info("배치 분석 API 호출 중...")
                start_time = time.time()
                try:
                    response = openai.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": batch_prompt}],
                        temperature=0.1,
                        max_tokens=200,
                        timeout=10  # 10초 타임아웃 설정
                    )
                    elapsed_time = time.time() - start_time
                    self.logger.info(f"배치 분석 API 응답 완료 (소요 시간: {elapsed_time:.2f}초)")
                
                    # 응답 처리
                    analysis_text = response.choices[0].message.content.strip()
                    self.logger.info(f"배치 분석 원본 응답:\n{analysis_text}")
                except (openai.Timeout, TimeoutError) as e:
                    self.logger.error(f"배치 분석 API 호출 타임아웃: {str(e)}")
                    # 타임아웃 발생 시 모든 게시글에 대해 False 반환
                    batch_false_values = [False] * len(batch)
                    results.extend(batch_false_values)
                    
                    # 진행 상황 콜백 호출 (배치 완료)
                    if progress_callback:
                        progress_callback(batch_index, batch_count, False)
                    
                    # 다음 배치로 넘어감
                    continue
                
                # True/False 결과 추출
                true_false_values = []
                try:
                    lines = analysis_text.lower().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line == 'true':
                            true_false_values.append(True)
                        elif line == 'false':
                            true_false_values.append(False)
                except Exception as e:
                    self.logger.error(f"응답 파싱 중 오류 발생: {str(e)}")
                    # 파싱 오류 시 모든 게시글을 False로 처리
                    true_false_values = [False] * len(batch)
                
                # 결과 개수가 일치하지 않을 경우 처리
                if len(true_false_values) != len(batch):
                    self.logger.error(f"배치 분석 결과 개수 불일치: 요청={len(batch)}, 응답={len(true_false_values)}")
                    # 부족한 결과는 기본값 False로 채움
                    while len(true_false_values) < len(batch):
                        true_false_values.append(False)
                    # 초과 결과는 잘라냄
                    true_false_values = true_false_values[:len(batch)]
                
                # 배치 결과를 전체 결과에 추가
                results.extend(true_false_values)
                self.logger.info(f"배치 분석 결과: {true_false_values}")
                
                # 진행 상황 콜백 호출 (배치 완료)
                if progress_callback:
                    progress_callback(batch_index, batch_count, False)
                
                # API 요청 사이에 딜레이 추가
                time.sleep(0.5)
            
            self.logger.info(f"전체 배치 분석 완료: 총 {len(posts)}개 게시글")
            return results
            
        except Exception as e:
            self.logger.error(f"배치 분석 중 오류 발생: {str(e)}")
            # 오류 발생 시 모든 게시글에 대해 False 반환
            return [False] * len(posts)

if __name__ == "__main__":
    ai_generator = AIGenerator()
    result = ai_generator.analyze_post_with_command("테스트 제목", "테스트 내용", "테스트 명령")
    print(result)

