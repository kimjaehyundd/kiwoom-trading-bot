import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop
import pandas as pd
from config import Config

class KiwoomAPI:
    def __init__(self):
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.config = Config()
        
        # 이벤트 연결
        self.ocx.OnEventConnect.connect(self._event_connect)
        self.ocx.OnReceiveTrData.connect(self._receive_tr_data)
        self.ocx.OnReceiveRealData.connect(self._receive_real_data)
        self.ocx.OnReceiveChejanData.connect(self._receive_chejan_data)
        
        # 로그인 상태
        self.connected = False
        self.login_event_loop = None
        
    def login(self):
        """키움증권 로그인"""
        self.login_event_loop = QEventLoop()
        self.ocx.dynamicCall("CommConnect()")
        self.login_event_loop.exec_()
        
    def _event_connect(self, err_code):
        """로그인 이벤트 처리"""
        if err_code == 0:
            print("로그인 성공")
            self.connected = True
        else:
            print(f"로그인 실패: {err_code}")
            
        if self.login_event_loop:
            self.login_event_loop.exit()
            
    def get_account_list(self):
        """계좌 목록 조회"""
        if not self.connected:
            print("로그인이 필요합니다.")
            return []
            
        account_list = self.ocx.dynamicCall("GetLoginInfo(QString)", "ACCNO")
        accounts = account_list.split(';')[:-1]  # 마지막 빈 문자열 제거
        return accounts
        
    def get_stock_price(self, stock_code):
        """주식 현재가 조회"""
        if not self.connected:
            print("로그인이 필요합니다.")
            return None
            
        # TR 요청 구현 필요
        # 실제 구현시 SetInputValue, CommRqData 등 사용
        pass
        
    def _receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        """TR 데이터 수신 이벤트"""
        pass
        
    def _receive_real_data(self, jongmok_code, real_type, real_data):
        """실시간 데이터 수신 이벤트"""
        pass
        
    def _receive_chejan_data(self, gubun, item_cnt, fid_list):
        """체결 데이터 수신 이벤트"""
        pass
        
    def buy_stock(self, account, stock_code, quantity, price):
        """주식 매수 주문"""
        if not self.connected:
            print("로그인이 필요합니다.")
            return False
            
        # 실제 주문 로직 구현 필요
        print(f"매수 주문: {stock_code}, 수량: {quantity}, 가격: {price}")
        return True
        
    def sell_stock(self, account, stock_code, quantity, price):
        """주식 매도 주문"""
        if not self.connected:
            print("로그인이 필요합니다.")
            return False
            
        # 실제 주문 로직 구현 필요
        print(f"매도 주문: {stock_code}, 수량: {quantity}, 가격: {price}")
        return True