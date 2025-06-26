import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class TradingStrategy:
    def __init__(self, kiwoom_api):
        self.api = kiwoom_api
        self.positions = {}  # 보유 포지션
        self.order_history = []  # 주문 내역
        
    def simple_moving_average_strategy(self, stock_code, short_period=5, long_period=20):
        """단순 이동평균 전략
        
        Args:
            stock_code: 종목코드
            short_period: 단기 이동평균 기간
            long_period: 장기 이동평균 기간
            
        Returns:
            signal: 'BUY', 'SELL', 'HOLD'
        """
        # 실제 구현시 과거 가격 데이터를 가져와서 계산
        # 현재는 예시 로직
        
        # 가격 데이터 조회 (실제로는 API에서 가져와야 함)
        prices = self._get_historical_prices(stock_code, long_period)
        
        if len(prices) < long_period:
            return 'HOLD'
            
        # 이동평균 계산
        short_ma = np.mean(prices[-short_period:])
        long_ma = np.mean(prices[-long_period:])
        
        # 골든크로스: 단기 이평선이 장기 이평선을 상향 돌파
        if short_ma > long_ma:
            return 'BUY'
        # 데드크로스: 단기 이평선이 장기 이평선을 하향 돌파
        elif short_ma < long_ma:
            return 'SELL'
        else:
            return 'HOLD'
            
    def rsi_strategy(self, stock_code, period=14, oversold=30, overbought=70):
        """RSI 전략
        
        Args:
            stock_code: 종목코드
            period: RSI 계산 기간
            oversold: 과매도 기준선
            overbought: 과매수 기준선
            
        Returns:
            signal: 'BUY', 'SELL', 'HOLD'
        """
        prices = self._get_historical_prices(stock_code, period + 1)
        
        if len(prices) < period + 1:
            return 'HOLD'
            
        # RSI 계산
        rsi = self._calculate_rsi(prices, period)
        
        if rsi < oversold:
            return 'BUY'  # 과매도 구간에서 매수
        elif rsi > overbought:
            return 'SELL'  # 과매수 구간에서 매도
        else:
            return 'HOLD'
            
    def _get_historical_prices(self, stock_code, days):
        """과거 가격 데이터 조회 (예시)"""
        # 실제로는 키움 API를 통해 데이터를 가져와야 함
        # 여기서는 임의의 데이터 생성
        np.random.seed(42)
        base_price = 10000
        prices = []
        
        for i in range(days):
            price = base_price + np.random.randint(-500, 500)
            prices.append(price)
            base_price = price
            
        return prices
        
    def _calculate_rsi(self, prices, period):
        """RSI 계산"""
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
        
    def execute_strategy(self, stock_codes, strategy_name="sma"):
        """전략 실행"""
        signals = {}
        
        for stock_code in stock_codes:
            if strategy_name == "sma":
                signal = self.simple_moving_average_strategy(stock_code)
            elif strategy_name == "rsi":
                signal = self.rsi_strategy(stock_code)
            else:
                signal = 'HOLD'
                
            signals[stock_code] = signal
            
            # 실제 주문 실행 (모의투자 모드에서는 로그만 출력)
            if signal == 'BUY':
                print(f"[{stock_code}] 매수 신호 발생")
                # self.api.buy_stock(account, stock_code, quantity, price)
            elif signal == 'SELL':
                print(f"[{stock_code}] 매도 신호 발생")
                # self.api.sell_stock(account, stock_code, quantity, price)
                
        return signals