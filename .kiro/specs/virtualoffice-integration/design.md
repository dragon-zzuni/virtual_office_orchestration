# Design Document

## Overview

이 문서는 offline_agent와 virtualoffice 시스템 간의 실시간 통합 기능에 대한 설계를 정의합니다. 이 통합을 통해 offline_agent는 virtualoffice의 시뮬레이션에서 생성된 메일 및 메시지 데이터를 실시간으로 수집하고 분석할 수 있습니다.

### 핵심 목표

1. **실시간 데이터 수집**: virtualoffice API를 통한 메일/메시지 폴링
2. **시뮬레이션 모니터링**: 틱 진행 상황 및 시뮬레이션 상태 추적
3. **사용자 페르소나 선택**: PM 외 다른 페르소나 관점에서 분석
4. **기존 기능 호환**: 시간 범위 필터 등 기존 UI 기능 유지

### 아키텍처 원칙

- **최소 침습**: 기존 코드 구조를 최대한 유지하고 새로운 모듈로 확장
- **데이터 소스 추상화**: JSON 파일과 API를 동일한 인터페이스로 처리
- **비동기 처리**: 폴링 작업이 UI를 블로킹하지 않도록 백그라운드 스레드 사용
- **오류 복원력**: 네트워크 오류 시 자동 재시도 및 사용자 알림

## Architecture

### 시스템 구성도

```
┌─────────────────────────────────────────────────────────────┐
│                     offline_agent (GUI)                      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Main Window  │  │ TODO Panel   │  │ Email Panel  │      │
│  └──────┬───────┘  └──────────────┘  └──────────────┘      │
│         │                                                     │
│  ┌──────▼──────────────────────────────────────────┐        │
│  │      Data Source Manager (NEW)                  │        │
│  │  - JSON File Source                             │        │
│  │  - VirtualOffice API Source (NEW)               │        │
│  └──────┬──────────────────────────────────────────┘        │
│         │                                                     │
│  ┌──────▼──────────────────────────────────────────┐        │
│  │      SmartAssistant (Core Engine)               │        │
│  │  - collect_messages()                           │        │
│  │  - analyze_messages()                           │        │
│  │  - generate_todo_list()                         │        │
│  └─────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ HTTP REST API
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    virtualoffice (Backend)                   │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Email Server │  │ Chat Server  │  │ Sim Manager  │      │
│  │ Port 8000    │  │ Port 8001    │  │ Port 8015    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 데이터 흐름

1. **초기화 단계**
   - 사용자가 데이터 소스 선택 (JSON 또는 virtualoffice)
   - virtualoffice 선택 시 API 연결 테스트
   - 페르소나 목록 조회 및 사용자 선택

2. **수집 단계**
   - 백그라운드 스레드에서 주기적 폴링 시작
   - Email/Chat API에서 새 데이터 조회
   - 데이터를 기존 포맷으로 변환하여 저장

3. **분석 단계**
   - 기존 분석 파이프라인 사용 (변경 없음)
   - 우선순위 분류, 요약, 액션 추출

4. **표시 단계**
   - UI에 분석 결과 표시
   - 새 데이터 도착 시 시각적 알림


## Components and Interfaces

### 1. VirtualOfficeClient (새 모듈)

**위치**: `offline_agent/src/integrations/virtualoffice_client.py`

**책임**: virtualoffice API와의 통신 담당

```python
class VirtualOfficeClient:
    """virtualoffice API 클라이언트"""
    
    def __init__(self, email_url: str, chat_url: str, sim_url: str):
        self.email_url = email_url
        self.chat_url = chat_url
        self.sim_url = sim_url
        self.session = requests.Session()
        # 재시도 로직 설정
    
    # 연결 테스트
    def test_connection(self) -> Dict[str, bool]:
        """각 서버 연결 상태 확인"""
        pass
    
    # 시뮬레이션 상태
    def get_simulation_status(self) -> SimulationStatus:
        """GET /api/v1/simulation"""
        pass
    
    # 페르소나 목록
    def get_personas(self) -> List[PersonaInfo]:
        """GET /api/v1/people"""
        pass
    
    # 메일 수집
    def get_emails(self, mailbox: str, since_id: Optional[int] = None) -> List[Dict]:
        """GET /mailboxes/{mailbox}/emails?since_id={since_id}"""
        pass
    
    # 메시지 수집
    def get_messages(self, handle: str, since_id: Optional[int] = None) -> List[Dict]:
        """GET /users/{handle}/dms?since_id={since_id}"""
        pass
    
    # 룸 메시지 수집
    def get_room_messages(self, room_slug: str, since_id: Optional[int] = None) -> List[Dict]:
        """GET /rooms/{room_slug}/messages?since_id={since_id}"""
        pass
