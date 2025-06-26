import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pykiwoom.kiwoom import Kiwoom

# 새 모듈들 import
from account_handler import AccountHandler
from condition_handler import ConditionHandler

class TradingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.kiwoom = Kiwoom()
        self.watch_stocks = {}  # 실시간 감시 종목들
        self.real_data = {}  # 실시간 데이터 저장
        
        # 새 핸들러들 초기화
        self.account_handler = AccountHandler(self.kiwoom)
        self.condition_handler = ConditionHandler(self.kiwoom)
        
        self.init_ui()
        self.setup_signals()
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("키움증권 자동매매 대시보드")
        self.setGeometry(100, 100, 1200, 800)
        
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
        
        # 실시간 감시 종목 섹션 추가
        self.create_realtime_section(main_layout)
        
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
        
    def create_realtime_section(self, layout):
        """실시간 데이터 섹션"""
        group = QGroupBox("📈 실시간 감시 종목")
        group_layout = QVBoxLayout(group)
        
        # 종목 추가 입력부
        input_layout = QHBoxLayout()
        
        self.stock_code_input = QLineEdit()
        self.stock_code_input.setPlaceholderText("종목코드 입력 (예: 005930)")
        self.stock_code_input.returnPressed.connect(self.add_watch_stock)
        input_layout.addWidget(QLabel("종목코드:"))
        input_layout.addWidget(self.stock_code_input)
        
        self.add_stock_button = QPushButton("감시 추가")
        self.add_stock_button.clicked.connect(self.add_watch_stock)
        self.add_stock_button.setEnabled(False)
        input_layout.addWidget(self.add_stock_button)
        
        self.remove_stock_button = QPushButton("선택 제거")
        self.remove_stock_button.clicked.connect(self.remove_watch_stock)
        self.remove_stock_button.setEnabled(False)
        input_layout.addWidget(self.remove_stock_button)
        
        group_layout.addLayout(input_layout)
        
        # 실시간 데이터 테이블
        self.realtime_table = QTableWidget()
        self.realtime_table.setColumnCount(8)
        self.realtime_table.setHorizontalHeaderLabels([
            "종목명", "종목코드", "현재가", "전일대비", "등락률", "거래량", "시간", "상태"
        ])
        
        # 테이블 스타일
        header = self.realtime_table.horizontalHeader()
        header.setStretchLastSection(True)
        self.realtime_table.setAlternatingRowColors(True)
        self.realtime_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        group_layout.addWidget(self.realtime_table)
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
        """pykiwoom 시그널 연결"""
        try:
            # 기본 pykiwoom 시그널
            self.kiwoom.OnReceiveRealData.connect(self.receive_real_data)
            self.kiwoom.OnReceiveTrData.connect(self.receive_tr_data)
            
            # 새 핸들러 시그널 연결
            self.account_handler.account_updated.connect(self.update_account_display)
            self.condition_handler.condition_result.connect(self.on_condition_result)
            
            self.log("✅ 시그널 연결 완료")
        except Exception as e:
            self.log(f"❌ 시그널 연결 오류: {e}")
    
    def update_account_display(self, account_data):
        """계좌 정보 화면 업데이트 (새 핸들러 연동)"""
        try:
            if 'deposit' in account_data:
                self.account_labels["예수금:"].setText(f"{account_data['deposit']:,}원")
            
            if 'total_value' in account_data:
                self.account_labels["총평가액:"].setText(f"{account_data['total_value']:,}원")
            
            if 'total_profit' in account_data:
                profit_val = account_data['total_profit']
                profit_text = f"{profit_val:+,}원"
                label = self.account_labels["총손익:"]
                label.setText(profit_text)
                
                # 손익에 따른 색상 설정
                if profit_val > 0:
                    label.setStyleSheet("color: red; font-weight: bold;")
                elif profit_val < 0:
                    label.setStyleSheet("color: blue; font-weight: bold;")
                else:
                    label.setStyleSheet("color: black; font-weight: bold;")
            
            if 'profit_rate' in account_data:
                rate_text = f"{account_data['profit_rate']:+.2f}%"
                self.account_labels["수익률:"].setText(rate_text)
            
            self.log("✅ 계좌 정보 업데이트 완료 (새 핸들러)")
            
        except Exception as e:
            self.log(f"❌ 계좌 화면 업데이트 오류: {e}")
    
    def on_condition_result(self, condition_name, stock_list):
        """조건검색 결과 처리 (새 핸들러 연동)"""
        try:
            for stock_code in stock_list:
                stock_name = self.kiwoom.get_master_code_name(stock_code)
                self.log(f"🎯 조건편입: {stock_name}({stock_code}) - {condition_name}")
                
        except Exception as e:
            self.log(f"❌ 조건검색 결과 처리 오류: {e}")
            
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
                self.add_stock_button.setEnabled(True)
                self.remove_stock_button.setEnabled(True)
                
                # 계좌 정보 가져오기
                self.load_account_info()
                
                # 기본 종목 추가 (삼성전자)
                self.stock_code_input.setText("005930")
                self.add_watch_stock()
                
            else:
                self.log("❌ 로그인 대기 중... 키움 로그인창에서 로그인해주세요.")
                self.login_button.setEnabled(True)
                
                # 5초 후 다시 확인
                QTimer.singleShot(5000, self.check_login_status)
                
        except Exception as e:
            self.log(f"❌ 로그인 상태 확인 오류: {e}")
            self.login_button.setEnabled(True)
            
    def add_watch_stock(self):
        """실시간 감시 종목 추가"""
        stock_code = self.stock_code_input.text().strip()
        
        if not stock_code:
            self.log("❌ 종목코드를 입력하세요.")
            return
            
        if len(stock_code) != 6 or not stock_code.isdigit():
            self.log("❌ 올바른 종목코드를 입력하세요. (6자리 숫자)")
            return
            
        if stock_code in self.watch_stocks:
            self.log(f"❌ {stock_code}는 이미 감시 중입니다.")
            return
            
        try:
            # 종목명 조회
            stock_name = self.kiwoom.get_master_code_name(stock_code)
            
            if not stock_name:
                self.log(f"❌ {stock_code}: 올바르지 않은 종목코드입니다.")
                return
                
            # 실시간 등록
            self.kiwoom.set_real_reg("1000", stock_code, "9001;10;12;27;28;13;14;16;17;18;25;26;29;30", "1")
            
            # 테이블에 추가
            row = self.realtime_table.rowCount()
            self.realtime_table.insertRow(row)
            
            self.realtime_table.setItem(row, 0, QTableWidgetItem(stock_name))
            self.realtime_table.setItem(row, 1, QTableWidgetItem(stock_code))
            self.realtime_table.setItem(row, 2, QTableWidgetItem("-"))
            self.realtime_table.setItem(row, 3, QTableWidgetItem("-"))
            self.realtime_table.setItem(row, 4, QTableWidgetItem("-"))
            self.realtime_table.setItem(row, 5, QTableWidgetItem("-"))
            self.realtime_table.setItem(row, 6, QTableWidgetItem("-"))
            self.realtime_table.setItem(row, 7, QTableWidgetItem("등록됨"))
            
            # 감시 목록에 추가
            self.watch_stocks[stock_code] = {
                'name': stock_name,
                'row': row
            }
            
            self.log(f"✅ {stock_name}({stock_code}) 실시간 감시 시작")
            self.stock_code_input.clear()
            
        except Exception as e:
            self.log(f"❌ 종목 추가 오류: {e}")
            
    def remove_watch_stock(self):
        """선택된 감시 종목 제거"""
        current_row = self.realtime_table.currentRow()
        
        if current_row < 0:
            self.log("❌ 제거할 종목을 선택하세요.")
            return
            
        try:
            stock_code = self.realtime_table.item(current_row, 1).text()
            stock_name = self.realtime_table.item(current_row, 0).text()
            
            # 실시간 해제
            self.kiwoom.set_real_remove("1000", stock_code)
            
            # 테이블에서 제거
            self.realtime_table.removeRow(current_row)
            
            # 감시 목록에서 제거
            if stock_code in self.watch_stocks:
                del self.watch_stocks[stock_code]
                
            # 남은 행들의 row 번호 업데이트
            for code, info in self.watch_stocks.items():
                if info['row'] > current_row:
                    info['row'] -= 1
                    
            self.log(f"✅ {stock_name}({stock_code}) 감시 중단")
            
        except Exception as e:
            self.log(f"❌ 종목 제거 오류: {e}")
            
    def receive_real_data(self, code, real_type, real_data):
        """실시간 데이터 수신"""
        try:
            if code in self.watch_stocks:
                row = self.watch_stocks[code]['row']
                
                if real_type == "주식시세":
                    # 현재가
                    current_price = self.kiwoom.get_comm_real_data(code, 10)
                    if current_price:
                        price = abs(int(current_price))
                        self.realtime_table.setItem(row, 2, QTableWidgetItem(f"{price:,}"))
                    
                    # 전일대비
                    change = self.kiwoom.get_comm_real_data(code, 12)
                    if change:
                        change_val = int(change)
                        change_text = f"{change_val:+,}" if change_val != 0 else "0"
                        item = QTableWidgetItem(change_text)
                        
                        # 색상 설정
                        if change_val > 0:
                            item.setForeground(QColor("red"))
                        elif change_val < 0:
                            item.setForeground(QColor("blue"))
                            
                        self.realtime_table.setItem(row, 3, item)
                    
                    # 등락률
                    rate = self.kiwoom.get_comm_real_data(code, 12)
                    if rate:
                        rate_val = float(rate)
                        rate_text = f"{rate_val:+.2f}%"
                        item = QTableWidgetItem(rate_text)
                        
                        # 색상 설정
                        if rate_val > 0:
                            item.setForeground(QColor("red"))
                        elif rate_val < 0:
                            item.setForeground(QColor("blue"))
                            
                        self.realtime_table.setItem(row, 4, item)
                    
                    # 거래량
                    volume = self.kiwoom.get_comm_real_data(code, 13)
                    if volume:
                        vol = int(volume)
                        self.realtime_table.setItem(row, 5, QTableWidgetItem(f"{vol:,}"))
                    
                    # 시간
                    time = self.kiwoom.get_comm_real_data(code, 20)
                    if time:
                        formatted_time = f"{time[:2]}:{time[2:4]}:{time[4:6]}"
                        self.realtime_table.setItem(row, 6, QTableWidgetItem(formatted_time))
                    
                    # 상태
                    self.realtime_table.setItem(row, 7, QTableWidgetItem("실시간"))
                    
        except Exception as e:
            self.log(f"❌ 실시간 데이터 처리 오류: {e}")
            
    def receive_tr_data(self, screen_no, rqname, trcode, record_name, prev_next):
        """TR 데이터 수신 (새 핸들러 연동)"""
        try:
            if rqname == "계좌평가잔고내역요청":
                # 새 핸들러로 처리 위임
                self.account_handler.process_balance_data(rqname, trcode)
        except Exception as e:
            self.log(f"❌ TR 데이터 처리 오류: {e}")
            
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
                else:
                    self.log(f"❌ 잔고 정보 요청 실패: {err_code}")
                    
        except Exception as e:
            self.log(f"❌ 잔고 정보 요청 오류: {e}")
            
    def logout_kiwoom(self):
        """키움 로그아웃"""
        try:
            # 모든 실시간 등록 해제
            for stock_code in list(self.watch_stocks.keys()):
                self.kiwoom.set_real_remove("1000", stock_code)
                
            self.kiwoom.comm_terminate()
            
            self.login_status_label.setText("로그인 안됨")
            self.login_status_label.setStyleSheet("color: red; font-weight: bold;")
            
            self.login_button.setEnabled(True)
            self.logout_button.setEnabled(False)
            self.add_stock_button.setEnabled(False)
            self.remove_stock_button.setEnabled(False)
            
            # 계좌 정보 초기화
            for label in self.account_labels.values():
                label.setText("-")
                
            # 테이블 초기화
            self.holdings_table.setRowCount(0)
            self.realtime_table.setRowCount(0)
            self.watch_stocks.clear()
            
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