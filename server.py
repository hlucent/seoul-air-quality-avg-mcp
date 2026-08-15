import os

from dotenv import load_dotenv
from fastmcp import FastMCP

from seoul_api import SeoulApiError, fetch_air_quality

load_dotenv()

mcp = FastMCP("seoul-air-quality-avg")


@mcp.tool()
def get_latest_air_quality(grade: str | None = None) -> dict:
    """서울 전체 평균 대기환경 최신 1건을 조회합니다.

    Args:
        grade: 통합대기환경지수 등급 필터 (예: "보통"). 선택 사항.

    Returns:
        dict: 최신 서울 전체 평균 대기질 정보.
            - CAI_GRD: 통합대기환경지수 등급
            - CAI: 통합대기환경지수
            - CRST_SBSTN: 지수 결정 물질
            - NTDX: 이산화질소 (ppm)
            - OZON: 오존 (ppm)
            - CBMX: 일산화탄소 (ppm)
            - SPDX: 아황산가스 (ppm)
            - PM: 미세먼지 PM-10 (㎍/㎥)
            - FPM: 초미세먼지 PM-2.5 (㎍/㎥)
    """
    try:
        rows = fetch_air_quality(1, 1, grade)
    except SeoulApiError as e:
        return {"error": str(e)}
    return rows[0] if rows else {"error": "데이터 없음"}


@mcp.tool()
def get_air_quality_range(start_index: int = 1, end_index: int = 24, grade: str | None = None) -> dict:
    """서울 전체 평균 대기환경을 여러 건(시계열) 조회합니다.

    주의: 이 API는 날짜가 아닌 "레코드 순번" 방식입니다.
    START_INDEX=1이 가장 최근 값이며, 인덱스가 커질수록 과거 데이터입니다.
    한 번에 최대 1000건까지 조회 가능하며 (end_index - start_index) <= 1000 이어야 합니다.

    Args:
        start_index: 조회 시작 순번 (1부터 시작, 기본 1)
        end_index: 조회 종료 순번 (기본 24, 최대 1000건 제한)
        grade: 통합대기환경지수 등급 필터 (예: "보통"). 선택 사항.

    Returns:
        dict: {"count": 건수, "rows": [레코드, ...]}
            각 레코드 필드:
            - CAI_GRD: 통합대기환경지수 등급
            - CAI: 통합대기환경지수
            - CRST_SBSTN: 지수 결정 물질
            - NTDX: 이산화질소 (ppm)
            - OZON: 오존 (ppm)
            - CBMX: 일산화탄소 (ppm)
            - SPDX: 아황산가스 (ppm)
            - PM: 미세먼지 PM-10 (㎍/㎥)
            - FPM: 초미세먼지 PM-2.5 (㎍/㎥)
    """
    try:
        rows = fetch_air_quality(start_index, end_index, grade)
    except SeoulApiError as e:
        return {"error": str(e)}
    return {"count": len(rows), "rows": rows}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port, stateless_http=True)
