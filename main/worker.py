from PyQt5.QtCore import QThread

# 작업관리에서 작업 리스트를 가져오고 작업에 맞는 설정값들은 스케줄러를 만들고 별도로 관리한다.

class Worker(QThread):
    
    def __init__(self):
        super().__init__()
        pass

    def run(self):
        pass