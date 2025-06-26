import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt5.QtCore import Qt, QTimer
from kiwoom_api import KiwoomAPI

def main():
    """1단계: 로그인 테스트 프로그램"""
    print("=" * 50)
    print("키움증권 자동매매 프로그램 - 1단계 (로그인 테스트)")
    print("=" * 50)
    
    # PyQt5 애플리케이션 생성
    app = QApplication(sys.argv)
    
    # 키움 API 초기화
    kiwoom = KiwoomAPI()
    
    if not kiwoom.ocx:
        print("❌ 키움 OpenAPI 초기화 실패")
        print("\n해결 방법:")
        print("1. 키움증권 KOA Studio가 설치되어 있는지 확인")
        print("2. 관리자 권한으로 실행해보기")
        print("3. 키움증권 OpenAPI가 정상 등록되어 있는지 확인")
        input("Enter 키를 눌러 종료...")
        return
    
    print("\n✅ 키움 OpenAPI 초기화 성공!")
    print("🔐 로그인을 시도합니다...")
    print("※ 키움증권 로그인 창이 나타나면 로그인해주세요")
    
    def on_login_status_changed(success, message):
        """로그인 상태 변경 콜백"""
        if success:
            print(f"✅ {message}")
            print(f"📊 계좌 목록: {kiwoom.get_account_list()}")
            print(f"🏦 서버 타입: {kiwoom.get_server_type()}")
            print("\n" + "=" * 50)
            print("1단계 테스트 완료! 로그인이 성공적으로 되었습니다.")
            print("다음 단계에서는 계좌정보 조회 기능을 추가할 예정입니다.")
            print("=" * 50)
        else:
            print(f"❌ {message}")
            print("\n문제 해결:")
            print("1. 키움증권 계좌가 있는지 확인")
            print("2. OpenAPI 신청이 되어 있는지 확인")
            print("3. 키움증권 HTS에서 정상 로그인되는지 확인")
    
    # 로그인 상태 변경 이벤트 연결
    kiwoom.login_status_changed.connect(on_login_status_changed)
    
    # 로그인 시도
    try:
        login_result = kiwoom.login()
        
        # 잠시 대기 (로그인 처리 완료까지)
        QTimer.singleShot(5000, app.quit)  # 5초 후 자동 종료
        
        # 애플리케이션 실행
        app.exec_()
        
    except Exception as e:
        print(f"❌ 프로그램 실행 오류: {e}")
        print("\n오류 해결 방법:")
        print("1. 가상환경이 활성화되어 있는지 확인")
        print("2. 필요한 패키지가 설치되어 있는지 확인")
        print("3. 키움증권 관련 프로그램이 실행중이 아닌지 확인")
        
    finally:
        # 로그아웃
        if kiwoom.is_connected():
            kiwoom.logout()
        
        print("\n프로그램을 종료합니다.")

if __name__ == "__main__":
    main()