```

### 2. DataSourceManager (새 모듈)

**위치**: `offline_agent/src/data_sources/manager.py`

**책임**: 데이터 소스 추상화 및 전환 관리

```python
class DataSource(ABC):
    """데이터 소스 추상 인터페이스"""
    
    @abstractmethod
    async def collect_messages(self, options: Dict) -> List[Dict]:
        """메시지 수집"""
        pass
    
    @abstractmethod
    def get_personas(self) -> List[Dict]:
        """페르소나 목록 조회"""
        pass

class JSONDataSource(DataSource):
    """기존 JSON 파일 기반 데이터 소스"""
    
    def __init__(self, dataset_root: Path):
        self.dataset_root = dataset_root
    
    async def collect_messages(self, options: Dict) -> List[Dict]:
        # 기존 SmartAssistant._load_dataset() 로직 사용
        pass

class VirtualOfficeDataSource(DataSource):
    """virtualoffice API 기반 데이터 소스"""
    
    def __init__(self, client: VirtualOfficeClient, selected_persona: str):
        self.client = client
        self.selected_persona = selected_persona
        self.last_email_id = 0
        self.last_message_id = 0
    
    async def collect_messages(self, options: Dict) -> List[Dict]:
        # API에서 새 메일/메시지 조회
        # 기존 포맷으로 변환
        pass

class DataSourceManager:
    """데이터 소스 관리자"""
    
    def __init__(self):
        self.current_source: Optional[DataSource] = None
        self.source_type: str = "json"  # "json" or "virtualoffice"
    
    def set_source(self, source: DataSource, source_type: str):
        """데이터 소스 전환"""
        pass
    
    async def collect_messages(self, options: Dict) -> List[Dict]:
        """현재 소스에서 메시지 수집"""
        if not self.current_source:
            raise RuntimeError("No data source configured")
        return await self.current_source.collect_messages(options)
```

### 3. SimulationMonitor (새 모듈)

**위치**: `offline_agent/src/integrations/simulation_monitor.py`

**책임**: 시뮬레이션 상태 모니터링 및 UI 업데이트

```python
class SimulationMonitor(QObject):
    """시뮬레이션 상태 모니터링"""
    
    # 시그널
    status_updated = pyqtSignal(dict)  # 시뮬레이션 상태 변경
    tick_advanced = pyqtSignal(int)    # 틱 진행
    
    def __init__(self, client: VirtualOfficeClient):
        super().__init__()
        self.client = client
        self.timer = QTimer()
        self.timer.timeout.connect(self._poll_status)
        self.current_tick = 0
    
    def start_monitoring(self, interval_ms: int = 2000):
        """모니터링 시작 (2초 간격)"""
        self.timer.start(interval_ms)
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.timer.stop()
    
    def _poll_status(self):
        """상태 폴링"""
        try:
            status = self.client.get_simulation_status()
            if status.current_tick != self.current_tick:
                self.tick_advanced.emit(status.current_tick)
                self.current_tick = status.current_tick
            self.status_updated.emit(status.to_dict())
        except Exception as e:
            logger.error(f"Status polling failed: {e}")
```

### 4. PollingWorker (새 모듈)

**위치**: `offline_agent/src/integrations/polling_worker.py`

**책임**: 백그라운드에서 주기적 데이터 수집

```python
class PollingWorker(QThread):
    """백그라운드 폴링 워커"""
    
    # 시그널
    new_data_received = pyqtSignal(dict)  # 새 데이터 도착
    error_occurred = pyqtSignal(str)      # 오류 발생
    
    def __init__(self, data_source: VirtualOfficeDataSource):
        super().__init__()
        self.data_source = data_source
        self.polling_interval = 5  # 5초
        self.running = False
    
    def run(self):
        """폴링 루프"""
        self.running = True
        while self.running:
            try:
                # 새 메일/메시지 조회
                new_emails = self.data_source.get_new_emails()
                new_messages = self.data_source.get_new_messages()
                
                if new_emails or new_messages:
                    self.new_data_received.emit({
                        "emails": new_emails,
                        "messages": new_messages,
                        "timestamp": datetime.now().isoformat()
                    })
                
                time.sleep(self.polling_interval)
            except Exception as e:
                self.error_occurred.emit(str(e))
                time.sleep(self.polling_interval * 2)  # 오류 시 대기 시간 증가
    
    def stop(self):
        """폴링 중지"""
        self.running = False
