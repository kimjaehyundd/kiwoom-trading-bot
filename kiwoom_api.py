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
        
        # QAxWidget 연결 시도
        self._init_ocx()
        
    def _init_ocx(self):
        """키움 OpenAPI 초기화 시도"""
        try:
            from PyQt5.QAxContainer import QAxWidget
            from PyQt5.QtCore import QEventLoop
            
            self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
            self.login_event_loop = None
            
            # 이벤트 연결
            self.ocx.OnEventConnect.connect(self._event_connect)
            
            print("✅ 키움 OpenAPI 연결 성공")
            return True
            
        except ImportError as e:
            print(f"❌ PyQt5.QAxContainer 모듈 오류: {e}")
            print("해결방법: pip install PyQt5 재설치 필요")
            return False
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 키움 OpenAPI 연결 실패: {error_msg}")
            
            if "could not be instantiated" in error_msg:
                print("\n📋 필수 확인사항:")
                print("1. 키움증권 계좌 개설 여부")
                print("2. 키움 홈페이지에서 OpenAPI 사용 신청 여부") 
                print("3. 신청 승인 완료 여부 (1-2일 소요)")
                print("4. KOA Studio 설치 여부")
                print("5. 모의투자 신청 여부")
                print("\n📋 해결 방법:")
                print("1. 키움증권 홈페이지 로그인")
                print("2. 고객서비스 > 다운로드 > Open API")
                print("3. '서비스 사용 등록/해지' 탭에서 사용등록")
                print("4. 모의투자 > 상시모의투자 신청")
                
            elif "OnEventConnect" in error_msg:
                print("\n📋 해결 방법:")
                print("1. 키움증권 계좌 개설 확인")
                print("2. OpenAPI 사용 신청 확인")
                print("3. KOA Studio에서 API 등록 확인")
                
            return False
    
    def disable_auto_login(self):
        """자동 로그인 해제 - 로그인창이 보이도록"""
        if not self.ocx:
            print("❌ 키움 OpenAPI가 초기화되지 않았습니다.")
            return False
            
        try:
            print("🔧 자동 로그인 해제 중...")
            # 자동 로그인 해제
            result = self.ocx.dynamicCall("KOA_Functions(QString, QString)", "DisableAutoLogin", "")
            print(f"자동 로그인 해제 결과: {result}")
            return True
        except Exception as e:
            print(f"자동 로그인 해제 실패: {e}")
            return False
    
    def show_account_window(self):
        """계좌 비밀번호 설정창 표시"""
        if not self.ocx:
            return False
            
        try:
            print("💼 계좌 설정창 표시 중...")
            self.ocx.dynamicCall("KOA_Functions(QString, QString)", "ShowAccountWindow", "")
            return True
        except Exception as e:
            print(f"계좌 설정창 표시 실패: {e}")
            return False
    
    def login(self):
        """키움증권 로그인"""
        if not self.ocx:
            print("❌ 키움 OpenAPI가 초기화되지 않았습니다.")
            self.login_status_changed.emit(False, "API 초기화 실패")
            return False
            
        print("🔐 키움증권 로그인 시도 중...")
        
        # 자동 로그인 해제 (로그인창이 보이도록)
        self.disable_auto_login()
        
        try:
            from PyQt5.QtCore import QEventLoop
            self.login_event_loop = QEventLoop()
            
            print("⏳ 키움증권 로그인 창이 나타날 때까지 잠시 기다려주세요...")
            print("📌 로그인 창에서 '모의투자 접속'을 체크하고 로그인하세요")
            
            # 로그인 시도
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
            print("✅ 실제 로그인 성공!")
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
            
            if err_code == -101:
                print("\n📋 서버접속 실패 해결방법:")
                print("1. 키움증권 OpenAPI 사용 신청이 승인되었는지 확인")
                print("2. 모의투자 신청이 되어 있는지 확인")
                print("3. 인터넷 연결 상태 확인")
                print("4. 방화벽 설정 확인")
                
            elif err_code == -108:
                print("\n📋 공인인증 관련:")
                print("1. 공인인증서가 설치되어 있는지 확인")
                print("2. 키움증권 HTS에서 정상 로그인되는지 확인")
                
            self.connected = False
            self.login_status_changed.emit(False, f"로그인 실패: {error_msg}")
            
        if hasattr(self, 'login_event_loop') and self.login_event_loop:
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
        
    def get_connection_status(self):
        """연결 상태 상세 정보"""
        if self.ocx and self.connected:
            return "실제 API 연결됨"
        elif self.connected:
            return "테스트 모드 실행 중"
        else:
            return "연결되지 않음"