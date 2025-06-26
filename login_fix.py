    def login_kiwoom(self):
        """키움 로그인"""
        self.log("🔐 키움증권 로그인 시도...")
        self.log("⚠️ 키움 로그인창에서 '모의투자 접속'을 체크하고 로그인하세요!")
        
        try:
            # 로그인 시도 (pykiwoom 메서드명 수정)
            err_code = self.kiwoom.CommConnect()
            
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
            # 로그인 상태 확인 (pykiwoom 메서드명 수정)
            state = self.kiwoom.GetConnectState()
            
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