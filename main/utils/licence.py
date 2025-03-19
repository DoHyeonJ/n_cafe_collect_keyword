import json
import os
import requests
import logging
import traceback
from datetime import datetime, timedelta

class Licence:
    def __init__(self):
        self.licence_key = None
        self.expiry_date = None
        self.load_licence()

    def load_licence(self):
        """라이선스 파일에서 라이선스 키를 로드합니다."""
        try:
            if os.path.exists('licence.json'):
                with open('licence.json', 'r', encoding='utf-8') as f:
                    licence_data = json.load(f)
                    self.licence_key = licence_data.get('licence', '')
                    self.expiry_date = licence_data.get('expires_at', None)
        except:
            logging.error(f"load_licence Error :: {traceback.format_exc()}")

    def save_licence(self, licence_key, expires_at):
        """라이선스 정보를 파일에 저장합니다."""
        try:
            licence_data = {
                'licence': licence_key
            }
            with open('licence.json', 'w', encoding='utf-8') as f:
                json.dump(licence_data, f, indent=4, ensure_ascii=False)
            self.licence_key = licence_key
            self.expiry_date = expires_at
            return True
        except:
            logging.error(f"save_licence Error :: {traceback.format_exc()}")
            return False

    def get_licence_key(self):
        """저장된 라이선스 키를 반환합니다."""
        return self.licence_key

    def check_license(self, licence_key):
        """라이선스 키의 유효성을 검증합니다."""
        try:
            url = "http://jdh7693.gabia.io/license"
            params = {
                "license_key": licence_key,
                "license_type": "N_CAFE_AI_ACTIVE"
            }
            headers = {
                "accept": "application/json"
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                return False, "라이선스 확인 중 알수 없는 오류가 발생했습니다."

            response_data = response.json()

            if response_data.get('status_code') == 200:
                expires_at = response_data['data']['expires_at']
                # 만료일 형식 검증
                datetime.strptime(expires_at, "%Y-%m-%d")
                # 라이선스 정보 저장
                if self.save_licence(licence_key, expires_at):
                    return True, expires_at
                else:
                    return False, "라이선스 정보 저장 중 오류가 발생했습니다."
            else:
                return False, response_data.get('detail', '유효하지 않은 라이선스입니다.')
            
        except Exception as e:
            logging.error(f"check_license Error :: {traceback.format_exc()}")
            return False, str(e)

    def get_expiry_date(self):
        """만료일을 반환합니다."""
        return self.expiry_date
    
    def get_days_left(self):
        """남은 일수를 계산합니다."""
        try:
            if not self.expiry_date:
                return 0
            expiry = datetime.strptime(self.expiry_date, "%Y-%m-%d")
            today = datetime.now()
            delta = expiry - today
            return delta.days
        except:
            logging.error(f"get_days_left Error :: {traceback.format_exc()}")
            return 0

    def is_expired(self):
        """라이선스가 만료되었는지 확인합니다."""
        try:
            if not self.expiry_date:
                return True
            days_left = self.get_days_left()
            return days_left <= 0
        except:
            logging.error(f"is_expired Error :: {traceback.format_exc()}")
            return True 