# run_pipeline.py — reviews_sample.csv 전체를 분류하고 처리/실패 건수를 보고한다
import csv
from pathlib import Path

import mock_llm
from classify import classify_review

CSV_PATH = Path(__file__).parent / "reviews_sample.csv"


def load_reviews(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return [row["review_text"] for row in csv.DictReader(f)]


def main():
    reviews = load_reviews(CSV_PATH)

    stats = {}
    failed = 0
    for review in reviews:
        result = classify_review(review)
        if result is None:  # 실패 건은 건너뛰되 반드시 센다
            failed += 1
            continue
        cat = result["category"]
        stats[cat] = stats.get(cat, 0) + 1

    counts = mock_llm.malformed_counts
    malformed_total = sum(counts.values())
    recovered = counts["codefence"]  # 코드펜스형은 방어 1이 걷어내서 정상 처리된다

    print("\n" + "=" * 50)
    print(f"처리 {len(reviews)}건 / 실패 {failed}건")
    print("=" * 50)
    print(f"카테고리별 집계 (성공 {len(reviews) - failed}건): {stats}")
    print(f"\n불량 응답 {malformed_total}건 "
          f"(코드펜스 {counts['codefence']} / 사족 {counts['chatty']} / 잘린 JSON {counts['truncated']})")
    print(f"  - 복구: {recovered}건 (코드펜스형 → 방어 1이 ``` 제거 후 정상 파싱)")
    print(f"  - 실패: {counts['chatty'] + counts['truncated']}건 (사족형·잘린 JSON형 → 방어 2에서 None 반환)")
    print(f"\n→ 실패 {failed}건이 불량 응답 {malformed_total}건보다 적은 이유: "
          f"코드펜스형 {recovered}건이 복구되었기 때문")


if __name__ == "__main__":
    main()
