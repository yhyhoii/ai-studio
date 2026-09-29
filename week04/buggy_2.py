# -*- coding: utf-8 -*-
"""
buggy_2.py  ―  카테고리별 매출 집계 (pandas 버전)

dirty_sales.csv를 pandas로 읽어 카테고리별 매출 합계를 구하려 한다.
그런데 실행하자마자 죽는다.

[과제] Traceback을 얻어 예외 타입을 확인하고,
       '원인을 데이터에서 직접 확인'한 뒤(힌트: 실제 컬럼명이 무엇인가?)
       코드를 수정하라.
"""
import pandas as pd

def load(path):
    df = pd.read_csv(path, encoding="utf-8")
    return df

def summarize(df):
    # 단가 x 수량으로 매출액 컬럼을 만든 뒤 카테고리별 합계를 낸다
    # FIXED: price가 문자열(str)이라 곱하면 숫자 곱셈이 아닌 문자열 반복이 일어나므로 숫자로 변환
    price = (df["price"].astype(str)
                         .str.replace(",", "")
                         .str.replace("원", "")
                         .str.strip())
    df["price"] = pd.to_numeric(price, errors="coerce")

    # FIXED: 실제 컬럼명은 "단가"/"수량"이 아니라 "price"/"quantity" (df.columns.tolist()로 확인)
    df["매출액"] = df["price"] * df["quantity"]
    return df.groupby("category")["매출액"].sum()

if __name__ == "__main__":
    df = load("dirty_sales.csv")
    result = summarize(df)
    print(result)
