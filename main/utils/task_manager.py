import os
import json
import shutil
from datetime import datetime

class TaskManager:
    """작업 설정 관리 클래스"""
    
    def __init__(self, base_dir="tasks"):
        """초기화
        
        Args:
            base_dir (str): 작업 설정 저장 기본 디렉토리
        """
        self.base_dir = base_dir
        
        # 기본 디렉토리 생성
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
    
    def save_task_settings(self, task_settings, filename):
        """작업 설정 저장
        
        Args:
            task_settings (dict): 저장할 작업 설정
            filename (str): 저장할 파일 이름 (확장자 제외)
            
        Returns:
            bool: 저장 성공 여부
        """
        try:
            # 파일 경로 생성
            file_path = os.path.join(self.base_dir, f"{filename}.json")
            
            # 저장 시간 추가
            task_settings['saved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # JSON 파일로 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(task_settings, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"작업 설정 저장 중 오류 발생: {str(e)}")
            return False
    
    def load_task_settings(self, filename):
        """작업 설정 불러오기
        
        Args:
            filename (str): 불러올 파일 이름 (확장자 제외)
            
        Returns:
            dict: 불러온 작업 설정 (실패 시 None)
        """
        try:
            # 파일 경로 생성
            file_path = os.path.join(self.base_dir, f"{filename}.json")
            
            # 파일 존재 여부 확인
            if not os.path.exists(file_path):
                print(f"파일이 존재하지 않습니다: {file_path}")
                return None
            
            # JSON 파일 불러오기
            with open(file_path, 'r', encoding='utf-8') as f:
                task_settings = json.load(f)
            
            return task_settings
        except Exception as e:
            print(f"작업 설정 불러오기 중 오류 발생: {str(e)}")
            return None
    
    def get_task_list(self):
        """저장된 작업 설정 목록 조회
        
        Returns:
            list: 작업 설정 파일 목록 (확장자 제외)
        """
        try:
            # 디렉토리 내 모든 파일 조회
            files = os.listdir(self.base_dir)
            
            # JSON 파일만 필터링하고 확장자 제거
            task_files = [os.path.splitext(f)[0] for f in files if f.endswith('.json')]
            
            return task_files
        except Exception as e:
            print(f"작업 설정 목록 조회 중 오류 발생: {str(e)}")
            return []
    
    def delete_task_settings(self, filename):
        """작업 설정 삭제
        
        Args:
            filename (str): 삭제할 파일 이름 (확장자 제외)
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            # 파일 경로 생성
            file_path = os.path.join(self.base_dir, f"{filename}.json")
            
            # 파일 존재 여부 확인
            if not os.path.exists(file_path):
                print(f"파일이 존재하지 않습니다: {file_path}")
                return False
            
            # 파일 삭제
            os.remove(file_path)
            
            return True
        except Exception as e:
            print(f"작업 설정 삭제 중 오류 발생: {str(e)}")
            return False
    
    def rename_task_settings(self, old_filename, new_filename):
        """작업 설정 이름 변경
        
        Args:
            old_filename (str): 기존 파일 이름 (확장자 제외)
            new_filename (str): 새 파일 이름 (확장자 제외)
            
        Returns:
            bool: 이름 변경 성공 여부
        """
        try:
            # 파일 경로 생성
            old_path = os.path.join(self.base_dir, f"{old_filename}.json")
            new_path = os.path.join(self.base_dir, f"{new_filename}.json")
            
            # 파일 존재 여부 확인
            if not os.path.exists(old_path):
                print(f"파일이 존재하지 않습니다: {old_path}")
                return False
            
            # 새 파일 이름이 이미 존재하는지 확인
            if os.path.exists(new_path):
                print(f"이미 존재하는 파일 이름입니다: {new_path}")
                return False
            
            # 파일 이름 변경
            os.rename(old_path, new_path)
            
            return True
        except Exception as e:
            print(f"작업 설정 이름 변경 중 오류 발생: {str(e)}")
            return False
    
    def get_task_info(self, filename):
        """작업 설정 정보 조회 (간략 정보)
        
        Args:
            filename (str): 조회할 파일 이름 (확장자 제외)
            
        Returns:
            dict: 작업 설정 간략 정보 (실패 시 None)
        """
        try:
            # 작업 설정 불러오기
            task_settings = self.load_task_settings(filename)
            
            if not task_settings:
                return None
            
            # 간략 정보 추출
            task_info = {
                'filename': filename,
                'saved_at': task_settings.get('saved_at', '알 수 없음'),
                'task_count': len(task_settings.get('tasks', [])),
                'account_count': len(task_settings.get('accounts', {})),
                'prompt_count': sum(len(task.get('comment_settings', {}).get('prompts', [])) 
                                  for task in task_settings.get('tasks', []))
            }
            
            return task_info
        except Exception as e:
            print(f"작업 설정 정보 조회 중 오류 발생: {str(e)}")
            return None 