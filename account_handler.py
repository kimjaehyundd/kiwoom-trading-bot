# 계좌 정보 처리 전용 모듈
from PyQt5.QtCore import QObject, pyqtSignal

class AccountHandler(QObject):
    # 계좌 정보 업데이트 시그널
    account_updated = pyqtSignal(dict)
    
    def __init__(self, kiwoom_api):
        super().__init__()
        self.kiwoom = kiwoom_api
        
    def process_balance_data(self, rqname, trcode):
        """계좌 잔고 데이터 처리"""
        try:
            account_data = {}
            
            if rqname == "계좌평가잔고내역요청":
                # 예수금
                deposit = self.kiwoom.get_comm_data(trcode, "", rqname, 0, "예수금")
                if deposit:
                    account_data['deposit'] = abs(int(deposit.strip()))
                
                # 총평가액
                total_value = self.kiwoom.get_comm_data(trcode, "", rqname, 0, "총평가액")
                if total_value:
                    account_data['total_value'] = abs(int(total_value.strip()))
                
                # 총손익
                total_profit = self.kiwoom.get_comm_data(trcode, "", rqname, 0, "총손익금액")
                if total_profit:
                    account_data['total_profit'] = int(total_profit.strip())
                
                # 수익률 계산
                if 'total_value' in account_data and 'total_profit' in account_data:
                    if account_data['total_value'] > 0:
                        profit_rate = (account_data['total_profit'] / (account_data['total_value'] - account_data['total_profit'])) * 100
                        account_data['profit_rate'] = profit_rate
                
                # 보유종목 개수
                stock_count = self.kiwoom.get_repeat_cnt(trcode, rqname)
                account_data['stock_count'] = stock_count
                
                self.account_updated.emit(account_data)
                
        except Exception as e:
            print(f"계좌 데이터 처리 오류: {e}")
            
    def get_holdings_data(self, rqname, trcode):
        """보유종목 데이터 가져오기"""
        try:
            holdings = []
            stock_count = self.kiwoom.get_repeat_cnt(trcode, rqname)
            
            for i in range(stock_count):
                stock_data = {
                    'name': self.kiwoom.get_comm_data(trcode, "", rqname, i, "종목명").strip(),
                    'code': self.kiwoom.get_comm_data(trcode, "", rqname, i, "종목번호").strip(),
                    'quantity': int(self.kiwoom.get_comm_data(trcode, "", rqname, i, "보유수량").strip()),
                    'buy_price': int(self.kiwoom.get_comm_data(trcode, "", rqname, i, "매입가").strip()),
                    'current_price': int(self.kiwoom.get_comm_data(trcode, "", rqname, i, "현재가").strip()),
                    'profit': int(self.kiwoom.get_comm_data(trcode, "", rqname, i, "평가손익").strip()),
                }
                
                # 수익률 계산
                if stock_data['buy_price'] > 0:
                    profit_rate = ((stock_data['current_price'] - stock_data['buy_price']) / stock_data['buy_price']) * 100
                    stock_data['profit_rate'] = profit_rate
                
                holdings.append(stock_data)
                
            return holdings
            
        except Exception as e:
            print(f"보유종목 데이터 처리 오류: {e}")
            return []
