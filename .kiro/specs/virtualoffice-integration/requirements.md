# Requirements Document

## Introduction

이 문서는 offline_agent와 virtualoffice 시스템 간의 실시간 통합 기능에 대한 요구사항을 정의합니다. 이 통합을 통해 offline_agent는 virtualoffice의 시뮬레이션에서 생성된 메일 및 메시지 데이터를 실시간으로 수집하고 분석할 수 있으며, 사용자는 시뮬레이션 진행 상황을 모니터링하고 다양한 페르소나 관점에서 데이터를 분석할 수 있습니다.

## Glossary

- **offline_agent**: 오프라인 메시지 분석 및 TODO 생성 데스크톱 애플리케이션
- **virtualoffice**: 가상 부서 시뮬레이션 시스템 (VDOS)
- **Simulation Manager**: virtualoffice의 시뮬레이션 엔진 (포트 8015)
- **Email Server**: virtualoffice의 이메일 REST API 서버 (포트 8000/8025)
- **Chat Server**: virtualoffice의 채팅 REST API 서버 (포트 8001/8035)
- **Tick**: virtualoffice 시뮬레이션의 시간 단위 (기본 50ms)
- **Persona**: virtualoffice 시뮬레이션의 가상 직원 캐릭터
- **PM (Project Manager)**: 프로젝트 관리자 페르소나, offline_agent의 기본 사용자
- **Data Collection**: virtualoffice API로부터 메일/메시지를 가져오는 프로세스
- **Real-time Sync**: 시뮬레이션 진행에 따른 실시간 데이터 동기화

## Requirements

### Requirement 1: virtualoffice API 연동

**User Story:** PM으로서, virtualoffice 시뮬레이션에서 생성된 메일과 메시지를 offline_agent에서 실시간으로 수집하고 분석하고 싶습니다. 이를 통해 실제 데이터 없이도 시스템을 테스트하고 개선할 수 있습니다.

#### Acceptance Criteria

1. WHEN 사용자가 virtualoffice 연동 설정을 활성화하면, THE offline_agent SHALL Email Server (포트 8000 또는 8025)에 HTTP 연결을 시도한다
2. WHEN 사용자가 virtualoffice 연동 설정을 활성화하면, THE offline_agent SHALL Chat Server (포트 8001 또는 8035)에 HTTP 연결을 시도한다
3. WHEN 사용자가 virtualoffice 연동 설정을 활성화하면, THE offline_agent SHALL Simulation Manager (포트 8015)에 HTTP 연결을 시도한다
4. WHEN API 연결이 실패하면, THE offline_agent SHALL 사용자에게 연결 실패 메시지를 표시하고 재시도 옵션을 제공한다
5. WHEN API 연결이 성공하면, THE offline_agent SHALL 연결 상태를 UI에 표시한다

### Requirement 2: 실시간 데이터 수집

**User Story:** PM으로서, virtualoffice 시뮬레이션이 진행되는 동안 새로운 메일과 메시지를 자동으로 수집하고 싶습니다. 이를 통해 실시간으로 업데이트되는 커뮤니케이션을 분석할 수 있습니다.

#### Acceptance Criteria

1. WHEN virtualoffice 연동이 활성화되면, THE offline_agent SHALL 5초마다 Email Server의 `/emails` 엔드포인트를 폴링한다
2. WHEN virtualoffice 연동이 활성화되면, THE offline_agent SHALL 5초마다 Chat Server의 `/messages` 엔드포인트를 폴링한다
3. WHEN 새로운 메일이 수집되면, THE offline_agent SHALL 기존 데이터 구조와 동일한 형식으로 변환하여 저장한다
4. WHEN 새로운 메시지가 수집되면, THE offline_agent SHALL 기존 데이터 구조와 동일한 형식으로 변환하여 저장한다
5. WHEN 데이터 수집 중 오류가 발생하면, THE offline_agent SHALL 오류를 로깅하고 다음 폴링 주기에 재시도한다

### Requirement 3: 시뮬레이션 상태 모니터링

**User Story:** PM으로서, virtualoffice 시뮬레이션의 현재 상태와 진행 상황을 실시간으로 확인하고 싶습니다. 이를 통해 시뮬레이션이 정상적으로 작동하는지 파악할 수 있습니다.

