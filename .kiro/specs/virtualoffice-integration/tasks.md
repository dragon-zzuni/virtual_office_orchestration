# Implementation Plan

## Phase 1: 기본 연동 (MVP)

- [x] 1. VirtualOfficeClient 모듈 구현




  - VirtualOffice API와 통신하는 클라이언트 클래스 작성
  - HTTP 세션 설정 및 재시도 로직 구현
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 1.1 VirtualOfficeClient 기본 구조 생성


  - `offline_agent/src/integrations/virtualoffice_client.py` 파일 생성
  - 클래스 초기화 메서드 구현 (email_url, chat_url, sim_url 파라미터)
  - requests.Session 설정 및 재시도 로직 추가 (Retry 사용)
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 1.2 연결 테스트 메서드 구현


  - `test_connection()` 메서드 작성
  - 각 서버 (Email, Chat, Sim Manager)에 헬스 체크 요청
  - 연결 상태를 Dict[str, bool]로 반환
  - _Requirements: 1.4, 1.5_

- [x] 1.3 페르소나 조회 메서드 구현


  - `get_personas()` 메서드 작성
  - `GET /api/v1/people` 엔드포인트 호출
  - PersonaInfo 객체 리스트로 변환하여 반환
  - _Requirements: 5.1_

- [x] 1.4 메일 수집 메서드 구현


  - `get_emails(mailbox, since_id)` 메서드 작성
  - `GET /mailboxes/{mailbox}/emails?since_id={since_id}` 엔드포인트 호출
  - 응답 검증 및 오류 처리
  - _Requirements: 2.1, 2.3_



- [x] 1.5 메시지 수집 메서드 구현





  - `get_messages(handle, since_id)` 메서드 작성
  - `GET /users/{handle}/dms?since_id={since_id}` 엔드포인트 호출


  - 응답 검증 및 오류 처리
  - _Requirements: 2.2, 2.4_

- [x] 1.6 시뮬레이션 상태 조회 메서드 구현





  - `get_simulation_status()` 메서드 작성
  - `GET /api/v1/simulation` 엔드포인트 호출
  - SimulationStatus 객체로 변환하여 반환
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 2. 데이터 모델 정의




  - SimulationStatus, PersonaInfo, VirtualOfficeConfig 데이터 클래스 작성
  - 데이터 검증 및 변환 로직 구현
  - _Requirements: 5.1, 7.2, 7.3_

- [x] 2.1 SimulationStatus 데이터 클래스 작성


  - `offline_agent/src/integrations/models.py` 파일 생성
  - SimulationStatus 데이터 클래스 정의 (current_tick, sim_time, is_running, auto_tick)
  - `to_dict()` 메서드 구현
  - _Requirements: 3.2, 3.3, 3.4_

- [x] 2.2 PersonaInfo 데이터 클래스 작성


  - PersonaInfo 데이터 클래스 정의 (id, name, email_address, chat_handle, role)
  - `from_api_response()` 클래스 메서드 구현
  - _Requirements: 5.1, 5.2_

- [x] 2.3 VirtualOfficeConfig 데이터 클래스 작성


  - VirtualOfficeConfig 데이터 클래스 정의 (email_url, chat_url, sim_url, polling_interval, selected_persona)
  - `save_to_file()` 및 `load_from_file()` 메서드 구현
  - _Requirements: 7.2, 7.3, 7.4_

- [x] 3. 데이터 변환 함수 구현




  - virtualoffice API 응답을 offline_agent 내부 포맷으로 변환하는 함수 작성
  - 페르소나 매핑 로직 구현
  - _Requirements: 2.3, 2.4, 5.3_

- [x] 3.1 Email 변환 함수 작성


  - `offline_agent/src/integrations/converters.py` 파일 생성
  - `convert_email_to_internal_format(email, persona_map)` 함수 구현
  - simulation_output/email_communications.json 형식을 main.py의 _build_email_messages 형식으로 변환
  - recipient_type 필드 설정 (to/cc/bcc 판별)
  - _Requirements: 2.3, 5.3_


- [x] 3.2 Chat Message 변환 함수 작성





  - `convert_message_to_internal_format(message, persona_map)` 함수 구현
  - simulation_output/chat_communications.json 형식을 main.py의 _build_chat_messages 형식으로 변환
  - room_slug 파싱 및 recipient_type 설정
  - _Requirements: 2.4, 5.3_


- [x] 3.3 페르소나 매핑 헬퍼 함수 작성





  - `build_persona_maps(personas)` 함수 구현
  - email_address → persona 및 chat_handle → persona 매핑 딕셔너리 생성
  - _Requirements: 5.1, 5.2_

