# 조건식 자동매매 모듈
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import time

class ConditionHandler(QObject):
    # 조건식 검색 결과 시그널
    condition_result = pyqtSignal(str, list)  # (조건식명, 종목리스트)
    
    def __init__(self, kiwoom_api):
        super().__init__()
        self.kiwoom = kiwoom_api
        self.condition_list = {}  # 조건식 목록
        self.monitoring_conditions = []  # 감시 중인 조건식
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.monitor_conditions)
        
    def load_condition_list(self):
        """조건식 목록 로드"""
        try:
            # 조건식 목록 요청
            result = self.kiwoom.get_condition_load()
            
            if result == 1:
                # 조건식 목록 가져오기
                conditions = self.kiwoom.get_condition_name_list()
                
                self.condition_list = {}
                for condition in conditions:
                    parts = condition.split('^')
                    if len(parts) >= 2:
                        index = parts[0]
                        name = parts[1]
                        self.condition_list[index] = name
                        
                print(f"✅ 조건식 {len(self.condition_list)}개 로드 완료")
                return True
            else:
                print("❌ 조건식 로드 실패")
                return False
                
        except Exception as e:
            print(f"❌ 조건식 로드 오류: {e}")
            return False
            
    def get_condition_list(self):
        """조건식 목록 반환"""
        return self.condition_list
        
    def start_condition_search(self, condition_index, condition_name):
        """조건식 검색 시작"""
        try:
            # 실시간 조건검색 시작
            result = self.kiwoom.send_condition_stop("0156", condition_name, condition_index, 1)
            
            if result == 1:
                print(f"✅ 조건식 '{condition_name}' 검색 시작")
                if condition_index not in self.monitoring_conditions:
                    self.monitoring_conditions.append(condition_index)
                return True
            else:
                print(f"❌ 조건식 '{condition_name}' 검색 시작 실패")
                return False
                
        except Exception as e:
            print(f"❌ 조건식 검색 시작 오류: {e}")
            return False
            
    def stop_condition_search(self, condition_index, condition_name):
        """조건식 검색 중단"""
        try:
            result = self.kiwoom.send_condition_stop("0156", condition_name, condition_index, 0)
            
            if result == 1:
                print(f"✅ 조건식 '{condition_name}' 검색 중단")
                if condition_index in self.monitoring_conditions:
                    self.monitoring_conditions.remove(condition_index)
                return True
            else:
                print(f"❌ 조건식 '{condition_name}' 검색 중단 실패")
                return False
                
        except Exception as e:
            print(f"❌ 조건식 검색 중단 오류: {e}")
            return False
            
    def on_receive_condition_ver(self, ret, msg):
        """조건식 목록 수신 이벤트"""
        if ret == 1:
            print("✅ 조건식 목록 수신 완료")
            self.load_condition_list()
        else:
            print(f"❌ 조건식 목록 수신 실패: {msg}")
            
    def on_receive_real_condition(self, code, type, condition_name, condition_index):
        """실시간 조건검색 결과 수신"""
        try:
            if type == "I":  # 편입
                print(f"📈 조건편입: {code} ({self.kiwoom.get_master_code_name(code)})")
            elif type == "D":  # 이탈
                print(f"📉 조건이탈: {code} ({self.kiwoom.get_master_code_name(code)})")
                
            # 조건식 결과 시그널 발생
            self.condition_result.emit(condition_name, [code])
            
        except Exception as e:
            print(f"❌ 실시간 조건검색 처리 오류: {e}")
            
    def start_monitoring(self, interval=5):
        """조건식 모니터링 시작"""
        if not self.monitor_timer.isActive():
            self.monitor_timer.start(interval * 1000)  # 초 단위를 밀리초로 변환
            print(f"✅ 조건식 모니터링 시작 (간격: {interval}초)")
            
    def stop_monitoring(self):
        """조건식 모니터링 중단"""
        if self.monitor_timer.isActive():
            self.monitor_timer.stop()
            print("✅ 조건식 모니터링 중단")
            
    def monitor_conditions(self):
        """조건식 상태 모니터링"""
        try:
            current_time = time.strftime("%H:%M:%S")
            if self.monitoring_conditions:
                print(f"[{current_time}] 📊 {len(self.monitoring_conditions)}개 조건식 모니터링 중...")
                
        except Exception as e:
            print(f"❌ 조건식 모니터링 오류: {e}")
