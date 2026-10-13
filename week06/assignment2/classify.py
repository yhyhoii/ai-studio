# classify.py — 리뷰 1건을 분류하는 classify_review
import json
from mock_llm import mock_llm_call

SYSTEM = """당신은 고객 리뷰 분류기입니다. 반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트를 절대 포함하지 마세요.
{"category": "배송|품질|가격|서비스|기타", "sentiment": "긍정|부정|중립", "score": 1~5 사이의 정수}"""

VALID_CATEGORIES = ["배송", "품질", "가격", "환불", "서비스", "기타"]


def classify_review(review_text):
    """리뷰 1건을 분류하여 딕셔너리로 반환. 실패 시 None."""
    result = mock_llm_call(SYSTEM, f"리뷰: {review_text}")
    raw = result["text"].strip()  # 결과 텍스트의 앞뒤 불필요한 공백과 줄바꿈을 제거

    # 방어 1: 마크다운 코드 블록 제거 (포맷 정규화): ```json ... ``` 코드 제거
    if raw.startswith("```"):
        raw = raw.strip("`")  # 문자열의 시작과 끝에 붙은 백틱(`)만 모두 제거
        raw = raw.replace("json", "", 1).strip()  # "json"을 한번만(1회) 지우고 strip()

    # 방어 2: 파싱 실패는 언제든 일어날 수 있다 → 예외 처리 필수
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(f"[경고] JSON 파싱 실패 (stop_reason={result['stop_reason']}): {raw[:50]}...")
        return None

    # 방어 3: 필드 존재와 값의 유효성 검증
    if data.get("category") not in VALID_CATEGORIES:
        return None
    return data
