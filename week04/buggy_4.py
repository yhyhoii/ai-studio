# -*- coding: utf-8 -*-
"""
buggy_4.py  ―  총 매출액 집계 (에러 없이 '조용히' 틀리는 스크립트)

이 스크립트는 에러 없이 잘 돌아가고, 그럴듯한 숫자를 출력한다.
하지만 그 숫자는 '틀렸다'.

[과제] 이 스크립트는 예외를 던지지 않는다. 대신
       (1) info()/describe()로 데이터 상태를 먼저 세어 보고
       (2) '무엇이 틀렸는지 어떻게 알아챘는지'를 서술한 뒤
       (3) 결측 규모를 보고하고 처리 방법을 선택·적용하여
           올바른 총매출을 산출하라.
       (힌트: 가격 결측은 몇 건인가? 음수 가격과 9999999 같은 값은 정상인가?)
"""
import pandas as pd

def main():
    df = pd.read_csv("dirty_sales.csv", encoding="utf-8")

    df["price"] = (df["price"].astype(str)
                              .str.replace(",", "")
                              .str.replace("원", "")
                              .str.strip())
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    # FIXED: coerce로 생긴 NaN 규모를 반드시 재확인 (price 결측 2건)
    print(f"price 결측: {df['price'].isna().sum()}건")

    # FIXED: IQR 규칙으로 price 이상치 후보 식별 (lower=-8500, upper=24300)
    q1, q3 = df["price"].quantile(0.25), df["price"].quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr

    # FIXED: 결측 2건은 비율(0.4%)이 낮아 삭제 선택
    df = df.dropna(subset=["price"])
    # FIXED: 음수(마들렌 -4500, 정상가 2800과 불일치)와 9999999(카페라떼)는 입력 오류로 판단해 제외
    df = df[~((df["price"] < lower) | (df["price"] > upper) | (df["price"] < 0))]
    # FIXED: quantity 9999999(텀블러)는 placeholder로 추정, 총매출을 왜곡하므로 제외
    df = df[df["quantity"] != 9999999]

    df["revenue"] = df["price"] * df["quantity"]
    total = df["revenue"].sum()
    avg_price = df["price"].mean()

    print(f"총 매출액: {total:,.0f}원")
    print(f"평균 단가: {avg_price:,.0f}원")

if __name__ == "__main__":
    main()