- [x] 4. DataSourceManager 구현




  - 데이터 소스 추상화 인터페이스 및 구현체 작성
  - JSON 파일 소스와 VirtualOffice API 소스 구현
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 4.1 DataSource 추상 인터페이스 정의


  - `offline_agent/src/data_sources/manager.py` 파일 생성
  - DataSource 추상 베이스 클래스 정의 (ABC 사용)
  - `collect_messages()` 및 `get_personas()` 추상 메서드 선언
  - _Requirements: 8.1, 8.2_

- [x] 4.2 JSONDataSource 구현


  - JSONDataSource 클래스 구현 (기존 SmartAssistant._load_dataset 로직 재사용)
  - `collect_messages()` 메서드에서 JSON 파일 로드 및 파싱
  - `get_personas()` 메서드에서 team_personas.json 로드
  - _Requirements: 8.2_

- [x] 4.3 VirtualOfficeDataSource 구현


  - VirtualOfficeDataSource 클래스 구현
  - VirtualOfficeClient 인스턴스 및 선택된 페르소나 저장
  - `collect_messages()` 메서드에서 API 호출 및 데이터 변환
  - last_email_id 및 last_message_id 추적
  - _Requirements: 2.1, 2.2, 8.3_

- [x] 4.4 DataSourceManager 구현

  - DataSourceManager 클래스 구현
  - `set_source()` 메서드로 데이터 소스 전환
  - `collect_messages()` 메서드에서 현재 소스에 위임
  - _Requirements: 8.1, 8.4, 8.5_

- [x] 5. SmartAssistant 확장




  - SmartAssistant 클래스에 DataSourceManager 통합
  - 기존 인터페이스 유지하면서 데이터 소스 추상화
  - _Requirements: 8.2, 8.3, 8.4_

- [x] 5.1 SmartAssistant에 DataSourceManager 추가


  - `main.py` 파일 수정
  - `__init__()` 메서드에 DataSourceManager 인스턴스 생성
  - `_setup_default_json_source()` 메서드 구현 (기본 JSON 소스 설정)
  - _Requirements: 8.2_

- [x] 5.2 VirtualOffice 소스 전환 메서드 추가


  - `set_virtualoffice_source(client, persona)` 메서드 구현
  - VirtualOfficeDataSource 생성 및 DataSourceManager에 설정
  - _Requirements: 8.3_


- [x] 5.3 collect_messages() 메서드 수정

  - 기존 `collect_messages()` 메서드를 DataSourceManager에 위임하도록 수정
  - 기존 인터페이스 및 반환 형식 유지
  - _Requirements: 8.4_

- [x] 6. 기본 GUI 연동 패널 구현



  - VirtualOffice 연동 설정 UI 추가
  - 연결 테스트 및 페르소나 선택 기능 구현
  - _Requirements: 7.1, 7.2, 5.2, 5.3, 5.4_

- [x] 6.1 VirtualOffice 연동 패널 UI 생성


  - `main_window.py` 파일 수정
  - `create_virtualoffice_panel()` 메서드 구현
  - Email/Chat/Sim Manager URL 입력 필드 추가
  - 연결 버튼 및 상태 표시 레이블 추가
  - _Requirements: 7.1, 7.2_

- [x] 6.2 페르소나 선택 드롭다운 추가


  - QComboBox 위젯 추가
  - 페르소나 목록 로드 및 표시
  - PM 페르소나 자동 선택 로직 구현
  - _Requirements: 5.2, 5.4, 5.5_

- [x] 6.3 연결 버튼 이벤트 핸들러 구현


  - `connect_virtualoffice()` 메서드 구현
  - VirtualOfficeClient 생성 및 연결 테스트
  - 페르소나 목록 조회 및 드롭다운 업데이트
  - 성공/실패 메시지 표시
  - _Requirements: 1.4, 1.5, 5.1_

- [x] 6.4 페르소나 변경 이벤트 핸들러 구현

  - `on_persona_changed()` 메서드 구현
  - 선택된 페르소나로 데이터 소스 업데이트
  - SmartAssistant.set_virtualoffice_source() 호출
  - _Requirements: 5.3_

- [x] 6.5 데이터 소스 전환 UI 추가

  - "로컬 JSON 파일" / "VirtualOffice 실시간" 라디오 버튼 또는 토글 추가
  - 데이터 소스 전환 이벤트 핸들러 구현
  - 현재 데이터 소스 표시
  - _Requirements: 8.1, 8.5_

