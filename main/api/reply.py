import requests
import traceback
import time

class ReplyAPI:
    def __init__(self, headers):
        self.headers = headers
        
    def write_reply(self, cafe_id, article_id, content, emoji_code=""):
        """댓글 작성"""
        try:
            url = "https://apis.naver.com/cafe-web/cafe-mobile/CommentPost.json"
            
            data = {
                'content': content,
                'stickerId': emoji_code,
                'cafeId': cafe_id,
                'requestFrom': 'A',
                'articleId': article_id
            }
            
            response = requests.post(url, headers=self.headers, data=data)
            
            if response.status_code == 200:
                print(f"댓글 등록 성공 - 게시글: {article_id}")
                return response.json().get('commentId')  # 댓글 ID 반환
            else:
                if "많은 댓글" in response.text:
                    print("댓글 연속 등록 실패. 잠시 후 다시 시도합니다.")
                else:
                    print(f"댓글 등록 실패 - 상태 코드: {response.status_code}")
                    print(f"댓글 등록 실패 - 상세 사유: {response.text}")
                return None
                
        except Exception as e:
            print(f"댓글 등록 중 오류 발생: {str(e)}")
            print(traceback.format_exc())
            return None
            
    def write_re_reply(self, cafe_id, article_id, ref_comment_id, content, emoji_code=""):
        """대댓글 작성"""
        try:
            content = content.replace("└", "")
            url = "https://apis.naver.com/cafe-web/cafe-mobile/CommentReply.json"
            
            data = {
                'content': content,
                'stickerId': emoji_code,
                'refCommentId': ref_comment_id,
                'cafeId': cafe_id,
                'articleId': article_id,
                'requestFrom': 'A'
            }
            
            response = requests.post(url, headers=self.headers, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"대댓글 등록 성공 - 댓글ID: {result.get('commentId')}")
                return result
            else:
                if "많은 댓글" in response.text:
                    print("대댓글 연속 등록 실패. 잠시 후 다시 시도합니다.")
                else:
                    print(f"대댓글 등록 실패 - 상태 코드: {response.status_code}")
                    print(f"대댓글 등록 실패 - 상세 사유: {response.text}")
                return None
                
        except Exception as e:
            print(f"대댓글 등록 중 오류 발생: {str(e)}")
            print(traceback.format_exc())
            return None

    def get_comments(self, cafe_id, article_id, page=1, order_by="asc"):
        """댓글 목록 조회"""
        try:
            url = f"https://apis.naver.com/cafe-web/cafe-articleapi/v2/cafes/{cafe_id}/articles/{article_id}/comments/pages/{page}"
            params = {
                'requestFrom': 'A',
                'orderBy': order_by
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            print(f"댓글 목록 조회 중 오류 발생: {str(e)}")
            print(traceback.format_exc())
            return None
            
    def get_emoji_code(self, main_num: int, sub_num: int):
        """이모티콘 코드 조회"""
        try:
            url = "https://apis.naver.com/cafe-web/gfmarket/proxyStickerPackList"
            params = {
                'serviceCode': 'cafe'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                main_idx = main_num - 1
                data = response.json()
                main_code = data['result']['list'][main_idx]
                
                if main_code['stickerCount'] < sub_num:
                    print("없는 이모지 코드입니다.")
                    print(f"사용 가능한 이모지 개수: {main_code['stickerCount']}")
                    print(f"요청한 이모지 번호: {sub_num}")
                    return ""
                    
                emoji_code = main_code['packCode']
                result_code = f"{emoji_code}-{sub_num}-185-160"
                return result_code
                
            return ""
            
        except Exception as e:
            print(f"이모티콘 코드 조회 실패: {str(e)}")
            print(traceback.format_exc())
            return ""
            
    def test_reply(self, cafe_id, article_id):
        """테스트용 댓글 작성"""
        try:
            # 일반 댓글 테스트
            content = "테스트 댓글입니다."
            comment_id = self.write_reply(cafe_id, article_id, content)
            if comment_id:
                print("일반 댓글 작성 성공")
                
                # 대댓글 테스트
                time.sleep(2)  # 잠시 대기
                re_content = "테스트 대댓글입니다."
                result = self.write_re_reply(cafe_id, article_id, comment_id, re_content)
                if result:
                    print("대댓글 작성 성공")
                else:
                    print("대댓글 작성 실패")
            else:
                print("일반 댓글 작성 실패")

            time.sleep(5)
                
            # 이모티콘 댓글 테스트
            emoji_code = self.get_emoji_code(1, 1)  # 첫 번째 팩의 첫 번째 이모티콘
            if emoji_code:
                result = self.write_reply(cafe_id, article_id, "", emoji_code)
                if result:
                    print("이모티콘 댓글 작성 성공")
                else:
                    print("이모티콘 댓글 작성 실패")
                    
            return True
            
        except Exception as e:
            print(f"댓글 테스트 중 오류 발생: {str(e)}")
            return False

if __name__ == "__main__":
    headers = {
        "origin": "https://cafe.naver.com",
        "referer": "https://cafe.naver.com",
        "x-cafe-product": "pc",
        'cookie': "NNB=2QP3YT6BPGMWI; ASID=31a8f9cc0000018978da1f5400000064; ncvid=#vid#_115.138.87.199IWS1; ba.uuid=a76ad3c1-5903-42bd-8399-3eb89840598c; tooltipDisplayed=true; _ga_6Z6DP60WFK=GS1.2.1726462403.1.0.1726462403.60.0.0; NFS=2; _ga=GA1.1.877073880.1704979036; _ga_EFBDNNF91G=GS1.1.1732339996.1.0.1732339999.0.0.0; _ga_8P4PY65YZ2=GS1.1.1734265772.1.1.1734265776.56.0.0; nstore_session=uajHtGrn2P2hNissMDvcn+a3; nstore_pagesession=iI4S7lqW4vuF/ssL/6s-089597; NAC=bt7NBgQZgVqM; NACT=1; page_uid=iJJSAwqo1SossuojL40ssssssF8-021740; SRT30=1740567125; nid_inf=2003783109; NID_AUT=qj+qPx84ta92bm6V511C6YmeDGE4RZ8MwAgTAu4wVsZPt2kmZDzjbG7eyXzlgr/2; NID_SES=AAABlAoRgZZrYS7P3xtIUFncKWq5TTGEvDsqA6CvvRSZGBjgCvZaTXwsMBeUzYQr7jXtkCNxoX2SWfHx0QWEezLjVzYZQixpaBbUUFHSGu/Fj9OuMId5s8jPu4GUoOU9t7afm2/HEuaJDy7KfItKB9STaubry8xDBxhd6bar+pqL8ScJIIQen/JTbnMegzmGbRYK64/8TWhgUVW/uIqhbpPXqUXqiI7uYl0XcG5PbKj1/nnzNn0qywpOkpZyZiGhOYYxueHANkeI83Jw9ehsAMh8JC7q+3v86nJWv6TgdQ1356PBIKIB+S8sKcPIuE+xYK1o3sjiPvuv5U2eq0fRfNPuGBp8Qx/D0PYMfBZxhQr3aynGyzIuG23N7EdTePGoVYZrkuJvWw44QMIUIAzmPldDwC9p32gqrsJVMfKFjZuVVCjwB9hufq07JFZUaQYL+hU+s9ym/mTjM1bPnylEV98GKQSVpMOzgByHibzn8i3uHA28SG5bVUDL+kTvfrqstl7AIOE7YSm2xfMA2V02CKuzd5J2iHh7A9V9995e3rJZKZjD; NID_JKL=2Hct8b3FYkWCptGEFOX+TtlN4+l28Acdba7WGmyyNJo=; ncu=8bb05b2d3f7a1fdefb3d7a7b80681e2cd8; ncvc2=1d26cdbba9ec892411f690a196780b7ac7886b97c99475a15095af0bbcb97c855eb066fe3b0893a0c95707db60cf44bd7d46707f9eaec1e1de1abb15dbcc51a1dcd3dc82848a839d8d8e8f898a8a9f958d9f809f939b9890a2a2a209; nci4=0e39ddf6e6a7c27129c780979a650a60d8957b88dd984f9c46a4a9bb492ece01cd5b933efdbd44021bea9be157d572ba71597e30dbed88d2ee0d8d6190ae1bfdb283cebfb691b485bab5b89fbf8cdca9a58da899d1a1ac8b92a3ef9894b398ae9f9382a580b1faf9f8fff5f3f2f682f2d6f1c785ea878782ec819cf18299f0; ncmc4=6651b59e8ecfaa1941afe8fff2007401fead5cb492c80ff438dbff27b8bd6e8056b844a5512abb97980a7f870fa960d042294b13b7c0e486fb71930b8efa7db3fcdbe8d9d0dffadde2ad89; JSESSIONID=7DF7A6421AD62E8ACB139997EE3564A5; BUC=u_uw_21-vuVCc22qt_EwX-i2ErlG15POQ5APoVbRwz0=",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }
    
    reply_api = ReplyAPI(headers)
    reply_api.test_reply("31203823", "373")