```

### 5. SmartAssistant 확장

**위치**: `offline_agent/main.py` (기존 파일 수정)

**변경 사항**:
- `DataSourceManager` 통합
- `collect_messages()` 메서드를 데이터 소스에 위임

```python
class SmartAssistant:
    def __init__(self, dataset_root: Optional[Path | str] = None):
        # 기존 코드...
        
        # 새로 추가
        self.data_source_manager = DataSourceManager()
        self._setup_default_json_source(dataset_root)
    
    def _setup_default_json_source(self, dataset_root):
        """기본 JSON 데이터 소스 설정"""
        json_source = JSONDataSource(dataset_root or DEFAULT_DATASET_ROOT)
        self.data_source_manager.set_source(json_source, "json")
    
    def set_virtualoffice_source(self, client: VirtualOfficeClient, persona: str):
        """virtualoffice 데이터 소스로 전환"""
        vo_source = VirtualOfficeDataSource(client, persona)
        self.data_source_manager.set_source(vo_source, "virtualoffice")
    
    async def collect_messages(self, **options):
        """데이터 소스에서 메시지 수집 (기존 인터페이스 유지)"""
        messages = await self.data_source_manager.collect_messages(options)
        self.collected_messages = messages
        return messages
```

### 6. GUI 확장

**위치**: `offline_agent/src/ui/main_window.py` (기존 파일 수정)

**새 UI 컴포넌트**:

1. **VirtualOffice 연동 패널** (좌측 패널에 추가)
   - 연결 설정 (URL 입력)
   - 연결 상태 표시
   - 페르소나 선택 드롭다운
   - 시뮬레이션 상태 표시 (틱, 시간, 실행 상태)

2. **데이터 소스 전환 버튼**
   - "로컬 JSON 파일" / "VirtualOffice 실시간" 토글

3. **실시간 알림 표시**
   - 새 메일/메시지 도착 시 배지 표시
   - 틱 진행 시 활동 요약 표시

```python
class SmartAssistantGUI(QMainWindow):
    def __init__(self):
        # 기존 코드...
        
        # 새로 추가
        self.vo_client: Optional[VirtualOfficeClient] = None
        self.sim_monitor: Optional[SimulationMonitor] = None
        self.polling_worker: Optional[PollingWorker] = None
        self.selected_persona: Optional[str] = None
    
    def create_virtualoffice_panel(self):
        """VirtualOffice 연동 패널 생성"""
        group = QGroupBox("🌐 VirtualOffice 연동")
        layout = QVBoxLayout(group)
        
        # 연결 설정
        self.vo_email_url = QLineEdit("http://127.0.0.1:8000")
        self.vo_chat_url = QLineEdit("http://127.0.0.1:8001")
        self.vo_sim_url = QLineEdit("http://127.0.0.1:8015")
        
        # 연결 버튼
        self.vo_connect_btn = QPushButton("연결")
        self.vo_connect_btn.clicked.connect(self.connect_virtualoffice)
        
        # 페르소나 선택
        self.persona_combo = QComboBox()
        self.persona_combo.currentTextChanged.connect(self.on_persona_changed)
        
        # 시뮬레이션 상태
        self.sim_status_label = QLabel("연결되지 않음")
        
        layout.addWidget(QLabel("Email Server:"))
        layout.addWidget(self.vo_email_url)
        layout.addWidget(QLabel("Chat Server:"))
        layout.addWidget(self.vo_chat_url)
        layout.addWidget(QLabel("Sim Manager:"))
        layout.addWidget(self.vo_sim_url)
        layout.addWidget(self.vo_connect_btn)
        layout.addWidget(QLabel("사용자 페르소나:"))
        layout.addWidget(self.persona_combo)
        layout.addWidget(self.sim_status_label)
        
        return group
    
    def connect_virtualoffice(self):
        """VirtualOffice 연결"""
        try:
            # 클라이언트 생성
            self.vo_client = VirtualOfficeClient(
                self.vo_email_url.text(),
                self.vo_chat_url.text(),
                self.vo_sim_url.text()
            )
            
            # 연결 테스트
            status = self.vo_client.test_connection()
            if not all(status.values()):
                raise ConnectionError("일부 서버 연결 실패")
            
            # 페르소나 목록 조회
            personas = self.vo_client.get_personas()
            self.persona_combo.clear()
            for p in personas:
                self.persona_combo.addItem(p["name"], p)
            
            # PM 자동 선택
            pm_index = next((i for i, p in enumerate(personas) 
                           if "pm" in p["name"].lower()), 0)
            self.persona_combo.setCurrentIndex(pm_index)
            
            # 모니터링 시작
            self.sim_monitor = SimulationMonitor(self.vo_client)
            self.sim_monitor.status_updated.connect(self.on_sim_status_updated)
            self.sim_monitor.tick_advanced.connect(self.on_tick_advanced)
            self.sim_monitor.start_monitoring()
            
            QMessageBox.information(self, "성공", "VirtualOffice 연결 성공!")
            
        except Exception as e:
            QMessageBox.critical(self, "오류", f"연결 실패: {e}")
    
    def on_persona_changed(self, persona_name: str):
        """페르소나 변경 시"""
        persona_data = self.persona_combo.currentData()
        if persona_data and self.vo_client:
            self.selected_persona = persona_data["email_address"]
            # 데이터 소스 업데이트
            self.assistant.set_virtualoffice_source(
                self.vo_client, 
                self.selected_persona
            )
    
    def on_sim_status_updated(self, status: dict):
        """시뮬레이션 상태 업데이트"""
        self.sim_status_label.setText(
            f"Tick: {status['current_tick']} | "
            f"Time: {status['sim_time']} | "
            f"Status: {'Running' if status['is_running'] else 'Stopped'}"
        )
    
    def on_tick_advanced(self, tick: int):
        """틱 진행 시"""
        # 시각적 알림 표시
        self.statusBar().showMessage(f"Tick {tick} 진행됨", 3000)
