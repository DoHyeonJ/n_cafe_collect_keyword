from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
import platform
import pyperclip
import logging
import requests
import os
import time

class NaverAuth:
    def __init__(self):
        self.session = requests.Session()
        self.headers = None
        self.username = None
        self.password = None
        
    def set_credentials(self, username, password):
        """로그인 자격 증명 설정"""
        self.username = username
        self.password = password
        
    def _open_web_mode(self):
        driver_path = ChromeDriverManager().install()

        # OS에 따라 다른 드라이버 경로 설정
        if platform.system() == "Windows":
            correct_driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver.exe")
        else:
            correct_driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver")

        self.driver = webdriver.Chrome(service=Service(executable_path=correct_driver_path))
        self.driver.set_page_load_timeout(120)

    def login(self, username=None, password=None):
        """네이버 로그인 (자격 증명 사용)"""
        # 인자로 전달된 경우 자격 증명 업데이트
        if username and password:
            self.set_credentials(username, password)
            
        if not self.username or not self.password:
            return False, None
            
        # 기존 로그인 로직 사용
        success = self._login_with_credentials(self.username, self.password)
        
        if success:
            try:
                # imgs 폴더 확인 및 생성
                if not os.path.exists('imgs'):
                    os.makedirs('imgs')
                    
                # 계정별 이미지 폴더 확인 및 생성
                if self.username:  # username이 존재하는 경우에만 폴더 생성
                    account_img_dir = os.path.join('imgs', self.username)
                    if not os.path.exists(account_img_dir):
                        os.makedirs(account_img_dir)
                return True, self.get_headers()
            except Exception as e:
                print(f"폴더 생성 중 오류 발생: {str(e)}")
                return False, None
        return False, None
        
    def _login_with_credentials(self, username, password):
        """실제 로그인 처리 (기존 login 메서드 내용)"""
        self._open_web_mode()
        self.driver.get("https://nid.naver.com/nidlogin.login?mode=form")

        # 아이디 입력
        id_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "id"))
        )
        id_input.click()
        pyperclip.copy(username)
        
        actions = ActionChains(self.driver)
        if platform.system() == 'Darwin':  # macOS
            actions.key_down(Keys.COMMAND).send_keys('v').key_up(Keys.COMMAND).perform()
        else:  # Windows and others
            actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

        # 패스워드 입력
        pw_input = self.driver.find_element(By.ID, "pw")
        pw_input.click()
        pyperclip.copy(password)
        
        if platform.system() == 'Darwin':  # macOS
            actions.key_down(Keys.COMMAND).send_keys('v').key_up(Keys.COMMAND).perform()
        else:  # Windows and others
            actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

        # 로그인 버튼 클릭
        login_btn = self.driver.find_element(By.ID, "log.login")
        login_btn.click()

        try:
            err_common = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.ID, "err_common"))
            )
            error_msg = err_common.find_element(By.CSS_SELECTOR ,".error_message")
            if error_msg.text:
                logging.info("로그인 실패")
                self.driver.quit()
                return False
        except:
            logging.info("로그인 실패메세지 pass")

        # 로그인 후 처리
        try:
            element = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.btn_cancel"))
            )
            element.click()
        except:
            logging.info("등록안함 pass")

        # 2차 인증 체크
        try:
            element = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button#useotpBtn"))
            )
            logging.info("2차 인증이 존재합니다. 인증을 완료해주세요.")
        except:
            logging.info("2차 인증 pass")

        # 쿠키 및 헤더 설정
        try:
            element = WebDriverWait(self.driver, 240).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.search_area"))
            )
        except:
            logging.info("메인 페이지 접근 실패")
            return False

        cookies = self.driver.get_cookies()
        result_cookie_str = ""
        for cookie in cookies:
            key = cookie['name']
            value = cookie['value']
            result_cookie_str = f"{result_cookie_str} {key}={value};"
        
        if cookies:
            user_agent = self.driver.execute_script("return navigator.userAgent;")
            self.headers = {
                "x-cafe-product": "pc",
                'Cookie': result_cookie_str.strip(),
                'Referer': 'https://cafe.naver.com/',
                'User-Agent': user_agent
            }
            self.driver.quit()
            return True
        
        self.driver.quit()
        return False

    def get_headers(self):
        """로그인 후 헤더 정보 반환 (타임스탬프 추가)"""
        headers = {
            "x-cafe-product": "pc",
            'Cookie': self.headers['Cookie'],
            'Referer': 'https://cafe.naver.com/',
            'User-Agent': self.headers['User-Agent']
        }
        
        # 타임스탬프는 헤더에 직접 추가하지 않고 별도 필드로 저장
        # 헤더는 HTTP 요청에만 사용되는 값이므로 내부 용도의 값은 별도로 관리
        result = headers.copy()
        result['_timestamp'] = time.time()  # 언더스코어로 시작하여 내부용 필드임을 표시
        
        return result

    def check_login(self):
        """로그인 상태 확인"""
        # 프로필 페이지로 요청을 보내 로그인 상태 확인
        profile_url = 'https://nid.naver.com/user2/help/myInfo.nhn'
        response = self.session.get(profile_url)
        return 'Login' not in response.url
        
    def logout(self):
        """로그아웃"""
        logout_url = 'https://nid.naver.com/nidlogin.logout'
        self.session.get(logout_url)
        self.session = requests.Session() 