import sys
from PyQt5.QtWidgets import QApplication
from kiwoom_api import KiwoomAPI
from strategy import TradingStrategy
from config import Config
import time

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("키움증권 자동매매 프로그램 시작 (테스트 모드)")
    print("=" * 50)
    
    # PyQt5 애플리케이션 생성 (테스트 모드에서는 생략)
    # app = QApplication(sys.argv)
    
    try:
        # 키움 API 초기화 (테스트 모드에서는 주석 처리)
        # kiwoom = KiwoomAPI()
        # print("키움 API 초기화 완료")
        kiwoom = None  # 테스트용
        print("테스트 모드로 실행 (키움 API 연결 없음)")
        
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
        print("※ 실제 가격이 아닌 가상의 데이터를 사용합니다")
        
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
            
        print("\n✅ 프로그램이 정상적으로 실행되었습니다!")
        print("\n📌 실제 매매를 위해서는:")
        print("1. 키움증권 계좌 개설 및 OpenAPI 신청")
        print("2. config.py에서 계좌 정보 설정")
        print("3. main.py에서 키움 API 초기화 주석 해제")
        print("4. 로그인 기능 활성화")
        
        print("\n🎯 현재는 매매 전략 로직만 테스트하는 모드입니다.")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("\n🔧 문제 해결 방법:")
        print("1. 필요한 패키지가 모두 설치되어 있는지 확인")
        print("2. Python 가상환경이 활성화되어 있는지 확인")
        print("3. requirements.txt의 패키지들이 정상 설치되었는지 확인")
        
    print("\n프로그램을 종료합니다.")

if __name__ == "__main__":
    main()