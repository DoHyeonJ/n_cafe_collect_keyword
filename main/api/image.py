import os
from bs4 import BeautifulSoup
from main.api.utils import handle_response
import requests
import xml.etree.ElementTree as ET

class ImageAPI:
    def __init__(self, headers):
        self.headers = headers
        
    def upload(self, cafe_id, image_path, session_key):
        """이미지 업로드"""
        url = f'https://cafe.upphoto.naver.com/{session_key}/simpleUpload/0'
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")
            
        with open(image_path, 'rb') as f:
            files = {
                'image': (os.path.basename(image_path), f, 'image/jpeg')
            }
            
            params = {
                'userId': self.headers.get('userId', ''),
                'extractExif': 'true',
                'extractAnimatedCnt': 'true',
                'autorotate': 'true',
                'extractDominantColor': 'false',
                'type': '',
                'denyAnimatedImage': 'false',
                'skipXcamFiltering': 'false'
            }
            
            # 이미지 업로드용 헤더 설정
            upload_headers = {
                'accept': 'application/json',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'ko',
                'cookie': self.headers['Cookie'] if 'Cookie' in self.headers else self.headers['cookie'],
                'origin': 'https://cafe.naver.com',
                'pragma': 'no-cache',
                'referer': f'https://cafe.naver.com/ca-fe/cafes/{cafe_id}/articles/write',
                'se-authorization': self.headers.get('se-authorization', ''),
                'user-agent': self.headers['user-agent']
            }
            
            response = requests.post(url, headers=upload_headers, params=params, files=files)
            if response.status_code == 200:
                return self._parse_image_response(response.text)
            return None
            
    def _parse_image_response(self, xml_response):
        """이미지 업로드 응답 파싱"""
        try:
            root = ET.fromstring(xml_response.strip())
            if root.tag == 'item':
                image_info = {
                    'url': root.find('url').text,
                    'path': root.find('path').text,
                    'fileName': root.find('fileName').text,
                    # 'width': int(root.find('width').text),
                    # 'height': int(root.find('height').text),
                    'width': 400,
                    'height': 400,
                    'fileSize': int(root.find('fileSize').text),
                    'thumbnail': root.find('thumbnail').text,
                    'imageType': root.find('imageType').text,
                    'src': f"https://cafeptthumb-phinf.pstatic.net{root.find('url').text}?type=w1600"
                }
                return image_info
            return None
            
        except Exception as e:
            print(f"XML 파싱 오류: {str(e)}")
            return None
        
    def get_image_info(self, image_id):
        """이미지 정보 조회"""
        url = f'https://cafe.naver.com/api/cafe-image/{image_id}'
        response = requests.get(url, headers=self.headers)
        return handle_response(response) 