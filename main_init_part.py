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