# 개발계획서 — 서울시 실시간 대기환경 평균 현황 MCP

## 1. 데이터 개요
- **서비스명(SERVICE)**: `ListAvgOfSeoulAirQualityService`
- **제공기관**: 서울특별시 (기후환경본부 대기정책과)
- **내용**: 서울시 25개 자치구 대기환경 측정값을 합산한 "서울 전체 평균값". 매시간 갱신.
- **기존 MCP와의 차이**: 이미 보유 중인 "서울시 실시간 자치구별 대기환경 현황 MCP"는 자치구별 값을 다루고, 이번 것은 **서울 전체 평균 1개 값(시계열)** 을 다룸. 서로 다른 API이므로 별도 프로젝트로 진행.

## 2. API 스펙 요약

### 요청 (Base URL)
```
http://openapi.seoul.go.kr:8088/{KEY}/{TYPE}/ListAvgOfSeoulAirQualityService/{START_INDEX}/{END_INDEX}/{CAI_GRD}
```
| 변수 | 타입 | 설명 |
|---|---|---|
| KEY | string(필수) | 인증키 |
| TYPE | string(필수) | xml / xmlf / xls / json |
| START_INDEX | int(필수) | 요청 시작 위치 (1부터) |
| END_INDEX | int(필수) | 요청 종료 위치 (한 번에 최대 1000건, 시작-종료 차이 ≤1000) |
| CAI_GRD | string(선택) | 통합대기환경지수 등급 필터 (예: "보통") |

### 응답 필드
| 필드명 | 설명 | 단위 |
|---|---|---|
| CAI_GRD | 통합대기환경지수 등급 | - |
| CAI | 통합대기환경지수 | - |
| CRST_SBSTN | 지수 결정 물질 | - |
| NTDX | 이산화질소 | ppm |
| OZON | 오존 | ppm |
| CBMX | 일산화탄소 | ppm |
| SPDX | 아황산가스 | ppm |
| PM | 미세먼지(PM-10) | ㎍/㎥ |
| FPM | 초미세먼지(PM-2.5) | ㎍/㎥ |

### 에러 코드
INFO-000(정상), INFO-100(인증키 오류), INFO-200(데이터 없음), ERROR-300(필수값 누락), ERROR-301(TYPE 오류), ERROR-310(SERVICE 오류), ERROR-331~335(INDEX 범위 오류), ERROR-336(1000건 초과), ERROR-500/600/601(서버/DB 오류)
→ MCP 응답 시 이 코드를 그대로 노출하지 말고, 사람이 이해할 수 있는 메시지로 변환.

## 3. MCP 서버 설계

### 제공 툴 (2개로 최소화)
1. **`get_latest_air_quality`**
   - 파라미터: 없음(또는 `grade` 선택)
   - 동작: START_INDEX=1, END_INDEX=1 로 최신 1건 조회
   - 반환: 최신 시각 기준 서울 전체 평균 대기질 요약

2. **`get_air_quality_range`**
   - 파라미터: `start_index`(int, 기본 1), `end_index`(int, 기본 24, 최대 1000), `grade`(선택, 등급 필터)
   - 동작: 기간 내 여러 건 조회 (시계열 추이 확인용)
   - 반환: 레코드 배열 + 각 필드 단위 주석 포함

> 참고: 이 API는 날짜 파라미터가 아니라 "몇 번째~몇 번째 레코드"인 INDEX 방식입니다(자치구별 API와 다름). START_INDEX/END_INDEX 관계를 코드 주석에 명확히 남길 것.

### 기술 스택 (기존 프로젝트와 통일)
- Python + FastMCP (streamable-http transport)
- httpx (동기/비동기 HTTP 클라이언트)
- Dockerfile 기반 fly.io 배포
- 환경변수: `SEOUL_API_KEY` (fly.io secrets로 주입, 코드에 하드코딩 금지)

### 디렉토리 구조
```
seoul-air-quality-avg-mcp/
├── server.py          # FastMCP 서버 진입점, 툴 2개 정의
├── seoul_api.py        # openapi.seoul.go.kr 호출 + 에러코드 매핑 로직
├── requirements.txt
├── Dockerfile
├── fly.toml
├── .env.example
├── .gitignore
├── README.md
├── CLAUDE.md
└── DEVLOG.md
```

## 4. 진행 순서 (Claude Code가 자동 수행할 범위)
1. `seoul_api.py` 작성 — API 호출, 응답 파싱(xml/json 중 택1, 권장: type=json), 에러코드 → 예외 매핑
2. `server.py` 작성 — FastMCP 툴 2개 등록, docstring에 파라미터/단위 명시
3. 로컬 테스트 — `.env`의 실제 키로 실행 후 두 툴 모두 정상 응답 확인
4. `Dockerfile`, `fly.toml` 작성 (기존 서울시 MCP들과 동일 패턴 재사용)
5. `README.md`, `DEVLOG.md` 최신화
6. **여기서 정지** — `flyctl deploy` 실행은 사용자 확인 후 사용자가 직접 실행 (또는 명시적으로 "배포해"라고 지시할 때만)

## 5. 사용자가 먼저 해야 할 것
1. GitHub 빈 저장소 생성: 이름 결정 필요 (제안: `seoul-air-quality-avg-mcp`)
2. 서울 열린데이터광장에서 인증키 발급 (이미 자치구별 MCP를 운영 중이므로 기존 키 재사용 가능할 수 있음 — 서비스별 키 정책 확인 필요)
3. fly.io 계정/CLI 로그인 (최초 1회, 이미 되어 있으면 생략)
4. 로컬에 `git clone` 후 `.env`에 `SEOUL_API_KEY` 입력
