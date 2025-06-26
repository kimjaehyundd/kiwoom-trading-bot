import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, QObject, QEventLoop, QTimer
import time
import subprocess

class KiwoomAPI(QObject):
    # 로그인 상태 변경 시그널
    login_status_changed = pyqtSignal(bool, str)  # (성공여부, 메시지)
    login_window_status = pyqtSignal(str)  # 로그인창 상태
    
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
            return False
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 키움 OpenAPI 연결 실패: {error_msg}")
            return False
    
    def kill_existing_processes(self):
        """기존 키움 프로세스 종료"""
        processes = [
            "opstarter.exe",
            "opsystem.exe", 
            "opw.exe",
            "versioning.exe",
            "KHOpenAPI.exe"
        ]
        
        killed_any = False
        for process_name in processes:
            try:
                result = subprocess.run(
                    ["taskkill", "/F", "/IM", process_name],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"🔄 {process_name} 프로세스 종료")
                    killed_any = True
            except:
                pass
        
        if killed_any:
            print("⏳ 프로세스 정리 완료, 3초 대기...")
            time.sleep(3)
            
        return killed_any
    
    def bring_window_to_front(self):
        """키움 로그인창을 화면 앞으로 가져오기"""
        try:
            import win32gui
            import win32con
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if "키움" in window_title or "OpenAPI" in window_title or "로그인" in window_title:
                        windows.append((hwnd, window_title))
                        
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            for hwnd, title in windows:
                print(f"🔍 발견된 키움 창: {title}")
                # 창을 앞으로 가져오기
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                win32gui.SetActiveWindow(hwnd)
                self.login_window_status.emit(f"로그인창 활성화: {title}")
                return True
                
        except ImportError:
            print("⚠️ win32gui 모듈이 없습니다. pip install pywin32")
        except Exception as e:
            print(f"창 활성화 오류: {e}")
            
        return False
    
    def login(self):
        """키움증권 로그인"""
        if not self.ocx:
            print("❌ 키움 OpenAPI가 초기화되지 않았습니다.")
            self.login_status_changed.emit(False, "API 초기화 실패")
            return False
            
        print("🔐 키움증권 로그인 시도 중...")
        
        # 1. 기존 프로세스 정리
        print("🔄 기존 키움 프로세스 정리 중...")
        self.kill_existing_processes()
        
        # 2. 자동 로그인 해제
        self.disable_auto_login()
        
        try:
            from PyQt5.QtCore import QEventLoop
            self.login_event_loop = QEventLoop()
            
            print("⏳ 키움증권 로그인 창 실행 중...")
            self.login_window_status.emit("로그인창 실행 중...")
            
            # 3. 로그인 시도
            self.ocx.dynamicCall("CommConnect()")
            
            # 4. 잠시 대기 후 창 찾기
            QTimer.singleShot(2000, self.find_login_window)
            
            print("📌 로그인 창이 나타나면:")
            print("   1. '모의투자 접속' 체크")
            print("   2. 아이디/비밀번호 입력")
            print("   3. 로그인 버튼 클릭")
            
            self.login_event_loop.exec_()
            return self.connected
            
        except Exception as e:
            print(f"❌ 로그인 오류: {e}")
            self.login_status_changed.emit(False, f"로그인 오류: {e}")
            return False
    
    def find_login_window(self):
        """로그인창 찾기 및 활성화"""
        print("🔍 로그인창 검색 중...")
        
        if self.bring_window_to_front():
            print("✅ 키움 로그인창을 화면으로 가져왔습니다.")
            self.login_window_status.emit("로그인창 활성화됨")
        else:
            print("⚠️ 로그인창을 찾을 수 없습니다.")
            print("💡 다음 사항을 확인해주세요:")
            print("   1. 작업표시줄에 키움 아이콘이 있는지 확인")
            print("   2. Alt+Tab으로 숨겨진 창이 있는지 확인")
            print("   3. 바탕화면에 로그인창이 최소화되어 있는지 확인")
            
            self.login_window_status.emit("로그인창을 찾을 수 없음 - 수동으로 확인 필요")
            
            # 추가 대기 시간
            QTimer.singleShot(5000, self.check_login_timeout)
    
    def check_login_timeout(self):
        """로그인 시간 초과 체크"""
        if not self.connected:
            print("⏰ 로그인 대기 시간 초과")
            print("💡 로그인창이 보이지 않는다면:")
            print("   1. KOA Studio에서 먼저 로그인 테스트")
            print("   2. 키움증권 HTS에서 정상 로그인 확인")
            print("   3. 프로그램을 관리자 권한으로 실행")
            
            self.login_window_status.emit("로그인 시간 초과 - 수동 확인 필요")
    
    def disable_auto_login(self):
        """자동 로그인 해제"""
        if not self.ocx:
            return False
            
        try:
            print("🔧 자동 로그인 해제 시도...")
            result = self.ocx.dynamicCall("KOA_Functions(QString, QString)", "DisableAutoLogin", "")
            print(f"   결과: {result}")
            return True
        except Exception as e:
            print(f"   자동 로그인 해제 실패: {e}")
            return False
    
    def show_account_window(self):
        """계좌 비밀번호 설정창 표시"""
        if not self.ocx:
            return False
            
        try:
            print("💼 계좌 설정창 표시...")
            self.ocx.dynamicCall("KOA_Functions(QString, QString)", "ShowAccountWindow", "")
            return True
        except Exception as e:
            print(f"계좌 설정창 표시 실패: {e}")
            return False
    
    def _event_connect(self, err_code):
        """로그인 이벤트 처리"""
        if err_code == 0:
            print("✅ 키움증권 로그인 성공!")
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
            print(f"❌ 로그인 실패: {error_msg} (코드: {err_code})")
            
            if err_code == -101:
                print("\n📋 서버접속 실패 해결방법:")
                print("1. 인터넷 연결 상태 확인")
                print("2. 방화벽/백신 프로그램 확인")
                print("3. 키움증권 서버 점검 시간 확인")
                
            elif err_code == -102:
                print("\n📋 버전처리 실패 해결방법:")
                print("1. 모든 키움 관련 프로그램 종료")
                print("2. 버전처리 창에서 '닫기' 클릭")
                print("3. 업데이트 완료 후 재실행")
                
            elif err_code == -108:
                print("\n📋 공인인증 관련:")
                print("1. 공인인증서 정상 설치 확인")
                print("2. 키움증권 HTS에서 로그인 테스트")
                
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