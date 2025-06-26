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
            self.load_condition_button.setEnabled(False)
            
            # 계좌 정보 초기화
            for label in self.account_labels.values():
                label.setText("-")
                
            # 테이블 초기화
            self.holdings_table.setRowCount(0)
            self.realtime_table.setRowCount(0)
            self.condition_table.setRowCount(0)
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