```


## Data Models

### 1. SimulationStatus

```python
@dataclass
class SimulationStatus:
    """시뮬레이션 상태"""
    current_tick: int
    sim_time: str  # ISO 8601 format
    is_running: bool
    auto_tick: bool
    
    def to_dict(self) -> Dict:
        return asdict(self)
```

### 2. PersonaInfo

```python
@dataclass
class PersonaInfo:
    """페르소나 정보"""
    id: int
    name: str
    email_address: str
    chat_handle: str
    role: str
    
    @classmethod
    def from_api_response(cls, data: Dict) -> "PersonaInfo":
        return cls(
            id=data["id"],
            name=data["name"],
            email_address=data["email_address"],
            chat_handle=data["chat_handle"],
            role=data.get("role", "Unknown")
        )
```

### 3. VirtualOfficeConfig

```python
@dataclass
class VirtualOfficeConfig:
    """VirtualOffice 연동 설정"""
    email_url: str = "http://127.0.0.1:8000"
    chat_url: str = "http://127.0.0.1:8001"
    sim_url: str = "http://127.0.0.1:8015"
    polling_interval: int = 5  # 초
    selected_persona: Optional[str] = None
    
    def save_to_file(self, path: Path):
        """설정 파일 저장"""
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2)
    
    @classmethod
    def load_from_file(cls, path: Path) -> "VirtualOfficeConfig":
        """설정 파일 로드"""
        with open(path, "r") as f:
            data = json.load(f)
        return cls(**data)
```

### 4. 데이터 변환 로직

**중요**: virtualoffice의 simulation_output 폴더에 생성되는 JSON 파일들이 offline_agent가 사용하는 형식입니다. API 응답도 동일한 구조를 따르므로, 변환 로직은 최소화됩니다.

**simulation_output 구조**:
```
simulation_output/
└── multi_project_8week_ko/
    ├── team_personas.json       # 페르소나 정보
    ├── email_communications.json # 메일 데이터
    ├── chat_communications.json  # 채팅 데이터
    ├── final_state.json         # 최종 상태
    └── api_errors.json          # API 오류 로그
