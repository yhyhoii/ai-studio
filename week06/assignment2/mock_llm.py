# mock_llm.py — 6~12주차용 모의 LLM 모듈
import random

# 불량 응답이 나올 확률 (실제 LLM도 가끔 형식이 깨진 답을 준다)
MALFORMED_RATE = 0.2

# 테스트용 기록: 불량 응답을 유형별로 몇 번 돌려줬는지 센다 (13주차 실제 API 교체 시 삭제)
malformed_counts = {"codefence": 0, "chatty": 0, "truncated": 0}


def make_malformed(canned):
    """정상 JSON 문자열을 받아 불량 응답 3유형 중 하나로 바꾼다."""
    kind = random.choice(["codefence", "chatty", "truncated"])
    malformed_counts[kind] += 1
    if kind == "codefence":
        # 코드펜스 포함: ```json ... ```으로 감싸서 돌려줌
        return f"```json\n{canned}\n```", "end_turn"
    if kind == "chatty":
        # 사족 포함: JSON 앞에 인사말이 붙음
        return f"물론입니다! 분석 결과는 다음과 같습니다. {canned}", "end_turn"
    # 잘린 JSON: max_tokens에 걸려 중간에서 끊긴 상황
    return canned[: len(canned) // 2], "max_tokens"


def mock_llm_call(system, user_message, temperature=0.2, max_tokens=500):
    """실제 API와 동일한 인터페이스를 갖는 모의 함수.
    13주차에 이 함수의 내부만 실제 Anthropic 호출로 교체한다."""
    reviews_keywords = {
        "배송": '{"category": "배송", "sentiment": "긍정", "score": 4}',
        "환불": '{"category": "환불", "sentiment": "부정", "score": 2}',
        "품질": '{"category": "품질", "sentiment": "긍정", "score": 5}',
        "가격": '{"category": "가격", "sentiment": "중립", "score": 3}',
        "고객센터": '{"category": "서비스", "sentiment": "부정", "score": 2}',
    }
    canned = '{"category": "기타", "sentiment": "중립", "score": 3}'
    for keyword, answer in reviews_keywords.items():
        if keyword in user_message:
            canned = answer
            break

    text, stop_reason = canned, "end_turn"
    if random.random() < MALFORMED_RATE:
        text, stop_reason = make_malformed(canned)

    return {"text": text, "stop_reason": stop_reason,
            "usage": {"input_tokens": 120, "output_tokens": 35}}
