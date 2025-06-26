import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QTextEdit,
                           QMessageBox, QGroupBox, QGridLayout, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont
from kiwoom_api import KiwoomAPI

class TradingDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.kiwoom = None
        self.init_ui()
        self.check_environment()
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("키움증권 자동매매 대시보드")
        self.setGeometry(100, 100, 800, 600)
        
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
        
        # 환경 체크 그룹
        self.create_environment_group(main_layout)
        
        # 연결 상태 그룹
        self.create_connection_group(main_layout)
        
        # 로그 그룹
        self.create_log_group(main_layout)
        
        # 제어 버튼 그룹
        self.create_control_group(main_layout)
        
    def create_environment_group(self, parent_layout):
        """환경 체크 그룹"""
        group = QGroupBox("📋 환경 체크")
        layout = QVBoxLayout(group)
        
        self.env_status = QLabel("환경 체크 중...")
        self.env_status.setStyleSheet("color: orange")
        layout.addWidget(self.env_status)
        
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
        
        self.guide_button = QPushButton("사용 가이드")
        self.guide_button.clicked.connect(self.show_guide)
        layout.addWidget(self.guide_button)
        
        parent_layout.addWidget(group)
        
    def check_environment(self):
        """환경 체크"""
        self.log("🔍 환경 체크 시작...")
        
        # KOA Studio 체크
        koa_paths = [
            "C:\\OpenAPI\\KOAStudioSA.exe",
            "C:\\OpenApi\\KOAStudioSA.exe"
        ]
        
        koa_found = any(os.path.exists(path) for path in koa_paths)
        
        if koa_found:
            self.log("✅ KOA Studio 설치 확인됨")
            self.env_status.setText("환경 확인 완료")
            self.env_status.setStyleSheet("color: green")
        else:
            self.log("❌ KOA Studio가 설치되지 않았습니다.")
            self.env_status.setText("KOA Studio 설치 필요")
            self.env_status.setStyleSheet("color: red")
        
        # API 초기화
        self.init_kiwoom()
        
    def init_kiwoom(self):
        """키움 API 초기화"""
        self.log("🔌 키움 OpenAPI 초기화...")
        
        try:
            self.kiwoom = KiwoomAPI()
            self.kiwoom.login_status_changed.connect(self.on_login_status_changed)
            
            if self.kiwoom.ocx:
                self.api_status_label.setText("API 연결됨")
                self.api_status_label.setStyleSheet("color: green")
                self.log("✅ 키움 OpenAPI 연결 성공")
                self.login_button.setEnabled(True)
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
        self.log("4. 사용 등록 신청 및 승인 대기")
        self.log("5. 모의투자 > 상시모의투자 신청")
        
    def show_guide(self):
        """사용 가이드"""
        guide = '''
🔧 키움증권 OpenAPI 사용 가이드

📋 사전 준비사항:
• 키움증권 계좌 개설
• 키움 홈페이지에서 OpenAPI 사용 신청
• 모의투자 신청 (상시모의투자)
• KOA Studio 설치

🔐 로그인 방법:
1. 다른 키움 프로그램(KOA Studio 등) 모두 종료
2. "키움 로그인" 버튼 클릭
3. 키움 로그인창에서 "모의투자 접속" 체크
4. 아이디/비밀번호 입력 후 로그인

❌ 문제 해결:
• 로그인창이 안 보임: 다른 키움 프로그램 종료
• API 연결 실패: OpenAPI 사용 신청 확인
• 오류코드 -101: OpenAPI 승인 확인
• 오류코드 -106: 중복 로그인 (다른 프로그램 종료)
        '''
        QMessageBox.information(self, "사용 가이드", guide)
        
    def log(self, message):
        """로그 메시지 추가"""
        self.log_text.append(message)
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
        self.log("⚠️  중요: 다른 키움 프로그램을 모두 종료해주세요!")
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
            
            if server_type == "모의투자":
                self.log("🎯 이제 모의투자 계좌에서 자동매매를 테스트할 수 있습니다!")
            
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
    print("키움증권 자동매매 대시보드 실행됨")
    print("=" * 60)
    print("🚀 실행 전 체크리스트:")
    print("✓ 키움증권 계좌 보유")
    print("✓ OpenAPI 사용 신청 완료")
    print("✓ 모의투자 신청 완료")  
    print("✓ KOA Studio 설치")
    print("✓ 다른 키움 프로그램 종료")
    print("-" * 60)
    print("💡 로그인 방법:")
    print("1. '키움 로그인' 버튼 클릭")
    print("2. 로그인창에서 '모의투자 접속' 체크")
    print("3. 아이디/비밀번호 입력")
    print("=" * 60)
    
    # 애플리케이션 실행
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()