```

virtualoffice API 응답을 offline_agent 내부 포맷으로 변환:

```python
def convert_email_to_internal_format(email: Dict, persona_map: Dict) -> Dict:
    """Email API 응답을 내부 포맷으로 변환
    
    Args:
        email: virtualoffice API 응답 (simulation_output과 동일 형식)
        {
            "id": 1079,
            "sender": "dev.1@multiproject.dev",
            "to": ["pm.1@multiproject.dev"],
            "cc": ["devops.1@multiproject.dev"],
            "bcc": [],
            "subject": "업데이트: 이준호",
            "body": "오늘 작업 결과 | 오늘 진행한 API 개발과 내부 테스트 결과를 공유합니다.",
            "thread_id": null,
            "sent_at": "2025-11-26T06:29:27.073636Z"
        }
        persona_map: {email_address -> persona_info}
    
    Returns:
        offline_agent 내부 포맷 (main.py의 _build_email_messages와 동일)
        {
            "msg_id": "email_1079_dev.1@multiproject.dev",
            "sender": "이준호",  # persona의 name
            "sender_email": "dev.1@multiproject.dev",
            "sender_handle": "dev",  # persona의 chat_handle
            "subject": "업데이트: 이준호",
            "body": "오늘 작업 결과 | ...",
            "content": "오늘 작업 결과 | ...",
            "date": "2025-11-26T06:29:27.073636Z",
            "type": "email",
            "platform": "email",
            "mailbox": "pm.1@multiproject.dev",  # 수신자 메일박스
            "recipients": ["pm.1@multiproject.dev"],
            "cc": ["devops.1@multiproject.dev"],
            "bcc": [],
            "thread_id": null,
            "recipient_type": "to",  # PM이 to/cc/bcc 중 어디에 있는지
            "is_read": True,
            "metadata": {
                "mailbox": "pm.1@multiproject.dev",
                "email_id": 1079,
                "persona": {...}  # sender의 persona 정보
            }
        }
    """
    sender_email = email["sender"]
    sender_persona = persona_map.get(sender_email, {})
    sender_name = sender_persona.get("name", sender_email)
    
    return {
        "msg_id": f"email_{email['id']}",
        "sender": sender_name,
        "sender_email": sender_email,
        "sender_handle": sender_persona.get("chat_handle"),
        "subject": email["subject"],
        "body": email["body"],
        "content": email["body"],
        "date": email["sent_at"],
        "type": "email",
        "platform": "email",
        "recipients": email["to"],
        "cc": email["cc"],
        "bcc": email["bcc"],
        "thread_id": email.get("thread_id"),
        "recipient_type": "to",  # 기본값, 실제로는 PM이 어디에 있는지 확인 필요
        "is_read": False,
        "metadata": {
            "email_id": email["id"],
            "persona": sender_persona,
        }
    }

def convert_message_to_internal_format(message: Dict, persona_map: Dict) -> Dict:
    """Chat API 응답을 내부 포맷으로 변환
    
    Args:
        message: virtualoffice API 응답 (simulation_output과 동일 형식)
        {
            "id": 26,
            "room_slug": "dm:designer:dev",
            "sender": "designer",
            "body": "이준호님, 09:00 - 09:15 진행 중입니다.",
            "sent_at": "2025-10-20T22:02:27.073636Z"
        }
        persona_map: {chat_handle -> persona_info}
    
    Returns:
        offline_agent 내부 포맷 (main.py의 _build_chat_messages와 동일)
        {
            "msg_id": "chat_dm:designer:dev_26",
            "sender": "김민준",  # persona의 name
            "sender_handle": "designer",
            "sender_email": "designer.1@multiproject.dev",  # persona의 email_address
            "subject": "",
            "body": "이준호님, 09:00 - 09:15 진행 중입니다.",
            "content": "이준호님, 09:00 - 09:15 진행 중입니다.",
            "date": "2025-10-20T22:02:27.073636Z",
            "type": "messenger",
            "platform": "dm:designer:dev",  # room_slug
            "room_slug": "dm:designer:dev",
            "recipient_type": "to",
            "is_read": True,
            "metadata": {
                "chat_id": 26,
                "raw_sender": "designer",
                "persona": {...},  # sender의 persona 정보
                "room_slug": "dm:designer:dev"
            }
        }
    """
    sender_handle = message["sender"]
    sender_persona = persona_map.get(sender_handle, {})
    sender_name = sender_persona.get("name", sender_handle)
    
    return {
        "msg_id": f"chat_{message['id']}",
        "sender": sender_name,
        "sender_handle": sender_handle,
        "sender_email": sender_persona.get("email_address"),
        "subject": "",
        "body": message["body"],
        "content": message["body"],
        "date": message["sent_at"],
        "type": "messenger",
        "platform": message["room_slug"],
        "room_slug": message["room_slug"],
        "recipient_type": "to",
        "is_read": False,
        "metadata": {
            "chat_id": message["id"],
            "persona": sender_persona,
            "room_slug": message["room_slug"],
        }
    }
```

## Error Handling

### 1. 연결 오류 처리

```python
class ConnectionManager:
    """연결 관리 및 재시도 로직"""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.consecutive_failures = 0
    
    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """재시도 로직이 적용된 함수 실행"""
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                self.consecutive_failures = 0  # 성공 시 리셋
                return result
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}/{self.max_retries}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.backoff_factor ** attempt)
                else:
                    raise
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error on attempt {attempt + 1}/{self.max_retries}")
                self.consecutive_failures += 1
                if attempt < self.max_retries - 1:
                    time.sleep(self.backoff_factor ** attempt)
                else:
                    raise
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise
        
        raise RuntimeError("Max retries exceeded")
```

### 2. 데이터 검증

```python
def validate_email_response(data: Dict) -> bool:
    """Email API 응답 검증"""
    required_fields = ["id", "sender", "subject", "body", "sent_at"]
    return all(field in data for field in required_fields)

