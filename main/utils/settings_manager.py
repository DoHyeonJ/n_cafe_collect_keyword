import os
import json
import shutil
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox

class SettingsManager:
    def __init__(self):
        # 실행 파일의 현재 디렉토리를 기준으로 settings 폴더 경로 설정
        self.settings_dir = os.path.join(os.getcwd(), "settings")
        
        # 설정 디렉토리 생성
        os.makedirs(self.settings_dir, exist_ok=True)
    
    def save_settings(self, settings_data, name=None):
        """설정 데이터를 파일로 저장"""
        if name is None:
            # 이름이 지정되지 않은 경우 현재 시간을 이용하여 파일명 생성
            name = f"settings_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 파일명에 .json 확장자가 없으면 추가
        if not name.endswith('.json'):
            name += '.json'
        
        file_path = os.path.join(self.settings_dir, name)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, ensure_ascii=False, indent=2)
            return True, file_path
        except Exception as e:
            return False, str(e)
    
    def load_settings(self, file_name):
        """파일에서 설정 데이터 로드"""
        file_path = os.path.join(self.settings_dir, file_name)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                settings_data = json.load(f)
            return True, settings_data
        except Exception as e:
            return False, str(e)
    
    def get_settings_list(self):
        """저장된 설정 파일 목록 반환"""
        if not os.path.exists(self.settings_dir):
            return []
        
        # .json 파일만 필터링
        files = [f for f in os.listdir(self.settings_dir) if f.endswith('.json')]
        # 수정 시간 기준으로 정렬 (최신 순)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(self.settings_dir, x)), reverse=True)
        return files
    
    def delete_settings(self, file_name):
        """설정 파일 삭제"""
        file_path = os.path.join(self.settings_dir, file_name)
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True, None
            else:
                return False, "파일이 존재하지 않습니다."
        except Exception as e:
            return False, str(e)
    
    def rename_settings(self, old_name, new_name):
        """설정 파일 이름 변경"""
        if not new_name.endswith('.json'):
            new_name += '.json'
            
        old_path = os.path.join(self.settings_dir, old_name)
        new_path = os.path.join(self.settings_dir, new_name)
        
        try:
            if os.path.exists(new_path):
                return False, "같은 이름의 파일이 이미 존재합니다."
                
            os.rename(old_path, new_path)
            return True, None
        except Exception as e:
            return False, str(e) 