- [x] 7. 기본 연동 테스트





  - VirtualOffice 서버 실행 후 연결 테스트
  - 메일/메시지 수집 및 표시 확인
  - 페르소나 전환 테스트
  - _Requirements: 모든 Phase 1 요구사항_

- [ ]* 7.1 단위 테스트 작성
  - VirtualOfficeClient 메서드 테스트 (Mock 서버 사용)
  - 데이터 변환 함수 테스트
  - DataSourceManager 테스트
  - _Requirements: 1.1-1.6, 2.3, 2.4, 8.1-8.5_

- [ ]* 7.2 통합 테스트 작성
  - VirtualOffice 서버와의 실제 연동 테스트
  - 전체 데이터 수집 플로우 테스트
  - _Requirements: 모든 Phase 1 요구사항_

## Phase 2: 실시간 기능

- [x] 8. PollingWorker 구현




  - 백그라운드에서 주기적으로 새 데이터를 수집하는 워커 스레드 작성
  - 증분 수집 로직 구현
  - _Requirements: 2.1, 2.2, 2.5_

- [x] 8.1 PollingWorker 기본 구조 생성


  - `offline_agent/src/integrations/polling_worker.py` 파일 생성
  - QThread 상속 클래스 정의
  - 시그널 정의 (new_data_received, error_occurred)
  - _Requirements: 2.1, 2.2_

- [x] 8.2 폴링 루프 구현


  - `run()` 메서드 구현
  - 5초 간격으로 새 메일/메시지 조회
  - since_id 파라미터를 사용한 증분 조회
  - _Requirements: 2.1, 2.2_

- [x] 8.3 오류 처리 및 재시도 로직


  - 네트워크 오류 시 재시도 로직 구현
  - 연속 실패 시 대기 시간 증가 (exponential backoff)
  - 오류 시그널 발생
  - _Requirements: 2.5, 9.1, 9.2_

- [x] 8.4 폴링 제어 메서드 구현


  - `start()` 및 `stop()` 메서드 구현
  - 폴링 간격 조정 기능
  - 시뮬레이션 일시정지 시 폴링 간격 증가
  - _Requirements: 3.5, 10.4_

- [x] 9. SimulationMonitor 구현




  - 시뮬레이션 상태를 모니터링하고 UI에 업데이트하는 모니터 작성
  - 틱 진행 감지 및 알림
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 9.1 SimulationMonitor 기본 구조 생성


  - `offline_agent/src/integrations/simulation_monitor.py` 파일 생성
  - QObject 상속 클래스 정의
  - 시그널 정의 (status_updated, tick_advanced)
  - _Requirements: 3.1_

- [x] 9.2 상태 폴링 로직 구현


  - QTimer를 사용한 2초 간격 폴링
  - `_poll_status()` 메서드 구현
  - 시뮬레이션 상태 조회 및 시그널 발생
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 9.3 틱 변경 감지 로직 구현


  - 이전 틱과 현재 틱 비교
  - 틱 변경 시 tick_advanced 시그널 발생
  - _Requirements: 3.1, 4.3_

- [x] 9.4 모니터링 제어 메서드 구현


  - `start_monitoring()` 및 `stop_monitoring()` 메서드 구현
  - 폴링 간격 조정 기능
  - _Requirements: 3.5_

- [x] 10. GUI에 실시간 기능 통합





  - PollingWorker 및 SimulationMonitor를 GUI에 통합
  - 새 데이터 도착 시 UI 업데이트
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 10.1 PollingWorker 인스턴스 생성 및 시작


  - `main_window.py` 파일 수정
  - VirtualOffice 연결 성공 시 PollingWorker 생성
  - 워커 시그널을 GUI 슬롯에 연결
  - _Requirements: 2.1, 2.2_

- [x] 10.2 새 데이터 수신 핸들러 구현


  - `on_new_data_received()` 메서드 구현
  - 새 메일/메시지를 기존 데이터에 추가
  - UI 업데이트 (메시지 목록, TODO 패널 등)
  - _Requirements: 4.1, 4.2_

- [x] 10.3 SimulationMonitor 인스턴스 생성 및 시작

  - VirtualOffice 연결 성공 시 SimulationMonitor 생성
  - 모니터 시그널을 GUI 슬롯에 연결
  - _Requirements: 3.1_

- [x] 10.4 시뮬레이션 상태 업데이트 핸들러 구현


  - `on_sim_status_updated()` 메서드 구현
  - 시뮬레이션 상태 레이블 업데이트 (틱, 시간, 실행 상태)
  - _Requirements: 3.2, 3.3, 3.4_

