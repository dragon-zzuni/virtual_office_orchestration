# Virtual Office Orchestration

**VirtualOffice + Offline Agent Integration**: Real-time workplace communication simulation and analysis system

## 🎯 프로젝트 개요

이 프로젝트는 두 개의 주요 컴포넌트로 구성된 통합 시스템입니다:

1. **VirtualOffice (VDOS)**: 가상 직장 환경 시뮬레이터
   - AI 기반 페르소나 시스템
   - 이메일 및 채팅 서버
   - 시뮬레이션 관리자

2. **Offline Agent (Smart Assistant)**: 커뮤니케이션 분석 도구
   - LLM 기반 메시지 분석
   - TODO 자동 추출
   - 실시간 VirtualOffice 연동

## 🚀 주요 기능

### VirtualOffice
- ✅ FastAPI 기반 REST API (Email, Chat, Simulation Manager)
- ✅ GPT-4o 기반 AI 페르소나 생성
- ✅ 틱 기반 시뮬레이션 엔진
- ✅ PySide6 GUI 대시보드
- ✅ 다중 프로젝트 시나리오 지원

### Offline Agent
- ✅ PyQt6 기반 데스크톱 GUI
- ✅ LLM 기반 메시지 요약 및 우선순위 분석
- ✅ TODO 자동 추출 및 관리
- ✅ VirtualOffice 실시간 연동
- ✅ 폴링 워커 및 시뮬레이션 모니터
- ✅ 시각적 알림 시스템 (NEW 배지, 틱 히스토리)
- ✅ 설정 자동 저장/로드

## 📦 설치 방법

### 사전 요구사항
- Python 3.10+ (VirtualOffice는 3.11+ 권장)
- OpenAI API Key 또는 Azure OpenAI 설정

### 1. VirtualOffice 설치

```bash
cd virtualoffice
pip install -r requirements.txt

# .env 파일 생성 및 API 키 설정
cp .env.example .env
# OPENAI_API_KEY 설정

# GUI 실행
briefcase dev
```

### 2. Offline Agent 설치

```bash
cd offline_agent
pip install -r requirements.txt

# .env 파일 생성 및 설정
cp .env.example .env
# LLM_PROVIDER, API 키 등 설정

# GUI 실행
python run_gui.py
```

## 🎮 사용 방법

### 1. VirtualOffice 시뮬레이션 시작

```bash
cd virtualoffice
briefcase dev
```

GUI에서:
1. Scenario 선택 (예: Multi-Project Team)
2. "Initialize" 버튼 클릭
3. "Start" 버튼 클릭
4. Auto Tick 활성화

### 2. Offline Agent 연동

```bash
cd offline_agent
python run_gui.py
```

GUI에서:
1. "🌐 VirtualOffice 연동" 섹션으로 이동
2. 서버 URL 입력 (자동으로 로드됨)
3. "🔌 연결 테스트" 버튼 클릭
4. 페르소나 선택
5. "메시지 수집 시작" 버튼 클릭

## 📚 문서

### VirtualOffice
- [Architecture](virtualoffice/docs/architecture.md)
- [Getting Started](virtualoffice/docs/GETTING_STARTED.md)
- [API Documentation](virtualoffice/docs/api/)

### Offline Agent
- [VirtualOffice 연동 테스트](offline_agent/docs/VIRTUALOFFICE_TESTING.md)
- [실시간 기능 테스트](offline_agent/docs/REALTIME_TESTING.md)
- [설정 관리](offline_agent/docs/VIRTUALOFFICE_CONFIG.md)
- [문제 해결](offline_agent/TROUBLESHOOTING.md)

## 🏗️ 프로젝트 구조

```
virtual_office_orchestration/
├── virtualoffice/          # VirtualOffice 시뮬레이터
│   ├── src/virtualoffice/
│   │   ├── servers/       # Email & Chat 서버
│   │   ├── sim_manager/   # 시뮬레이션 엔진
│   │   └── virtualWorkers/ # AI 페르소나
│   └── docs/
│
├── offline_agent/         # Offline Agent 분석 도구
│   ├── src/
│   │   ├── ui/           # PyQt6 GUI
│   │   ├── integrations/ # VirtualOffice 연동
│   │   └── data_sources/ # 데이터 소스 관리
│   ├── docs/
│   └── test/
│
└── .kiro/                # Kiro IDE 설정
    ├── specs/            # 프로젝트 스펙
    └── steering/         # 개발 가이드
```

## 🔧 기술 스택

### VirtualOffice
- **Backend**: FastAPI, Uvicorn
- **GUI**: PySide6
- **Database**: SQLite
- **AI**: OpenAI GPT-4o
- **Testing**: Pytest

### Offline Agent
- **GUI**: PyQt6
- **LLM**: OpenAI / Azure OpenAI / OpenRouter
- **Database**: SQLite
- **NLP**: Transformers, Torch
- **Testing**: Pytest

## 🎯 주요 통합 기능

### Phase 1: 기본 연동 ✅
- VirtualOfficeClient 구현
- 데이터 모델 정의
- 데이터 변환 함수
- DataSourceManager 구현
- GUI 연동 패널

### Phase 2: 실시간 기능 ✅
- PollingWorker (백그라운드 데이터 수집)
- SimulationMonitor (시뮬레이션 상태 모니터링)
- GUI 실시간 업데이트

### Phase 3: UI 개선 ✅
- NEW 배지 위젯
- 틱 히스토리 다이얼로그
- 시뮬레이션 상태 패널

### Phase 4: 고급 기능 ✅
- 오류 처리 및 복구 (ConnectionManager, ErrorNotifier)
- 성능 최적화 (병렬 처리, 메모리 관리, 캐싱)
- 설정 관리 (자동 저장/로드, 환경 변수 지원)
- 완전한 문서화

## 🧪 테스트

### VirtualOffice
```bash
cd virtualoffice
pytest
pytest --cov=. --cov-report=html
```

### Offline Agent
```bash
cd offline_agent

# 단위 테스트
pytest test/

# 통합 테스트
python test_virtualoffice_connection.py

# 실시간 기능 테스트
python run_realtime_tests.py
python run_realtime_tests.py --full
python run_realtime_tests.py --gui
```

## 📝 환경 변수

### VirtualOffice (.env)
```bash
OPENAI_API_KEY=your_key_here
VDOS_EMAIL_PORT=8002
VDOS_CHAT_PORT=8001
VDOS_SIM_PORT=8015
```

### Offline Agent (.env)
```bash
# LLM 설정
LLM_PROVIDER=azure  # or openai, openrouter
AZURE_OPENAI_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# VirtualOffice 연동
VDOS_EMAIL_URL=http://127.0.0.1:8002
VDOS_CHAT_URL=http://127.0.0.1:8001
VDOS_SIM_URL=http://127.0.0.1:8015
```

## 🤝 기여

기여는 언제나 환영합니다! 다음 단계를 따라주세요:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 👥 개발자

- **dragon-zzuni** - Initial work

## 🙏 감사의 말

- OpenAI GPT-4o for AI persona generation
- FastAPI & PyQt6 communities
- All contributors and testers

## 📞 문의

- GitHub Issues: [Issues](https://github.com/dragon-zzuni/virtual_office_orchestration/issues)
- Email: [Your Email]

---

**Made with ❤️ by dragon-zzuni**
