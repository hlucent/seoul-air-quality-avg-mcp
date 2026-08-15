# 개발일지

Claude Code는 작업 단계마다 아래 형식으로 짧게 기록합니다.

```
### [단계명] YYYY-MM-DD
- 한 일: (한 줄)
- 이슈: (있으면 한 줄)
- 다음: (한 줄)
```

---

### [프로젝트 시작] 2026-08-15
- 한 일: DEVPLAN.md / CLAUDE.md / README.md 초안 수령 (Claude 웹챗 작성)
- 다음: requirements.txt, seoul_api.py 작성부터 시작

### [핵심 구현] 2026-08-16
- 한 일: requirements.txt, seoul_api.py, server.py, Dockerfile, fly.toml 작성. 두 툴(get_latest_air_quality, get_air_quality_range) 실제 키로 정상 응답 확인
- 이슈: .env 파일에 BOM이 있어 python-dotenv가 SEOUL_API_KEY를 못 읽음 → BOM 제거로 해결
- 확인 필요: 이 API는 START_INDEX/END_INDEX를 넓게 잡아도 list_total_count가 항상 1로, 최신 1건만 반환됨(과거 시계열 미제공으로 추정). README에 참고 문구 추가함. 서울 열린데이터광장 측 스펙 재확인 필요할 수 있음
- 다음: 배포 준비 완료, flyctl deploy는 사용자 직접 실행