- [x] 10.5 틱 진행 알림 핸들러 구현


  - `on_tick_advanced()` 메서드 구현
  - 상태바에 틱 진행 메시지 표시
  - 틱별 활동 요약 표시 (선택적)
  - _Requirements: 4.3, 4.4_

- [x] 11. 실시간 기능 테스트





  - 시뮬레이션 진행 중 새 데이터 수집 확인
  - 틱 진행 알림 확인
  - 오류 처리 및 재시도 확인
  - _Requirements: 모든 Phase 2 요구사항_

- [ ]* 11.1 폴링 워커 테스트 작성
  - PollingWorker 동작 테스트
  - 증분 수집 로직 테스트
  - 오류 처리 테스트
  - _Requirements: 2.1, 2.2, 2.5, 9.1-9.3_

- [ ]* 11.2 시뮬레이션 모니터 테스트 작성
  - SimulationMonitor 동작 테스트
  - 틱 변경 감지 테스트
  - _Requirements: 3.1-3.5_

## Phase 3: UI 개선

- [x] 12. 새 데이터 시각적 알림 구현





  - 새 메일/메시지 도착 시 배지 표시
  - 애니메이션 효과 추가
  - _Requirements: 4.1, 4.2, 4.5_

- [x] 12.1 NEW 배지 위젯 생성


  - 메시지 목록 아이템에 "NEW" 배지 추가
  - 3초 후 자동 사라지는 애니메이션 구현
  - _Requirements: 4.1, 4.2_

- [x] 12.2 시각적 알림 효과 추가


  - 새 데이터 도착 시 색상 변경 또는 애니메이션
  - 0.5초 동안 표시
  - _Requirements: 4.5_

- [x] 13. 틱 히스토리 표시 기능 구현




  - 최근 틱별 활동 요약 표시
  - 틱 히스토리 다이얼로그 구현
  - _Requirements: 4.4_

- [x] 13.1 틱 히스토리 데이터 구조 설계


  - 최근 100개 틱의 활동 정보 저장
  - 틱별 메일/메시지 수 추적
  - _Requirements: 4.4_


- [x] 13.2 틱 히스토리 다이얼로그 UI 구현

  - QDialog 기반 히스토리 창 생성
  - 테이블 또는 리스트로 틱별 활동 표시
  - _Requirements: 4.4_

- [x] 14. 시뮬레이션 상태 패널 개선




  - 더 상세한 시뮬레이션 정보 표시
  - 진행률 바 추가
  - _Requirements: 3.2, 3.3, 3.4_

- [x] 14.1 상세 상태 정보 표시


  - 현재 틱, 시뮬레이션 시간, 실행 상태를 더 명확하게 표시
  - 아이콘 및 색상 사용
  - _Requirements: 3.2, 3.3, 3.4_

- [x] 14.2 진행률 바 추가 (선택적)


  - 시뮬레이션 전체 진행률 표시 (총 틱 대비 현재 틱)
  - _Requirements: 3.2_

- [ ] 15. UI 개선 테스트
  - 새 데이터 알림 동작 확인
  - 틱 히스토리 표시 확인
  - 시뮬레이션 상태 패널 확인
  - _Requirements: 모든 Phase 3 요구사항_

- [ ]* 15.1 UI 컴포넌트 테스트 작성
  - NEW 배지 표시 테스트
  - 틱 히스토리 다이얼로그 테스트
  - _Requirements: 4.1-4.5_

## Phase 4: 고급 기능

- [x] 16. 오류 처리 및 복구 강화




  - 연결 관리자 구현
  - 오류 알림 시스템 구현
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 16.1 ConnectionManager 구현


  - `offline_agent/src/integrations/connection_manager.py` 파일 생성
  - 재시도 로직이 적용된 `execute_with_retry()` 메서드 구현
  - 연속 실패 추적 및 exponential backoff
  - _Requirements: 9.1, 9.2_

- [x] 16.2 ErrorNotifier 구현


  - 오류 알림 관리 클래스 작성
  - 중복 알림 방지 로직 (1분 이내 동일 오류)
  - 재시도/취소 옵션 제공
  - _Requirements: 9.3, 9.4_

- [x] 16.3 데이터 검증 함수 구현


  - `validate_email_response()` 및 `validate_message_response()` 함수 작성
  - 필수 필드 검증
  - 잘못된 데이터 건너뛰기 및 로깅
  - _Requirements: 9.3_

