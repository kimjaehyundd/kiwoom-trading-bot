import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QTextEdit, QLineEdit,
                           QMessageBox, QGroupBox, QGridLayout, QCheckBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QFont
from kiwoom_api import KiwoomAPI
import os

class TradingDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.kiwoom = None
        self.init_ui()
        self.check_prerequisites()
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("키움증권 자동매매 대시보드")
        self.setGeometry(100, 100, 900, 700)
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)
        
        # 타이틀
        title_label = QLabel("키움증권 자동매매 프로그램")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # 사전 체크 그룹
        self.create_prerequisite_group(main_layout)
        
        # 연결 상태 그룹
        self.create_connection_group(main_layout)
        
        # 로그 그룹
        self.create_log_group(main_layout)
        
        # 제어 버튼 그룹
        self.create_control_group(main_layout)
        
    def create_prerequisite_group(self, parent_layout):
        """사전 요구사항 체크 그룹"""
        group = QGroupBox("📋 사전 요구사항 체크")
        layout = QVBoxLayout(group)
        
        # 체크리스트
        self.checks = {}
        
        checklist = [
            ("koa_studio", "KOA Studio 설치됨"),
            ("openapi_reg", "키움 OpenAPI 사용 신청 완료"),
            ("mock_trading", "모의투자 신청 완료"),
            ("account", "키움증권 계좌 보유")
        ]
        
        for key, text in checklist:
            checkbox = QCheckBox(text)
            self.checks[key] = checkbox
            layout.addWidget(checkbox)
        
        # 체크 버튼
        check_button = QPushButton("환경 체크")
        check_button.clicked.connect(self.check_prerequisites)
        layout.addWidget(check_button)
        
        parent_layout.addWidget(group)
        
    def create_connection_group(self, parent_layout):
        """연결 상태 그룹 생성"""
        group = QGroupBox("🔗 연결 상태")
        layout = QGridLayout(group)
        
        # API 상태
        layout.addWidget(QLabel("API 상태:"), 0, 0)
        self.api_status_label = QLabel("확인 중...")
        self.api_status_label.setStyleSheet("color: orange")
        layout.addWidget(self.api_status_label, 0, 1)
        
        # 로그인 상태
        layout.addWidget(QLabel("로그인 상태:"), 1, 0)
        self.login_status_label = QLabel("로그인 안됨")
        self.login_status_label.setStyleSheet("color: red")
        layout.addWidget(self.login_status_label, 1, 1)
        
        # 서버 타입
        layout.addWidget(QLabel("서버 타입:"), 2, 0)
        self.server_type_label = QLabel("-")
        layout.addWidget(self.server_type_label, 2, 1)
        
        # 계좌 정보
        layout.addWidget(QLabel("계좌 목록:"), 3, 0)
        self.account_label = QLabel("-")
        layout.addWidget(self.account_label, 3, 1)
        
        parent_layout.addWidget(group)
        
    def create_log_group(self, parent_layout):
        """로그 그룹 생성"""
        group = QGroupBox("📄 로그")
        layout = QVBoxLayout(group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        parent_layout.addWidget(group)
        
    def create_control_group(self, parent_layout):
        """제어 버튼 그룹 생성"""
        group = QGroupBox("🎮 제어")
        layout = QHBoxLayout(group)
        
        self.login_button = QPushButton("키움 로그인")
        self.login_button.clicked.connect(self.on_login_clicked)
        self.login_button.setEnabled(False)
        layout.addWidget(self.login_button)
        
        self.logout_button = QPushButton("로그아웃")
        self.logout_button.clicked.connect(self.on_logout_clicked)
        self.logout_button.setEnabled(False)
        layout.addWidget(self.logout_button)
        
        self.koa_button = QPushButton("KOA Studio 실행")
        self.koa_button.clicked.connect(self.run_koa_studio)
        layout.addWidget(self.koa_button)
        
        self.manual_button = QPushButton("수동 로그인 가이드")
        self.manual_button.clicked.connect(self.show_manual_guide)
        layout.addWidget(self.manual_button)
        
        parent_layout.addWidget(group)
        
    def check_prerequisites(self):
        """사전 요구사항 체크"""
        self.log("🔍 환경 체크 시작...")
        
        # KOA Studio 체크
        koa_paths = [
            "C:\\OpenAPI\\KOAStudioSA.exe",
            "C:\\OpenApi\\KOAStudioSA.exe",
            "C:\\Program Files\\Kiwoom\\KOAStudio\\KOAStudioSA.exe",
            "C:\\Program Files (x86)\\Kiwoom\\KOAStudio\\KOAStudioSA.exe"
        ]
        
        koa_found = False
        for path in koa_paths:
            if os.path.exists(path):
                koa_found = True
                self.log(f"✅ KOA Studio 발견: {path}")
                break
                
        self.checks["koa_studio"].setChecked(koa_found)
        
        if not koa_found:
            self.log("❌ KOA Studio가 설치되지 않았습니다.")
            self.log("📌 키움증권 홈페이지에서 KOA Studio를 다운로드하세요.")
        
        # API 초기화 시도
        self.init_kiwoom()
        
    def init_kiwoom(self):
        """키움 API 초기화"""
        self.log("🔌 키움 OpenAPI 초기화 시도...")
        
        try:
            self.kiwoom = KiwoomAPI()
            self.kiwoom.login_status_changed.connect(self.on_login_status_changed)
            
            if self.kiwoom.ocx:
                self.api_status_label.setText("API 연결됨")
                self.api_status_label.setStyleSheet("color: green")
                self.log("✅ 키움 OpenAPI 연결 성공")
                self.login_button.setEnabled(True)
                
                # 추가 체크
                self.checks["openapi_reg"].setChecked(True)
                self.log("✅ OpenAPI 사용 등록이 완료되어 있습니다.")
                
            else:
                self.api_status_label.setText("API 연결 실패")
                self.api_status_label.setStyleSheet("color: red")
                self.log("❌ 키움 OpenAPI 연결 실패")
                self.show_setup_guide()
                
        except Exception as e:
            self.api_status_label.setText("API 초기화 오류")
            self.api_status_label.setStyleSheet("color: red")
            self.log(f"❌ API 초기화 오류: {e}")
            self.show_setup_guide()
            
    def show_setup_guide(self):
        """설정 가이드 표시"""
        self.log("\n📋 키움 OpenAPI 설정 가이드:")
        self.log("1. 키움증권 홈페이지 로그인")
        self.log("2. 고객서비스 > 다운로드 > Open API")
        self.log("3. 'Open API+ 사용 등록/해지' 클릭")
        self.log("4. 사용 등록 신청")
        self.log("5. 모의투자 > 상시모의투자 신청")
        self.log("6. 승인 완료 후 프로그램 재실행")
        
    def run_koa_studio(self):
        """KOA Studio 실행"""
        koa_paths = [
            "C:\\OpenAPI\\KOAStudioSA.exe",
            "C:\\OpenApi\\KOAStudioSA.exe",
            "C:\\Program Files\\Kiwoom\\KOAStudio\\KOAStudioSA.exe",
            "C:\\Program Files (x86)\\Kiwoom\\KOAStudio\\KOAStudioSA.exe"
        ]
        
        for path in koa_paths:
            if os.path.exists(path):
                try:
                    os.startfile(path)
                    self.log(f"🚀 KOA Studio 실행: {path}")
                    self.log("📌 KOA Studio에서 먼저 로그인을 테스트해보세요.")
                    return
                except Exception as e:
                    self.log(f"❌ KOA Studio 실행 실패: {e}")
                    
        self.log("❌ KOA Studio를 찾을 수 없습니다.")
        self.log("📌 키움증권 홈페이지에서 KOA Studio를 다운로드하세요.")
        
    def show_manual_guide(self):
        """수동 로그인 가이드"""
        guide = '''
📖 키움 OpenAPI 수동 로그인 가이드

1️⃣ 사전 준비:
   • 키움증권 계좌 개설
   • 키움 홈페이지에서 OpenAPI 사용 신청
   • 모의투자 신청 (홈페이지 > 모의투자 > 상시모의투자)

2️⃣ 로그인 순서:
   • "키움 로그인" 버튼 클릭
   • 키움 로그인창이 나타나면:
     - "모의투자 접속" 체크
     - 아이디/비밀번호 입력
     - 공인인증서 비밀번호 입력

3️⃣ 로그인창이 안 나타날 때:
   • KOA Studio를 먼저 실행해서 로그인 테스트
   • 자동 로그인이 설정되어 있을 수 있음
   • 프로그램을 관리자 권한으로 실행

4️⃣ 문제 해결:
   • 오류 코드 -101: OpenAPI 사용 신청 확인
   • 오류 코드 -108: 공인인증서 확인
   • 로그인창 안 보임: KOA Studio 먼저 실행
        '''
        
        QMessageBox.information(self, "로그인 가이드", guide)
        
    def log(self, message):
        """로그 메시지 추가"""
        self.log_text.append(message)
        # 스크롤을 맨 아래로
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.End)
        self.log_text.setTextCursor(cursor)
        
    @pyqtSlot()
    def on_login_clicked(self):
        """로그인 버튼 클릭"""
        if not self.kiwoom or not self.kiwoom.ocx:
            QMessageBox.warning(self, "경고", "키움 OpenAPI가 연결되지 않았습니다.")
            return
            
        self.log("🔐 키움 로그인 시도...")
        self.log("⏳ 키움 로그인창을 기다리는 중...")
        self.log("💡 로그인창이 나타나지 않으면 'KOA Studio 실행' 버튼을 눌러보세요.")
        
        self.login_button.setEnabled(False)
        
        try:
            self.kiwoom.login()
        except Exception as e:
            self.log(f"❌ 로그인 오류: {e}")
            self.login_button.setEnabled(True)
            
    @pyqtSlot()
    def on_logout_clicked(self):
        """로그아웃 버튼 클릭"""
        if self.kiwoom:
            self.kiwoom.logout()
            
    @pyqtSlot(bool, str)
    def on_login_status_changed(self, success, message):
        """로그인 상태 변경"""
        if success:
            self.login_status_label.setText("로그인됨")
            self.login_status_label.setStyleSheet("color: green")
            self.login_button.setEnabled(False)
            self.logout_button.setEnabled(True)
            
            # 계좌 정보 업데이트
            accounts = self.kiwoom.get_account_list()
            server_type = self.kiwoom.get_server_type()
            
            self.server_type_label.setText(server_type)
            self.account_label.setText(", ".join(accounts) if accounts else "-")
            
            self.log(f"✅ {message}")
            self.log(f"📊 계좌: {accounts}")
            self.log(f"🏦 서버: {server_type}")
            
            # 체크박스 업데이트
            self.checks["mock_trading"].setChecked(server_type == "모의투자")
            self.checks["account"].setChecked(len(accounts) > 0)
            
        else:
            self.login_status_label.setText("로그인 실패")
            self.login_status_label.setStyleSheet("color: red")
            self.login_button.setEnabled(True)
            self.logout_button.setEnabled(False)
            
            self.log(f"❌ {message}")
            
    def closeEvent(self, event):
        """창 종료 시"""
        if self.kiwoom and self.kiwoom.is_connected():
            self.kiwoom.logout()
        event.accept()

def main():
    """메인 함수"""
    app = QApplication(sys.argv)
    
    # 애플리케이션 정보 설정
    app.setApplicationName("키움증권 자동매매")
    app.setApplicationVersion("1.0")
    
    # 메인 윈도우 생성
    dashboard = TradingDashboard()
    dashboard.show()
    
    print("=" * 60)
    print("키움증권 자동매매 대시보드가 실행되었습니다.")
    print("=" * 60)
    print("📌 로그인 전 확인사항:")
    print("1. 키움증권 계좌 보유")
    print("2. 키움 홈페이지에서 OpenAPI 사용 신청")
    print("3. 모의투자 신청")
    print("4. KOA Studio 설치")
    print("-" * 60)
    print("🔧 문제 해결:")
    print("• 로그인창이 안 보이면: 'KOA Studio 실행' 버튼 클릭")
    print("• API 연결 실패시: OpenAPI 사용 신청 확인")
    print("• GUI에서 '수동 로그인 가이드' 참고")
    print("=" * 60)
    
    # 애플리케이션 실행
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()