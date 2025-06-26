# 키움증권 API 설정
class Config:
    # 키움증권 계좌 정보 (실제 사용시 변경 필요)
    ACCOUNT_NUMBER = ""  # 계좌번호 입력
    ACCOUNT_PASSWORD = ""  # 계좌 비밀번호
    
    # API 설정
    API_VERSION = "1.0"
    
    # 로그 설정
    LOG_LEVEL = "INFO"
    LOG_FILE = "trading.log"
    
    # 매매 설정
    MAX_POSITION_SIZE = 1000000  # 최대 포지션 크기 (원)
    STOP_LOSS_PERCENT = 0.03  # 손절 비율 (3%)
    TAKE_PROFIT_PERCENT = 0.05  # 익절 비율 (5%)
    
    # 모의투자 설정
    MOCK_INVESTMENT = True  # True: 모의투자, False: 실제투자