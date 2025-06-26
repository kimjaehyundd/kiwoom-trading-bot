    def create_condition_section(self, layout):
        """조건식 섹션"""
        group = QGroupBox("🎯 조건식 자동매매")
        group_layout = QVBoxLayout(group)
        
        # 조건식 제어 버튼들
        button_layout = QHBoxLayout()
        
        self.load_condition_button = QPushButton("조건식 로드")
        self.load_condition_button.clicked.connect(self.load_conditions)
        self.load_condition_button.setEnabled(False)
        button_layout.addWidget(self.load_condition_button)
        
        self.condition_combo = QComboBox()
        self.condition_combo.setPlaceholderText("조건식 선택")
        button_layout.addWidget(self.condition_combo)
        
        self.start_condition_button = QPushButton("조건검색 시작")
        self.start_condition_button.clicked.connect(self.start_condition_search)
        self.start_condition_button.setEnabled(False)
        button_layout.addWidget(self.start_condition_button)
        
        self.stop_condition_button = QPushButton("조건검색 중단")
        self.stop_condition_button.clicked.connect(self.stop_condition_search)
        self.stop_condition_button.setEnabled(False)
        button_layout.addWidget(self.stop_condition_button)
        
        group_layout.addLayout(button_layout)
        
        # 조건검색 결과 테이블
        self.condition_table = QTableWidget()
        self.condition_table.setColumnCount(5)
        self.condition_table.setHorizontalHeaderLabels([
            "시간", "조건식", "종목명", "종목코드", "상태"
        ])
        
        # 테이블 스타일
        header = self.condition_table.horizontalHeader()
        header.setStretchLastSection(True)
        self.condition_table.setAlternatingRowColors(True)
        
        group_layout.addWidget(self.condition_table)
        layout.addWidget(group)
        
    def load_conditions(self):
        """조건식 로드"""
        try:
            self.log("📋 조건식 로드 중...")
            
            if self.condition_handler.load_condition_list():
                conditions = self.condition_handler.get_condition_list()
                
                self.condition_combo.clear()
                for index, name in conditions.items():
                    self.condition_combo.addItem(f"{name} ({index})", index)
                
                self.start_condition_button.setEnabled(True)
                self.log(f"✅ 조건식 {len(conditions)}개 로드 완료")
            else:
                self.log("❌ 조건식 로드 실패")
                
        except Exception as e:
            self.log(f"❌ 조건식 로드 오류: {e}")
    
    def start_condition_search(self):
        """조건검색 시작"""
        try:
            if self.condition_combo.currentIndex() < 0:
                self.log("❌ 조건식을 선택하세요")
                return
            
            condition_index = self.condition_combo.currentData()
            condition_name = self.condition_combo.currentText().split(' (')[0]
            
            if self.condition_handler.start_condition_search(condition_index, condition_name):
                self.stop_condition_button.setEnabled(True)
                self.start_condition_button.setEnabled(False)
                self.condition_handler.start_monitoring()
                
        except Exception as e:
            self.log(f"❌ 조건검색 시작 오류: {e}")
    
    def stop_condition_search(self):
        """조건검색 중단"""
        try:
            if self.condition_combo.currentIndex() < 0:
                return
            
            condition_index = self.condition_combo.currentData()
            condition_name = self.condition_combo.currentText().split(' (')[0]
            
            if self.condition_handler.stop_condition_search(condition_index, condition_name):
                self.start_condition_button.setEnabled(True)
                self.stop_condition_button.setEnabled(False)
                self.condition_handler.stop_monitoring()
                
        except Exception as e:
            self.log(f"❌ 조건검색 중단 오류: {e}")
    
    def on_condition_result(self, condition_name, stock_list):
        """조건검색 결과 처리 개선"""
        try:
            current_time = QTime.currentTime().toString()
            
            for stock_code in stock_list:
                stock_name = self.kiwoom.get_master_code_name(stock_code)
                
                # 조건검색 테이블에 추가
                row = self.condition_table.rowCount()
                self.condition_table.insertRow(row)
                
                self.condition_table.setItem(row, 0, QTableWidgetItem(current_time))
                self.condition_table.setItem(row, 1, QTableWidgetItem(condition_name))
                self.condition_table.setItem(row, 2, QTableWidgetItem(stock_name))
                self.condition_table.setItem(row, 3, QTableWidgetItem(stock_code))
                self.condition_table.setItem(row, 4, QTableWidgetItem("편입"))
                
                self.log(f"🎯 조건편입: {stock_name}({stock_code}) - {condition_name}")
                
        except Exception as e:
            self.log(f"❌ 조건검색 결과 처리 오류: {e}")