def validate_message_response(data: Dict) -> bool:
    """Chat API 응답 검증"""
    required_fields = ["id", "room_slug", "sender", "body", "sent_at"]
    return all(field in data for field in required_fields)
```

### 3. 오류 알림

```python
class ErrorNotifier:
    """오류 알림 관리"""
    
    def __init__(self, parent_widget: QWidget):
        self.parent = parent_widget
        self.error_count = 0
        self.last_error_time = None
    
    def notify_connection_error(self, error: Exception):
        """연결 오류 알림"""
        self.error_count += 1
        current_time = datetime.now()
        
        # 1분 이내 중복 알림 방지
        if self.last_error_time and (current_time - self.last_error_time).seconds < 60:
            return
        
        self.last_error_time = current_time
        
        msg = QMessageBox(self.parent)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("연결 오류")
        msg.setText(f"VirtualOffice 서버 연결 실패 ({self.error_count}회)")
        msg.setInformativeText(str(error))
        msg.setStandardButtons(QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Cancel)
        
        if msg.exec() == QMessageBox.StandardButton.Retry:
            return True  # 재시도
        else:
            return False  # 취소
```

## Testing Strategy

### 1. 단위 테스트

**테스트 대상**:
- `VirtualOfficeClient`: API 호출 및 응답 파싱
- `DataSourceManager`: 데이터 소스 전환 로직
- 데이터 변환 함수: API 응답 → 내부 포맷

**테스트 방법**:
- Mock 서버 사용 (responses 라이브러리)
- 다양한 API 응답 시나리오 테스트
- 오류 케이스 테스트 (타임아웃, 잘못된 응답 등)

```python
# 예시
def test_convert_email_to_internal_format():
    email = {
        "id": 123,
        "sender": "dev@vdos.local",
        "to": ["pm@vdos.local"],
        "cc": [],
        "bcc": [],
        "subject": "Test",
        "body": "Test body",
        "sent_at": "2025-01-15T10:00:00+00:00"
    }
    persona_map = {
        "dev@vdos.local": {"name": "Developer", "chat_handle": "dev"}
    }
    
    result = convert_email_to_internal_format(email, persona_map)
    
    assert result["msg_id"] == "email_123"
    assert result["sender"] == "Developer"
    assert result["type"] == "email"
