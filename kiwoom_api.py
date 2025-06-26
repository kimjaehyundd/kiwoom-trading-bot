import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, QObject, QEventLoop
import time

class KiwoomAPI(QObject):
    # 로그인 상태 변경 시그널
    login_status_changed = pyqtSignal(bool, str)  # (성공여부, 메시지)
    
    def __init__(self):
        super().__init__()
        print("키움 OpenAPI 초기화 중...")
        
        self.ocx = None
        self.connected = False
        self.account_list = []
        self.server_type = ""
        self.login_event_loop = None
        
        # QAxWidget 연결 시도
        self._init_ocx()
        
    def _init_ocx(self):
        """키움 OpenAPI 초기화 시도"""
        try:
            from PyQt5.QAxContainer import QAxWidget
            
            self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
            
            # 이벤트 연결
            self.ocx.OnEventConnect.connect(self._event_connect)
            
            print("✅ 키움 OpenAPI 연결 성공")
            return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 키움 OpenAPI 연결 실패: {error_msg}")
            
            if "could not be instantiated" in error_msg:
                print("\n📋 해결 방법:")
                print("1. 키움증권 홈페이지에서 OpenAPI 사용 신청")
                print("2. 모의투자 신청")
                print("3. KOA Studio가 실행중이면 종료")
                print("4. 관리자 권한으로 프로그램 실행")
                
            return False
    
    def login(self):
        """키움증권 로그인"""
        if not self.ocx:
            print("❌ 키움 OpenAPI가 초기화되지 않았습니다.")
            self.login_status_changed.emit(False, "API 초기화 실패")
            return False
        
        print("🔐 키움증권 로그인 시도 중...")
        print("⚠️  중요: KOA Studio나 다른 키움 프로그램을 모두 종료해주세요!")
        print("📌 로그인 창에서 '모의투자 접속'을 체크하고 로그인하세요!")
        
        try:
            self.login_event_loop = QEventLoop()
            
            # 로그인 시도
            result = self.ocx.dynamicCall("CommConnect()")
            print(f"CommConnect 호출 결과: {result}")
            
            if result == 0:
                print("✅ 로그인 요청 성공 - 로그인 창 대기 중...")
                print("⏳ 키움 로그인 창이 나타날 때까지 기다려주세요...")
                self.login_event_loop.exec_()
            else:
                print(f"❌ 로그인 요청 실패: {result}")
                self.login_status_changed.emit(False, f"로그인 요청 실패: {result}")
                
            return self.connected
            
        except Exception as e:
            print(f"❌ 로그인 오류: {e}")
            self.login_status_changed.emit(False, f"로그인 오류: {e}")
            return False
    
    def _event_connect(self, err_code):
        """로그인 이벤트 처리"""
        print(f"🔔 로그인 이벤트 수신: 오류코드 {err_code}")
        
        if err_code == 0:
            print("✅ 로그인 성공!")
            self.connected = True
            
            # 계좌 목록 가져오기
            self.account_list = self._get_account_list()
            print(f"📊 계좌 목록: {self.account_list}")
            
            # 서버 구분 (실계좌/모의투자)
            try:
                server_gubun = self.ocx.dynamicCall("GetLoginInfo(QString)", "GetServerGubun")
                self.server_type = "모의투자" if server_gubun == "1" else "실계좌"
                print(f"🏦 서버 타입: {self.server_type}")
                
                if self.server_type == "모의투자":
                    print("🎯 모의투자 서버에 성공적으로 연결되었습니다!")
                else:
                    print("⚠️  실계좌 서버에 연결되었습니다. 주의하세요!")
                    
            except Exception as e:
                print(f"서버 타입 확인 오류: {e}")
                self.server_type = "알 수 없음"
            
            # 사용자 정보
            try:
                user_id = self.ocx.dynamicCall("GetLoginInfo(QString)", "USER_ID")
                user_name = self.ocx.dynamicCall("GetLoginInfo(QString)", "USER_NAME")
                print(f"👤 사용자: {user_name} ({user_id})")
            except Exception as e:
                print(f"사용자 정보 조회 오류: {e}")
                
            self.login_status_changed.emit(True, f"{self.server_type} 로그인 성공")
            
        else:
            error_messages = {
                -100: "사용자 정보교환 실패",
                -101: "서버접속 실패 (OpenAPI 신청 확인)", 
                -102: "버전처리 실패",
                -103: "개인방화벽 설정 오류",
                -104: "메모리 보호 실패",
                -105: "함수입력값 오류",
                -106: "통신연결 종료 (중복로그인)",
                -107: "보안모듈 오류",
                -108: "공인인증 로그인 필요"
            }
            
            error_msg = error_messages.get(err_code, f"알 수 없는 오류 ({err_code})")
            print(f"❌ 로그인 실패: {error_msg}")
            
            if err_code == -101:
                print("🔧 해결방법: 키움 홈페이지에서 OpenAPI 사용 신청 확인")
            elif err_code == -106:
                print("🔧 해결방법: 다른 키움 프로그램(KOA Studio 등) 모두 종료")
            elif err_code == -108:
                print("🔧 해결방법: 공인인증서 설치 및 키움 HTS 로그인 확인")
                
            self.connected = False
            self.login_status_changed.emit(False, f"로그인 실패: {error_msg}")
            
        if self.login_event_loop:
            self.login_event_loop.exit()
            
    def _get_account_list(self):
        """계좌 목록 조회"""
        if not self.connected or not self.ocx:
            return []
            
        try:
            account_list = self.ocx.dynamicCall("GetLoginInfo(QString)", "ACCNO")
            accounts = account_list.split(';')[:-1]  # 마지막 빈 문자열 제거
            return accounts
        except Exception as e:
            print(f"계좌 목록 조회 오류: {e}")
            return []
            
    def logout(self):
        """로그아웃"""
        if self.ocx and self.connected:
            try:
                self.ocx.dynamicCall("CommTerminate()")
                self.connected = False
                print("🚪 로그아웃 완료")
                self.login_status_changed.emit(False, "로그아웃")
            except Exception as e:
                print(f"로그아웃 오류: {e}")
                
    def is_connected(self):
        """연결 상태 확인"""
        return self.connected
        
    def get_account_list(self):
        """계좌 목록 반환"""
        return self.account_list
        
    def get_server_type(self):
        """서버 타입 반환 (실계좌/모의투자)"""
        return self.server_type