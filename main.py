import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from pykiwoom.kiwoom import Kiwoom

class TradingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.kiwoom = Kiwoom()
        self.init_ui()
        self.setup_signals()
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("키움증권 자동매매 대시보드")
        self.setGeometry(100, 100, 1000, 700)
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)
        
        # 제목
        title = QLabel("키움증권 자동매매 프로그램")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title)
        
        # 로그인 섹션
        self.create_login_section(main_layout)
        
        # 계좌 정보 섹션
        self.create_account_section(main_layout)
        
        # 보유 종목 섹션
        self.create_holdings_section(main_layout)
        
        # 로그 섹션
        self.create_log_section(main_layout)
        
    def create_login_section(self, layout):
        """로그인 섹션"""
        group = QGroupBox("🔐 로그인")
        group_layout = QHBoxLayout(group)
        
        self.login_status_label = QLabel("로그인 안됨")
        self.login_status_label.setStyleSheet("color: red; font-weight: bold;")
        group_layout.addWidget(self.login_status_label)
        
        group_layout.addStretch()
        
        self.login_button = QPushButton("키움 로그인")
        self.login_button.clicked.connect(self.login_kiwoom)
        group_layout.addWidget(self.login_button)
        
        self.logout_button = QPushButton("로그아웃")
        self.logout_button.clicked.connect(self.logout_kiwoom)
        self.logout_button.setEnabled(False)
        group_layout.addWidget(self.logout_button)
        
        layout.addWidget(group)
        
    def create_account_section(self, layout):
        """계좌 정보 섹션"""
        group = QGroupBox("💰 계좌 정보")
        group_layout = QGridLayout(group)
        
        # 라벨들
        labels = ["계좌번호:", "서버타입:", "예수금:", "총평가액:", "총손익:", "수익률:"]
        self.account_labels = {}
        
        for i, label_text in enumerate(labels):
            label = QLabel(label_text)
            value_label = QLabel("-")
            value_label.setStyleSheet("font-weight: bold;")
            
            group_layout.addWidget(label, i//2, (i%2)*2)
            group_layout.addWidget(value_label, i//2, (i%2)*2+1)
            
            self.account_labels[label_text] = value_label
            
        layout.addWidget(group)
        
    def create_holdings_section(self, layout):
        """보유 종목 섹션"""
        group = QGroupBox("📊 보유 종목")
        group_layout = QVBoxLayout(group)
        
        # 테이블
        self.holdings_table = QTableWidget()
        self.holdings_table.setColumnCount(7)
        self.holdings_table.setHorizontalHeaderLabels([
            "종목명", "종목코드", "보유수량", "매입가", "현재가", "평가손익", "수익률(%)"
        ])
        
        # 테이블 스타일
        header = self.holdings_table.horizontalHeader()
        header.setStretchLastSection(True)
        self.holdings_table.setAlternatingRowColors(True)
        
        group_layout.addWidget(self.holdings_table)
        layout.addWidget(group)
        
    def create_log_section(self, layout):
        """로그 섹션"""
        group = QGroupBox("📝 로그")
        group_layout = QVBoxLayout(group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        group_layout.addWidget(self.log_text)
        
        layout.addWidget(group)
        
    def setup_signals(self):
        """시그널 연결"""
        # pykiwoom 시그널 연결 (필요시 구현)
        pass
        
    def login_kiwoom(self):
        """키움 로그인"""
        self.log("🔐 키움증권 로그인 시도...")
        self.log("⚠️ 키움 로그인창에서 '모의투자 접속'을 체크하고 로그인하세요!")
        
        try:
            # 로그인 시도
            err_code = self.kiwoom.comm_connect()
            
            if err_code == 0:
                self.log("✅ 로그인 요청 성공 - 키움 로그인창 대기 중...")
                
                # 로그인 완료까지 대기
                self.login_button.setEnabled(False)
                
                # 2초 후 로그인 상태 확인
                QTimer.singleShot(2000, self.check_login_status)
                
            else:
                self.log(f"❌ 로그인 요청 실패: {err_code}")
                
        except Exception as e:
            self.log(f"❌ 로그인 오류: {e}")
            
    def check_login_status(self):
        """로그인 상태 확인"""
        try:
            # 로그인 상태 확인
            state = self.kiwoom.get_connect_state()
            
            if state == 1:
                self.log("✅ 로그인 성공!")
                self.login_status_label.setText("로그인됨")
                self.login_status_label.setStyleSheet("color: green; font-weight: bold;")
                
                self.login_button.setEnabled(False)
                self.logout_button.setEnabled(True)
                
                # 계좌 정보 가져오기
                self.load_account_info()
                
            else:
                self.log("❌ 로그인 대기 중... 키움 로그인창에서 로그인해주세요.")
                self.login_button.setEnabled(True)
                
                # 5초 후 다시 확인
                QTimer.singleShot(5000, self.check_login_status)
                
        except Exception as e:
            self.log(f"❌ 로그인 상태 확인 오류: {e}")
            self.login_button.setEnabled(True)
            
    def load_account_info(self):
        """계좌 정보 로드"""
        try:
            # 계좌 목록
            accounts = self.kiwoom.get_login_info("ACCNO").split(';')
            accounts = [acc for acc in accounts if acc]  # 빈 문자열 제거
            
            if accounts:
                account = accounts[0]  # 첫 번째 계좌 사용
                self.account_labels["계좌번호:"].setText(account)
                
                # 서버 타입
                server_type = self.kiwoom.get_login_info("GetServerGubun")
                server_name = "모의투자" if server_type == "1" else "실계좌"
                self.account_labels["서버타입:"].setText(server_name)
                
                # 사용자 정보
                user_name = self.kiwoom.get_login_info("USER_NAME")
                self.log(f"👤 사용자: {user_name}")
                self.log(f"🏦 서버: {server_name}")
                self.log(f"📊 계좌: {account}")
                
                # 계좌 잔고 정보 요청
                self.request_balance()
                
            else:
                self.log("❌ 계좌 정보를 가져올 수 없습니다.")
                
        except Exception as e:
            self.log(f"❌ 계좌 정보 로드 오류: {e}")
            
    def request_balance(self):
        """잔고 및 보유종목 정보 요청"""
        try:
            # 계좌 번호
            account = self.account_labels["계좌번호:"].text()
            
            if account and account != "-":
                self.log("💰 계좌 잔고 정보 요청 중...")
                
                # 계좌평가잔고내역요청 (opw00018)
                self.kiwoom.set_input_value("계좌번호", account)
                self.kiwoom.set_input_value("비밀번호", "")
                self.kiwoom.set_input_value("비밀번호입력매체구분", "00")
                self.kiwoom.set_input_value("조회구분", "1")
                
                # TR 요청
                err_code = self.kiwoom.comm_rq_data("계좌평가잔고내역요청", "opw00018", 0, "2000")
                
                if err_code == 0:
                    self.log("✅ 잔고 정보 요청 성공")
                    # 응답 처리는 OnReceiveTrData 이벤트에서 처리 (추후 구현)
                else:
                    self.log(f"❌ 잔고 정보 요청 실패: {err_code}")
                    
        except Exception as e:
            self.log(f"❌ 잔고 정보 요청 오류: {e}")
            
    def logout_kiwoom(self):
        """키움 로그아웃"""
        try:
            self.kiwoom.comm_terminate()
            
            self.login_status_label.setText("로그인 안됨")
            self.login_status_label.setStyleSheet("color: red; font-weight: bold;")
            
            self.login_button.setEnabled(True)
            self.logout_button.setEnabled(False)
            
            # 계좌 정보 초기화
            for label in self.account_labels.values():
                label.setText("-")
                
            # 보유종목 테이블 초기화
            self.holdings_table.setRowCount(0)
            
            self.log("🚪 로그아웃 완료")
            
        except Exception as e:
            self.log(f"❌ 로그아웃 오류: {e}")
            
    def log(self, message):
        """로그 메시지 추가"""
        self.log_text.append(f"[{QTime.currentTime().toString()}] {message}")
        
        # 스크롤을 맨 아래로
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.End)
        self.log_text.setTextCursor(cursor)
        
    def closeEvent(self, event):
        """프로그램 종료 시"""
        try:
            if self.kiwoom.get_connect_state() == 1:
                self.kiwoom.comm_terminate()
        except:
            pass
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    print("=" * 50)
    print("키움증권 자동매매 프로그램 시작")
    print("=" * 50)
    print("📌 실행 전 확인사항:")
    print("✓ 32bit Python 환경")
    print("✓ pykiwoom 라이브러리 설치")
    print("✓ 키움증권 OpenAPI 사용 신청")
    print("✓ 모의투자 신청")
    print("=" * 50)
    
    window = TradingApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()