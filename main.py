import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QTextEdit, QLineEdit,
                           QMessageBox, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QFont
from kiwoom_api import KiwoomAPI

class TradingDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.kiwoom = None
        self.init_ui()
        self.init_kiwoom()
        
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
        
        # 연결 상태 그룹
        self.create_connection_group(main_layout)
        
        # 로그 그룹
        self.create_log_group(main_layout)
        
        # 제어 버튼 그룹
        self.create_control_group(main_layout)
        
    def create_connection_group(self, parent_layout):
        """연결 상태 그룹 생성"""
        group = QGroupBox("연결 상태")
        layout = QGridLayout(group)
        
        # API 상태
        layout.addWidget(QLabel("API 상태:"), 0, 0)
        self.api_status_label = QLabel("연결 시도 중...")
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
        group = QGroupBox("로그")
        layout = QVBoxLayout(group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        parent_layout.addWidget(group)
        
    def create_control_group(self, parent_layout):
        """제어 버튼 그룹 생성"""
        group = QGroupBox("제어")
        layout = QHBoxLayout(group)
        
        self.login_button = QPushButton("로그인")
        self.login_button.clicked.connect(self.on_login_clicked)
        layout.addWidget(self.login_button)
        
        self.logout_button = QPushButton("로그아웃")
        self.logout_button.clicked.connect(self.on_logout_clicked)
        self.logout_button.setEnabled(False)
        layout.addWidget(self.logout_button)
        
        self.test_button = QPushButton("테스트 모드")
        self.test_button.clicked.connect(self.on_test_mode_clicked)
        layout.addWidget(self.test_button)
        
        parent_layout.addWidget(group)
        
    def init_kiwoom(self):
        """키움 API 초기화"""
        self.log("키움 OpenAPI 초기화 중...")
        
        try:
            self.kiwoom = KiwoomAPI()
            self.kiwoom.login_status_changed.connect(self.on_login_status_changed)
            
            if self.kiwoom.ocx:
                self.api_status_label.setText("API 연결됨")
                self.api_status_label.setStyleSheet("color: green")
                self.log("✅ 키움 OpenAPI 연결 성공")
                self.log("📌 로그인 버튼을 클릭하여 로그인하세요")
            else:
                self.api_status_label.setText("API 연결 실패")
                self.api_status_label.setStyleSheet("color: red")
                self.log("❌ 키움 OpenAPI 연결 실패")
                self.log("📌 테스트 모드 버튼을 클릭하여 가상 모드로 실행하세요")
                self.login_button.setEnabled(False)
                
        except Exception as e:
            self.api_status_label.setText("API 초기화 오류")
            self.api_status_label.setStyleSheet("color: red")
            self.log(f"❌ API 초기화 오류: {e}")
            self.login_button.setEnabled(False)
            
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
            
        self.log("🔐 로그인 시도 중...")
        self.log("⏳ 키움증권 로그인 창에서 로그인해주세요...")
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
            
    @pyqtSlot()
    def on_test_mode_clicked(self):
        """테스트 모드 버튼 클릭"""
        self.log("🧪 테스트 모드로 전환합니다...")
        
        if not self.kiwoom:
            self.kiwoom = KiwoomAPI()
            self.kiwoom.login_status_changed.connect(self.on_login_status_changed)
            
        self.kiwoom._simulate_login()
        
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
    
    print("GUI 대시보드가 실행되었습니다.")
    print("키움증권 로그인이 필요하면 GUI 창에서 '로그인' 버튼을 클릭하세요.")
    print("테스트만 원하면 '테스트 모드' 버튼을 클릭하세요.")
    
    # 애플리케이션 실행
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()