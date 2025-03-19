import random
import os

def generate_nicknames(count=1000):
    """닉네임을 생성하고 파일에 저장하는 함수"""
    # 닉네임 생성에 사용할 요소들
    prefixes = [
        '귀여운', '행복한', '즐거운', '따뜻한', '달콤한', '상큼한', '깜찍한', '사랑스러운', '멋진', '예쁜',
        '착한', '똑똑한', '든든한', '반짝이는', '싱그러운', '활기찬', '기분좋은', '포근한', '새침한', '앙큼한',
        '귀염둥이', '아기자기', '사랑둥이', '반반한', '알콩달콩', '아름다운', '화사한', '은은한', '산뜻한', '푸릇한'
    ]

    words = [
        '고양이', '강아지', '토끼', '판다', '여우', '곰돌이', '햄스터', '코알라', '펭귄', '기린',
        '다람쥐', '물범', '사슴', '알파카', '양', '치타', '캥거루', '쿼카', '하마', '호랑이',
        '늑대', '부엉이', '비버', '앵무새', '친칠라', '카피바라', '포메', '푸들', '햄찌'
    ]

    suffixes = [
        '님', '쓰', '양', '군', '공주', '왕자', '킹', '퀸', '짱', '맘',
        '달링', '씨', '하트', '러브', '몽', '찡', '띠', '뿡', '냥', '멍',
        '이', '에요', '랄라', '뿅', '방방', '콩콩', '데렐레', '방울', '초코', '밍밍'
    ]

    # 닉네임 생성
    nicknames = set()  # 중복 방지를 위해 set 사용
    while len(nicknames) < count:
        prefix = random.choice(prefixes)
        word = random.choice(words)
        suffix = random.choice(suffixes)
        nickname = f"{prefix}{word}{suffix}"
        nicknames.add(nickname)

    # 디렉토리 확인 및 생성
    directory = os.path.dirname('nickname.txt')
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # nickname.txt 파일에 저장
    with open('nickname.txt', 'w', encoding='utf-8') as f:
        for nickname in nicknames:
            f.write(nickname + '\n')
            
    return list(nicknames) 