```

### 2. 통합 테스트

**테스트 시나리오**:
1. VirtualOffice 서버 시작 → offline_agent 연결 → 데이터 수집
2. 시뮬레이션 진행 → 새 메일/메시지 생성 → 실시간 수집 확인
3. 페르소나 전환 → 필터링 결과 확인
4. 시간 범위 필터 적용 → 결과 확인

**테스트 환경**:
- Docker Compose로 virtualoffice 서버 실행
- 테스트 데이터 사전 생성
- 자동화된 시나리오 실행

### 3. UI 테스트

**테스트 항목**:
- 연결 설정 UI 동작
- 페르소나 선택 드롭다운
- 시뮬레이션 상태 표시
- 새 데이터 알림 표시
- 데이터 소스 전환

**테스트 방법**:
- PyQt6 테스트 프레임워크 사용
- 수동 테스트 체크리스트

### 4. 성능 테스트

**테스트 목표**:
- 1000개 메시지 수집 시 응답 시간 < 5초
- 메모리 사용량 < 500MB
- 폴링 간격 준수 (5초 ± 0.5초)

**테스트 방법**:
- 대량 데이터 생성 스크립트
- 프로파일링 도구 사용 (cProfile, memory_profiler)

## Performance Considerations

### 1. 폴링 최적화

- **증분 조회**: `since_id` 파라미터 사용하여 새 데이터만 조회
- **배치 처리**: 여러 API 호출을 병렬로 실행 (asyncio 사용)
- **캐싱**: 페르소나 정보 등 정적 데이터 캐싱

```python
async def collect_new_data_batch(self):
    """병렬로 새 데이터 수집"""
    tasks = [
        self.get_new_emails(),
        self.get_new_messages(),
        self.get_new_room_messages()
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### 2. 메모리 관리

- **데이터 제한**: 최대 10,000개 메시지 유지
- **자동 정리**: 오래된 데이터 자동 삭제
- **페이징**: 대량 데이터 조회 시 페이징 사용

```python
def cleanup_old_messages(self, max_count: int = 10000):
    """오래된 메시지 정리"""
    if len(self.collected_messages) > max_count:
        # 날짜 기준 정렬 후 최신 max_count개만 유지
        self.collected_messages.sort(key=lambda m: m["date"], reverse=True)
        self.collected_messages = self.collected_messages[:max_count]
```

### 3. UI 반응성

- **백그라운드 처리**: 모든 네트워크 작업을 별도 스레드에서 실행
- **진행 표시**: 장시간 작업 시 프로그레스 바 표시
- **비동기 업데이트**: 데이터 도착 시 점진적 UI 업데이트

## Security Considerations

### 1. 인증 (향후 확장)

현재는 로컬 네트워크 전용이지만, 향후 인증 추가 가능:

```python
class VirtualOfficeClient:
    def __init__(self, ..., api_key: Optional[str] = None):
        self.api_key = api_key
        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"
```

### 2. 데이터 보안

- **민감 정보 제외**: 로그에 이메일 내용 전체 출력 금지
- **설정 파일 보호**: API URL 등 설정 파일 권한 제한

### 3. 입력 검증

- **URL 검증**: 사용자 입력 URL 형식 검증
- **응답 검증**: API 응답 데이터 타입 및 필수 필드 검증

## Deployment Considerations

### 1. 설정 파일

**위치**: `data/virtualoffice_config.json`

```json
{
  "email_url": "http://127.0.0.1:8000",
  "chat_url": "http://127.0.0.1:8001",
  "sim_url": "http://127.0.0.1:8015",
  "polling_interval": 5,
  "selected_persona": "pm@vdos.local"
}
```

### 2. 환경 변수

```bash
# VirtualOffice 서버 URL (선택적)
VDOS_EMAIL_URL=http://127.0.0.1:8000
VDOS_CHAT_URL=http://127.0.0.1:8001
VDOS_SIM_URL=http://127.0.0.1:8015

# 폴링 간격 (초)
VDOS_POLLING_INTERVAL=5
```

### 3. 의존성 추가

`requirements.txt`에 추가:
```
requests>=2.31.0
urllib3>=2.0.0
```

### 4. 문서 업데이트

- README.md: VirtualOffice 연동 사용법 추가
- TROUBLESHOOTING.md: 연결 오류 해결 방법 추가
- CHANGELOG.md: 새 기능 추가 기록

## Migration Path

기존 사용자를 위한 마이그레이션 전략:

1. **기본 동작 유지**: 기존 JSON 파일 기반 동작은 그대로 유지
2. **선택적 활성화**: VirtualOffice 연동은 사용자가 명시적으로 활성화
3. **설정 마이그레이션**: 기존 설정 파일 자동 변환 (필요 시)
4. **문서 제공**: 새 기능 사용법 상세 문서 제공

## Future Enhancements

1. **양방향 통신**: offline_agent에서 virtualoffice로 메일/메시지 전송
2. **실시간 알림**: WebSocket 기반 실시간 푸시 알림
3. **다중 시뮬레이션**: 여러 시뮬레이션 동시 모니터링
4. **고급 필터링**: 프로젝트별, 우선순위별 필터링
5. **데이터 내보내기**: 수집된 데이터를 JSON 파일로 저장


## API Endpoint Mapping

virtualoffice API와 simulation_output 파일의 관계:

### 1. Personas (team_personas.json)

**API**: `GET /api/v1/people`

**응답 형식**:
```json
[
  {
    "id": 1,
    "name": "이민주",
    "role": "프로젝트 매니저",
    "email_address": "pm.1@multiproject.dev",
    "chat_handle": "pm",
    "is_department_head": true,
    "skills": ["Agile", "Scrum", ...],
    "personality": ["Helpful"],
    ...
  }
]
```

**사용처**: 페르소나 선택 드롭다운, 이름 매핑

### 2. Emails (email_communications.json)

**API**: `GET /mailboxes/{address}/emails?since_id={last_id}`

**응답 형식**:
```json
[
  {
    "id": 1079,
    "sender": "dev.1@multiproject.dev",
    "to": ["pm.1@multiproject.dev"],
    "cc": ["devops.1@multiproject.dev"],
    "bcc": [],
    "subject": "업데이트: 이준호",
    "body": "오늘 작업 결과 | ...",
    "thread_id": null,
    "sent_at": "2025-11-26T06:29:27.073636Z"
  }
]
```

**폴링 전략**:
- `since_id` 파라미터로 증분 조회
- 마지막 조회한 email ID 저장
- 5초마다 폴링

### 3. Chat Messages (chat_communications.json)

**API 옵션 1**: `GET /users/{handle}/dms?since_id={last_id}`
- 사용자의 모든 DM 메시지 조회

**API 옵션 2**: `GET /rooms/{room_slug}/messages?since_id={last_id}`
- 특정 룸의 메시지 조회

**응답 형식**:
```json
[
  {
    "id": 26,
    "room_slug": "dm:designer:dev",
    "sender": "designer",
    "body": "이준호님, 09:00 - 09:15 진행 중입니다.",
    "sent_at": "2025-10-20T22:02:27.073636Z"
  }
]
```

**폴링 전략**:
- PM의 chat_handle로 `/users/{pm_handle}/dms` 조회
- `since_id` 파라미터로 증분 조회
- 5초마다 폴링

### 4. Simulation Status

**API**: `GET /api/v1/simulation`

**응답 형식**:
```json
{
  "current_tick": 1920,
  "sim_time": "2025-11-26T06:29:27.073636Z",
  "is_running": true,
  "auto_tick": true
}
```

**폴링 전략**:
- 2초마다 폴링
- 틱 변경 감지 시 UI 업데이트

## Data Collection Flow

### 초기 수집 (Full Sync)

1. **페르소나 조회**
   ```python
   personas = client.get_personas()
   persona_by_email = {p["email_address"]: p for p in personas}
   persona_by_handle = {p["chat_handle"]: p for p in personas}
   ```

2. **선택된 페르소나의 메일박스 조회**
   ```python
   selected_persona = "pm.1@multiproject.dev"
   emails = client.get_emails(selected_persona, since_id=None)
   # 모든 메일 조회 (since_id=None)
   ```

3. **선택된 페르소나의 DM 조회**
   ```python
   selected_handle = "pm"
   messages = client.get_messages(selected_handle, since_id=None)
   # 모든 DM 조회 (since_id=None)
   ```

4. **데이터 변환 및 저장**
   ```python
   internal_emails = [convert_email_to_internal_format(e, persona_by_email) 
                      for e in emails]
   internal_messages = [convert_message_to_internal_format(m, persona_by_handle) 
                        for m in messages]
   all_messages = internal_emails + internal_messages
   ```

### 증분 수집 (Incremental Sync)

1. **마지막 ID 추적**
   ```python
   last_email_id = max([e["id"] for e in emails]) if emails else 0
   last_message_id = max([m["id"] for m in messages]) if messages else 0
   ```

2. **새 데이터 폴링 (5초마다)**
   ```python
   new_emails = client.get_emails(selected_persona, since_id=last_email_id)
   new_messages = client.get_messages(selected_handle, since_id=last_message_id)
   
   if new_emails:
       last_email_id = max([e["id"] for e in new_emails])
       # UI 업데이트 및 분석
   
   if new_messages:
       last_message_id = max([m["id"] for m in new_messages])
       # UI 업데이트 및 분석
   ```

3. **틱 변경 감지**
   ```python
   current_status = client.get_simulation_status()
   if current_status.current_tick != last_tick:
       # 틱 진행 알림
       emit_tick_notification(current_status.current_tick)
       last_tick = current_status.current_tick
   ```

## Compatibility Notes

### 기존 코드와의 호환성

1. **SmartAssistant.collect_messages()**
   - 기존 인터페이스 유지
   - 내부적으로 DataSourceManager에 위임
   - 반환 형식 동일 (List[Dict])

2. **시간 범위 필터**
   - 기존 TimeRangeSelector 그대로 사용
   - API에서 조회한 데이터도 동일한 필터 적용
   - `date` 필드 기준 필터링

3. **페르소나 필터링**
   - 기존 PM 필터링 로직 재사용
   - `_is_pm_recipient()` 함수 그대로 사용
   - `recipient_type` 필드 설정

4. **데이터 구조**
   - simulation_output JSON 파일과 동일한 구조
   - 기존 파싱 로직 재사용 가능
   - 추가 변환 최소화

### 새로운 기능

1. **실시간 업데이트**
   - 폴링 워커를 통한 자동 수집
   - 새 데이터 도착 시 시각적 알림

2. **페르소나 전환**
   - UI에서 페르소나 선택 가능
   - 선택된 페르소나 관점에서 데이터 필터링

3. **시뮬레이션 모니터링**
   - 틱 진행 상황 표시
   - 시뮬레이션 시간 표시
   - 실행 상태 표시

## Implementation Priority

### Phase 1: 기본 연동 (MVP)
1. VirtualOfficeClient 구현
2. 연결 테스트 및 페르소나 조회
3. 메일/메시지 수집 (Full Sync)
4. 데이터 변환 및 표시

### Phase 2: 실시간 기능
1. PollingWorker 구현
2. 증분 수집 (Incremental Sync)
3. 새 데이터 알림
4. SimulationMonitor 구현

### Phase 3: UI 개선
1. VirtualOffice 연동 패널
2. 페르소나 선택 드롭다운
3. 시뮬레이션 상태 표시
4. 틱 진행 알림

### Phase 4: 고급 기능
1. 오류 처리 및 재시도
2. 성능 최적화
3. 설정 저장/로드
4. 문서 및 테스트
