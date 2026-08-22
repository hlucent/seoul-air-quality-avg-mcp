> ⚠️ **이 프로젝트는 fly.io 서비스가 종료되었습니다 (2026-08-22 기준).**
> `seoul-air-quality-mcp` 통합 서버(서울시 대기환경정보 MCP)로 기능이 흡수되어, 이 저장소의 배포된 MCP 서버는 더 이상 응답하지 않습니다.
> 코드는 참고용으로 보존됩니다. 재배포하려면 아래 "배포" 섹션을 참고하세요.

# 서울시 실시간 대기환경 평균 현황 MCP

서울시 25개 자치구 대기환경 측정값을 합산한 **서울 전체 평균 대기질**을 조회하는 MCP 서버입니다.
(자치구별 개별 값이 아닌, 서울 전체를 대표하는 1개의 시계열 평균값을 다룹니다.)

데이터 출처: [서울 열린데이터광장 — 서울시 실시간 대기환경 평균 현황](https://data.seoul.go.kr) (서비스명: `ListAvgOfSeoulAirQualityService`)

## 제공 툴

### `get_latest_air_quality`
가장 최근 시점 기준 서울 전체 평균 대기질 1건을 조회합니다.

### `get_air_quality_range`
지정한 구간(레코드 순번 기준)의 대기질 이력을 조회합니다.
- `start_index` (기본 1)
- `end_index` (기본 24, 최대 1000)
- `grade` (선택, 통합대기환경지수 등급 필터)

> 참고: 실측 결과 이 API는 `list_total_count`가 항상 1로, 최신 1건만 제공합니다(과거 시계열 미제공). `end_index`를 크게 잡아도 반환 건수는 1건입니다.

## 반환 필드
| 필드 | 설명 | 단위 |
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

## 설치 및 실행

```bash
git clone <this-repo>
cd seoul-air-quality-avg-mcp
cp .env.example .env   # SEOUL_API_KEY 입력
pip install -r requirements.txt
python server.py
```

## 배포 (fly.io)

```bash
fly launch --no-deploy   # 최초 1회, fly.toml 생성/확인
fly secrets set SEOUL_API_KEY=발급받은키
fly deploy
```

## 환경변수
| 변수 | 설명 |
|---|---|
| `SEOUL_API_KEY` | 서울 열린데이터광장에서 발급받은 인증키 |
| `PORT` | 서버 포트 (기본 8080) |

## 라이선스
공공누리 1유형 (출처표시, 상업적 이용 및 변경 가능) — 데이터 제공: 서울특별시
