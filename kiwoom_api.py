import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop, pyqtSignal, QObject

class KiwoomAPI(QObject):
    # 로그인 상태 변경 시그널
    login_status_changed = pyqtSignal(bool, str)  # (성공여부, 메시지)
    
    def __init__(self):
        super().__init__()
        print("키움 OpenAPI 초기화 중...")
        
        try:
            self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
            print("✅ 키움 OpenAPI 연결 성공")
        except Exception as e:
            print(f"❌ 키움 OpenAPI 연결 실패: {e}")
            self.ocx = None
            return
        
        # 이벤트 연결
        self.ocx.OnEventConnect.connect(self._event_connect)
        
        # 로그인 상태
        self.connected = False
        self.login_event_loop = None
        self.account_list = []
        self.server_type = ""
        
    def login(self):
        """키움증권 로그인"""
        if not self.ocx:
            print("❌ 키움 OpenAPI가 초기화되지 않았습니다.")
            self.login_status_changed.emit(False, "API 초기화 실패")
            return False
            
        print("🔐 키움증권 로그인 시도 중...")
        self.login_event_loop = QEventLoop()
        
        try:
            self.ocx.dynamicCall("CommConnect()")
            self.login_event_loop.exec_()
            return self.connected
        except Exception as e:
            print(f"❌ 로그인 오류: {e}")
            self.login_status_changed.emit(False, f"로그인 오류: {e}")
            return False
        
    def _event_connect(self, err_code):
        """로그인 이벤트 처리"""
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
            except:
                self.server_type = "알 수 없음"
            
            # 사용자 정보
            try:
                user_id = self.ocx.dynamicCall("GetLoginInfo(QString)", "USER_ID")
                user_name = self.ocx.dynamicCall("GetLoginInfo(QString)", "USER_NAME")
                print(f"👤 사용자: {user_name} ({user_id})")
            except:
                pass
                
            self.login_status_changed.emit(True, f"{self.server_type} 로그인 성공")
            
        else:
            error_messages = {
                -100: "사용자 정보교환 실패",
                -101: "서버접속 실패", 
                -102: "버전처리 실패",
                -103: "개인방화벽 설정 오류",
                -104: "메모리 보호 실패",
                -105: "함수입력값 오류",
                -106: "통신연결 종료",
                -107: "보안모듈 오류",
                -108: "공인인증 로그인 필요"
            }
            
            error_msg = error_messages.get(err_code, f"알 수 없는 오류 ({err_code})")
            print(f"❌ 로그인 실패: {error_msg}")
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