- [x] 16.4 연결 복구 로직 구현


  - 연결 복구 시 마지막 성공 시점 이후 데이터 조회
  - 데이터 중복 방지
  - VirtualOfficeClient에 ConnectionManager 통합
  - _Requirements: 9.5_

- [x] 17. 성능 최적화




  - 폴링 최적화 (병렬 처리)
  - 메모리 관리 (자동 정리)
  - UI 반응성 개선
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 17.1 병렬 데이터 수집 구현


  - asyncio를 사용한 병렬 API 호출
  - `collect_new_data_batch()` 메서드 구현
  - _Requirements: 10.1_

- [x] 17.2 메모리 관리 로직 구현


  - `cleanup_old_messages()` 메서드 구현
  - 최대 10,000개 메시지 유지
  - 오래된 데이터 자동 삭제
  - _Requirements: 10.1, 10.2_

- [x] 17.3 캐싱 구현


  - 페르소나 정보 캐싱
  - 정적 데이터 재사용
  - _Requirements: 10.1_

- [x] 17.4 UI 반응성 개선


  - 장시간 작업 시 프로그레스 바 표시
  - 점진적 UI 업데이트
  - _Requirements: 10.3_

- [x] 18. 설정 저장 및 로드 기능 구현




  - VirtualOfficeConfig 저장/로드
  - 환경 변수 지원
  - _Requirements: 7.4, 7.5_

- [x] 18.1 설정 파일 저장 기능 구현


  - `data/virtualoffice_config.json` 파일에 설정 저장
  - VirtualOfficeConfig.save_to_file() 메서드 사용
  - 연결 성공 시 자동 저장
  - _Requirements: 7.4_

- [x] 18.2 설정 파일 로드 기능 구현


  - 애플리케이션 시작 시 설정 파일 자동 로드
  - VirtualOfficeConfig.load_from_file() 메서드 사용
  - UI에 저장된 URL 자동 반영
  - _Requirements: 7.5_

- [x] 18.3 환경 변수 지원 추가


  - VDOS_EMAIL_URL, VDOS_CHAT_URL, VDOS_SIM_URL 환경 변수 읽기
  - 환경 변수가 설정 파일보다 우선
  - 우선순위: 환경 변수 > 설정 파일 > 기본값
  - _Requirements: 7.5_

- [x] 18.4 설정 관리 문서 작성


  - VIRTUALOFFICE_CONFIG.md 문서 작성
  - 설정 파일 형식 및 사용법 설명
  - 환경 변수 사용 예시 추가
  - 문제 해결 가이드 포함
  - _Requirements: 7.4, 7.5_

- [x] 19. 문서 및 사용자 가이드 작성




  - README.md 업데이트
  - TROUBLESHOOTING.md 업데이트
  - CHANGELOG.md 업데이트
  - _Requirements: 모든 요구사항_

- [x] 19.1 README.md 업데이트


  - VirtualOffice 연동 사용법 섹션 추가
  - 설정 관리 정보 추가 (자동 저장/로드, 환경 변수)
  - 관련 문서 링크 추가
  - _Requirements: 모든 요구사항_

- [x] 19.2 TROUBLESHOOTING.md 작성


  - VirtualOffice 연동 문제 해결 섹션 추가
  - 서버 연결 실패, 페르소나 목록 비어있음, 새 데이터 미수집 등
  - 설정 파일 및 환경 변수 문제 해결
  - 데이터 수집, GUI, 성능 문제 해결
  - 로그 확인 방법 및 이슈 보고 가이드
  - _Requirements: 9.1-9.5_

- [x] 19.3 CHANGELOG.md 업데이트


  - 설정 관리 기능 추가 기록 (Unreleased 섹션)
  - 버전 정보 업데이트
  - _Requirements: 모든 요구사항_

- [ ] 20. 최종 테스트 및 검증
  - 전체 기능 통합 테스트
  - 성능 테스트
  - 사용자 시나리오 테스트
  - _Requirements: 모든 요구사항_

- [ ]* 20.1 통합 테스트 작성
  - 전체 데이터 수집 플로우 테스트
  - 페르소나 전환 테스트
  - 시간 범위 필터 테스트
  - _Requirements: 모든 요구사항_

- [ ]* 20.2 성능 테스트 작성
  - 1000개 메시지 수집 시 응답 시간 측정
  - 메모리 사용량 측정
  - 폴링 간격 정확도 측정
  - _Requirements: 10.1-10.5_

- [ ]* 20.3 사용자 시나리오 테스트
  - 실제 사용 시나리오 기반 테스트
  - 오류 복구 시나리오 테스트
  - _Requirements: 모든 요구사항_
