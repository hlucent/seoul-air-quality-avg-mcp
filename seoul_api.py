import os

import httpx

BASE_URL = "http://openapi.seoul.go.kr:8088"
SERVICE = "ListAvgOfSeoulAirQualityService"

# RESULT.CODE -> 사람이 이해할 수 있는 메시지
ERROR_MESSAGES = {
    "INFO-100": "인증키 오류, .env의 SEOUL_API_KEY 확인 필요",
    "INFO-200": "해당 기간 데이터 없음",
}


class SeoulApiError(Exception):
    pass


def _map_error(code: str, message: str) -> str:
    if code in ERROR_MESSAGES:
        return ERROR_MESSAGES[code]
    if code.startswith("ERROR-3"):
        return f"요청 파라미터 오류: {message}"
    if code.startswith("ERROR-5") or code.startswith("ERROR-6"):
        return "서울시 서버 오류, 잠시 후 재시도"
    return f"알 수 없는 오류({code}): {message}"


def fetch_air_quality(start_index: int, end_index: int, grade: str | None = None) -> list[dict]:
    api_key = os.environ.get("SEOUL_API_KEY")
    if not api_key:
        raise SeoulApiError("SEOUL_API_KEY가 설정되지 않았습니다. .env를 확인하세요.")

    segments = [BASE_URL, api_key, "json", SERVICE, str(start_index), str(end_index)]
    if grade:
        segments.append(grade)
    url = "/".join(segments)

    resp = httpx.get(url, timeout=10.0)
    resp.raise_for_status()
    data = resp.json()

    body = data.get(SERVICE)
    if body is None:
        raise SeoulApiError("예상치 못한 응답 형식입니다.")

    result = body.get("RESULT", {})
    code = result.get("CODE", "")
    message = result.get("MESSAGE", "")

    if code != "INFO-000":
        raise SeoulApiError(_map_error(code, message))

    return body.get("row", [])
