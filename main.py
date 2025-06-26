import sys
from PyQt5.QtWidgets import QApplication
from kiwoom_api import KiwoomAPI
from strategy import TradingStrategy
from config import Config
import time

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("키움증권 자동매매 프로그램 시작")
    print("=" * 50)
    
    # PyQt5 애플리케이션 생성
    app = QApplication(sys.argv)
    
    try:
        # 키움 API 초기화
        kiwoom = KiwoomAPI()
        print("키움 API 초기화 완료")
        
        # 로그인 (실제 사용시 주석 해제)
        # kiwoom.login()
        
        # 매매 전략 초기화
        strategy = TradingStrategy(kiwoom)
        print("매매 전략 초기화 완료")
        
        # 테스트용 종목 리스트
        test_stocks = [
            "005930",  # 삼성전자
            "000660",  # SK하이닉스
            "035420",  # NAVER
            "005380",  # 현대차
        ]
        
        print("\n테스트 모드로 전략 실행 중...")
        
        # 전략 실행 (단순 이동평균)
        print("\n[단순 이동평균 전략]")
        sma_signals = strategy.execute_strategy(test_stocks, "sma")
        
        # 전략 실행 (RSI)
        print("\n[RSI 전략]")
        rsi_signals = strategy.execute_strategy(test_stocks, "rsi")
        
        # 결과 출력
        print("\n=== 전략 실행 결과 ===")
        print("종목코드\t단순이평\tRSI")
        print("-" * 30)
        for stock_code in test_stocks:
            print(f"{stock_code}\t{sma_signals[stock_code]}\t{rsi_signals[stock_code]}")
            
        print("\n프로그램이 정상적으로 실행되었습니다!")
        print("실제 매매를 위해서는:")
        print("1. 키움증권 KOA Studio 설치")
        print("2. OpenAPI 신청")
        print("3. config.py에서 계좌 정보 설정")
        print("4. main.py에서 kiwoom.login() 주석 해제")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        print("\n문제 해결 방법:")
        print("1. 키움증권 KOA Studio가 설치되어 있는지 확인")
        print("2. 필요한 패키지가 모두 설치되어 있는지 확인")
        print("3. Python 가상환경이 활성화되어 있는지 확인")
        
    # 애플리케이션 종료
    sys.exit(0)

if __name__ == "__main__":
    main()