#### Acceptance Criteria

1. WHEN virtualoffice 연동이 활성화되면, THE offline_agent SHALL Simulation Manager의 `/status` 엔드포인트를 2초마다 폴링한다
2. WHEN 시뮬레이션 상태를 수신하면, THE offline_agent SHALL 현재 틱(tick) 번호를 UI에 표시한다
3. WHEN 시뮬레이션 상태를 수신하면, THE offline_agent SHALL 시뮬레이션 시간(가상 날짜/시간)을 UI에 표시한다
4. WHEN 시뮬레이션 상태를 수신하면, THE offline_agent SHALL 시뮬레이션 실행 상태(running/paused/stopped)를 UI에 표시한다
5. WHEN 시뮬레이션이 일시정지 또는 중지되면, THE offline_agent SHALL 데이터 폴링을 일시정지한다

### Requirement 4: 틱 단위 변경점 시각화

**User Story:** PM으로서, virtualoffice 시뮬레이션의 각 틱마다 발생한 새로운 메일과 메시지를 시각적으로 확인하고 싶습니다. 이를 통해 시뮬레이션 진행에 따른 커뮤니케이션 패턴을 이해할 수 있습니다.

#### Acceptance Criteria

1. WHEN 새로운 메일이 수집되면, THE offline_agent SHALL 메일 목록에 "NEW" 배지를 3초 동안 표시한다
2. WHEN 새로운 메시지가 수집되면, THE offline_agent SHALL 메시지 목록에 "NEW" 배지를 3초 동안 표시한다
3. WHEN 틱이 진행되면, THE offline_agent SHALL 해당 틱에서 수집된 항목 수를 상태 표시줄에 표시한다
4. WHEN 사용자가 틱 히스토리를 요청하면, THE offline_agent SHALL 최근 100개 틱의 활동 요약을 표시한다
5. WHEN 새로운 데이터가 수집되면, THE offline_agent SHALL 시각적 알림(색상 변경 또는 애니메이션)을 0.5초 동안 표시한다

### Requirement 5: 사용자 페르소나 선택

**User Story:** 분석가로서, PM이 아닌 다른 팀원의 관점에서 메일과 메시지를 분석하고 싶습니다. 이를 통해 다양한 역할의 커뮤니케이션 패턴을 이해할 수 있습니다.

#### Acceptance Criteria

1. WHEN virtualoffice 연동이 활성화되면, THE offline_agent SHALL Simulation Manager로부터 사용 가능한 페르소나 목록을 조회한다
2. WHEN 페르소나 목록을 수신하면, THE offline_agent SHALL UI에 페르소나 선택 드롭다운을 표시한다
3. WHEN 사용자가 페르소나를 선택하면, THE offline_agent SHALL 해당 페르소나를 수신자로 하는 메일과 메시지만 필터링한다
4. WHEN PM 페르소나가 존재하면, THE offline_agent SHALL PM을 기본 선택 페르소나로 설정한다
5. WHEN PM 페르소나가 존재하지 않으면, THE offline_agent SHALL 첫 번째 페르소나를 기본 선택으로 설정한다

### Requirement 6: 시간 범위 필터링 호환

**User Story:** PM으로서, virtualoffice에서 수집한 데이터에도 기존의 시간 범위 필터를 적용하고 싶습니다. 이를 통해 특정 기간의 커뮤니케이션만 분석할 수 있습니다.

#### Acceptance Criteria

1. WHEN virtualoffice 데이터가 로드되면, THE offline_agent SHALL 각 메일과 메시지의 타임스탬프를 파싱한다
2. WHEN 사용자가 시간 범위를 선택하면, THE offline_agent SHALL virtualoffice 데이터를 선택된 범위로 필터링한다
3. WHEN 시간 범위 필터가 적용되면, THE offline_agent SHALL 필터링된 데이터에 대해서만 분석을 수행한다
4. WHEN 실시간 수집 중 새 데이터가 도착하면, THE offline_agent SHALL 현재 시간 범위 필터를 자동으로 적용한다
5. WHEN 시뮬레이션 시간이 필터 범위를 벗어나면, THE offline_agent SHALL 사용자에게 필터 범위 확장을 제안한다

