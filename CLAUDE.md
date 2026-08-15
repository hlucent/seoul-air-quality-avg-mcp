# CLAUDE.md — 서울시 대기환경 평균 현황 MCP 개발 지침

이 문서는 Claude Code가 이 저장소에서 작업할 때 따라야 할 규칙입니다.
**목표: 토큰 소모 최소화 + DEVPLAN.md를 그대로 구현.** 스스로 설계를 다시 고민하지 말고 아래 계획을 그대로 따르세요.

## 0. 절대 규칙
- 이 저장소 루트의 `DEVPLAN.md`가 설계 원본입니다. 먼저 그 파일 하나만 읽고 시작하세요. 다른 문서를 먼저 탐색하지 마세요.
- 웹서치나 서울 열린데이터광장 사이트 재탐색 금지. API 스펙은 DEVPLAN.md에 이미 전부 있습니다.
- 불확실한 부분이 있으면 추측해서 여러 방향으로 구현해보지 말고, DEVLOG.md에 "확인 필요" 항목으로 남기고 가장 합리적인 기본값으로 1번만 구현하세요.
- 같은 파일을 반복해서 다시 읽지 마세요. 한 번 연 파일 내용은 대화 컨텍스트에 남아있다고 가정하세요.
- 디버깅 루프는 **동일 오류에 대해 최대 3회**까지만 재시도합니다. 3회 실패 시 DEVLOG.md에 실패 원인과 시도한 내용을 기록하고 다음 단계로 넘어가거나 사용자에게 보고하세요.
- `flyctl deploy`는 **절대 자동 실행하지 마세요.** 배포 직전 단계까지만 진행하고 멈추세요.

## 1. 작업 순서 (이 순서를 그대로 따르세요)
1. `requirements.txt` 작성: `fastmcp`, `httpx`, `python-dotenv`
2. `seoul_api.py` 작성
   - `TYPE=json`으로 호출 (xml 파싱보다 코드 간결)
   - Base URL: `http://openapi.seoul.go.kr:8088/{KEY}/json/ListAvgOfSeoulAirQualityService/{START}/{END}/{GRADE}`
   - GRADE가 없을 경우 URL 마지막 세그먼트를 생략 (빈 문자열로 두지 말 것 — API가 별도 처리하는지 실제 응답으로 확인)
   - 에러코드(RESULT.CODE) 매핑: INFO-000→정상, INFO-100→"인증키 오류, .env의 SEOUL_API_KEY 확인 필요", INFO-200→"해당 기간 데이터 없음", ERROR-3xx→"요청 파라미터 오류: {메시지}", ERROR-5/6xx→"서울시 서버 오류, 잠시 후 재시도"
3. `server.py` 작성
   - FastMCP 인스턴스 1개, 툴 2개(`get_latest_air_quality`, `get_air_quality_range`) — DEVPLAN.md 3장 그대로
   - 각 툴의 docstring에 반환 필드 단위(ppm, ㎍/㎥) 반드시 명시 — LLM이 사용자에게 답할 때 단위 착각 방지 목적
   - transport는 기존 서울시 MCP 시리즈와 동일하게 streamable-http, PORT는 환경변수 `PORT` (기본 8080)
4. `.env.example` 작성 (`SEOUL_API_KEY=` 만, 실제 키는 절대 커밋 금지)
5. `.gitignore`에 `.env`, `__pycache__/`, `*.pyc` 추가
6. 로컬 테스트: `.env`에 사용자가 넣어둔 실제 키로 두 툴 모두 1회씩 호출해서 정상 응답 확인. 실패 시 위 3회 재시도 규칙 적용.
7. `Dockerfile` 작성 — python:3.12-slim 기반, requirements 설치 후 `CMD ["python", "server.py"]`
8. `fly.toml` 작성 — 앱 이름은 저장소 이름과 동일하게, internal_port는 서버 PORT와 일치
9. `README.md` 최신화 (초안은 이미 저장소에 있음, 실제 구현과 다른 부분만 수정)
10. `DEVLOG.md`에 진행 기록 (아래 형식)
11. 여기까지 끝나면 **정지**하고 사용자에게 "배포 준비 완료, `flyctl deploy` 실행은 직접 하시거나 명시적으로 지시해주세요"라고 보고

## 2. DEVLOG.md 기록 형식
매 작업 단계마다 아래처럼 짧게 추가 (장문 서술 금지):
```
### [단계명] YYYY-MM-DD
- 한 일: (한 줄)
- 이슈: (있으면 한 줄, 없으면 생략)
- 다음: (한 줄)
```

## 3. 하지 말아야 할 것
- 툴을 3개 이상으로 확장하지 마세요 (DEVPLAN.md 범위 고정)
- 인증키를 코드나 커밋에 하드코딩하지 마세요
- xml/xmlf 타입 파싱 시도하지 마세요 (json으로 통일)
- README/CLAUDE.md 문체나 구조를 임의로 재작성하지 마세요 (내용 업데이트만)
- 자치구별 MCP(기존 프로젝트)의 코드를 복사하려 하지 마세요 — 이건 응답 구조가 다른 별도 API입니다
