import subprocess
import time
import re

def toggle_usb_tethering(enable):
    # USB 테더링을 켜거나 끄는 명령어
    command = "adb shell svc usb setFunctions rndis" if enable else "adb shell svc usb setFunctions none"
    subprocess.run(command, shell=True)
    
    # 테더링 상태 확인을 위해 잠시 대기
    time.sleep(1)
    
    # 테더링 상태 확인
    return is_tethering_enabled()

def toggle_mobile_data(enable):
    # 모바일 데이터를 켜거나 끄는 명령어
    command = f"adb shell svc data {'enable' if enable else 'disable'}"
    subprocess.run(command, shell=True)

def get_current_ip():
    """현재 IP 주소를 조회하는 함수"""
    try:
        # 외부 IP 조회 서비스 사용
        response = subprocess.check_output("curl -s https://api.ipify.org", shell=True)
        ip = response.decode('utf-8').strip()
        return ip
    except Exception as e:
        print(f"IP 조회 중 오류 발생: {str(e)}")
        return "알 수 없음"

def is_tethering_enabled():
    """USB 테더링이 활성화되어 있는지 확인합니다.
    
    Returns:
        bool: 테더링이 활성화되어 있으면 True, 아니면 False
    """
    try:
        # USB 함수 상태 확인
        result = subprocess.run("adb shell getprop sys.usb.state", shell=True, capture_output=True, text=True)
        output = result.stdout.strip()
        
        # 'rndis'가 포함되어 있으면 테더링이 활성화된 상태
        if 'rndis' in output:
            return True
            
        # 네트워크 인터페이스 확인 (추가 검증)
        result = subprocess.run("adb shell ip addr show", shell=True, capture_output=True, text=True)
        output = result.stdout.strip()
        
        # rndis 인터페이스가 있고 UP 상태인지 확인
        if re.search(r'rndis.*state UP', output):
            return True
            
        return False
    except Exception as e:
        print(f"테더링 상태 확인 중 오류 발생: {str(e)}")
        return False

def change_ip():
    print("IP 변경을 시작합니다...")
    
    # 테더링 상태 확인
    if not is_tethering_enabled():
        print("테더링이 활성화되어 있지 않습니다. 활성화를 시도합니다.")
        tethering_enabled = toggle_usb_tethering(True)
        if not tethering_enabled:
            print("테더링 활성화에 실패했습니다.")
            return False, "Unknown", "Unknown"
        print("테더링이 활성화되었습니다.")
    
    # 현재 IP 확인
    old_ip = get_current_ip()
    print(f"현재 IP: {old_ip}")
    
    # 1. 모바일 데이터 끄기
    toggle_mobile_data(False)
    time.sleep(1)
    
    # 2. 모바일 데이터 켜기
    toggle_mobile_data(True)
    time.sleep(3)  # IP 변경에 시간이 필요할 수 있음
    
    # 변경된 IP 확인
    new_ip = get_current_ip()
    print(f"변경된 IP: {new_ip}")
    
    print("IP 변경이 완료되었습니다.")
    
    # IP 변경 여부 반환
    return old_ip != new_ip, old_ip, new_ip

if __name__ == "__main__":
    print(change_ip())