### Requirement 7: 연동 설정 관리

**User Story:** 사용자로서, virtualoffice 연동 설정을 쉽게 구성하고 관리하고 싶습니다. 이를 통해 다양한 환경에서 시스템을 사용할 수 있습니다.

#### Acceptance Criteria

1. WHEN 사용자가 설정 메뉴를 열면, THE offline_agent SHALL virtualoffice 연동 설정 섹션을 표시한다
2. WHEN 사용자가 연동 설정을 입력하면, THE offline_agent SHALL Email Server URL, Chat Server URL, Simulation Manager URL을 저장한다
3. WHEN 사용자가 연동 설정을 입력하면, THE offline_agent SHALL 폴링 간격(초)을 저장한다
4. WHEN 사용자가 설정을 저장하면, THE offline_agent SHALL 설정을 .env 파일 또는 로컬 설정 파일에 영구 저장한다
5. WHEN 애플리케이션이 시작되면, THE offline_agent SHALL 저장된 연동 설정을 자동으로 로드한다

### Requirement 8: 데이터 소스 전환

**User Story:** 사용자로서, JSON 파일 기반 데이터와 virtualoffice 실시간 데이터를 쉽게 전환하고 싶습니다. 이를 통해 오프라인과 온라인 모드를 유연하게 사용할 수 있습니다.

#### Acceptance Criteria

1. WHEN 사용자가 데이터 소스 메뉴를 열면, THE offline_agent SHALL "로컬 JSON 파일"과 "virtualoffice 실시간" 옵션을 표시한다
2. WHEN 사용자가 "로컬 JSON 파일"을 선택하면, THE offline_agent SHALL virtualoffice 연동을 비활성화하고 기존 JSON 파일을 로드한다
3. WHEN 사용자가 "virtualoffice 실시간"을 선택하면, THE offline_agent SHALL JSON 파일 로딩을 비활성화하고 API 연동을 활성화한다
4. WHEN 데이터 소스가 전환되면, THE offline_agent SHALL 현재 분석 결과를 초기화하고 새 데이터를 로드한다
5. WHEN 데이터 소스가 전환되면, THE offline_agent SHALL 선택된 데이터 소스를 UI에 명확히 표시한다

### Requirement 9: 오류 처리 및 복구

**User Story:** 사용자로서, virtualoffice 연동 중 발생하는 오류를 명확히 이해하고 복구할 수 있기를 원합니다. 이를 통해 시스템을 안정적으로 사용할 수 있습니다.

#### Acceptance Criteria

1. WHEN API 요청이 5초 이상 응답하지 않으면, THE offline_agent SHALL 요청을 타임아웃 처리하고 오류를 로깅한다
2. WHEN 연속 3회 API 요청이 실패하면, THE offline_agent SHALL 사용자에게 연결 문제를 알리고 재연결 옵션을 제공한다
3. WHEN 잘못된 형식의 데이터를 수신하면, THE offline_agent SHALL 해당 데이터를 건너뛰고 오류를 로깅한다
4. WHEN 사용자가 재연결을 요청하면, THE offline_agent SHALL 모든 API 연결을 재시도한다
5. WHEN 연결이 복구되면, THE offline_agent SHALL 마지막 성공 시점 이후의 데이터를 조회한다

### Requirement 10: 성능 및 리소스 관리

**User Story:** 사용자로서, virtualoffice 연동이 시스템 리소스를 과도하게 사용하지 않기를 원합니다. 이를 통해 장시간 안정적으로 시스템을 운영할 수 있습니다.

#### Acceptance Criteria

1. WHEN 수집된 데이터가 10,000개를 초과하면, THE offline_agent SHALL 가장 오래된 데이터부터 자동으로 정리한다
2. WHEN 메모리 사용량이 500MB를 초과하면, THE offline_agent SHALL 캐시된 분석 결과를 정리한다
3. WHEN 폴링 요청이 실행 중이면, THE offline_agent SHALL 다음 폴링 주기를 건너뛴다
4. WHEN 시뮬레이션이 일시정지되면, THE offline_agent SHALL 폴링 간격을 10초로 증가시킨다
5. WHEN 애플리케이션이 종료되면, THE offline_agent SHALL 모든 API 연결을 정상적으로 종료한다
