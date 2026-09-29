# -*- coding: utf-8 -*-
"""
buggy_3.py  ―  데이터 로드 후 카테고리별 집계

load_and_clean()으로 데이터를 읽어 정제한 뒤,
그 결과를 groupby로 집계하려 한다.
그런데 집계 단계에서 이상한 에러가 난다.

[과제] Traceback의 예외 타입을 확인하고,
       'NoneType ...' 메시지가 가리키는 '이 변수를 만든 직전 단계'를
       역추적하여 원인 함수를 찾아 수정하라.
"""
import pandas as pd

def load_and_clean(path):
    df = pd.read_csv(path, encoding="utf-8")
    # price 컬럼을 숫자로 정제
    df["price"] = (df["price"].astype(str)
                              .str.replace(",", "")
                              .str.replace("원", "")
                              .str.strip())
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["revenue"] = df["price"] * df["quantity"]
    return df  # FIXED: return이 없어 함수가 None을 반환했고, main()에서 None.groupby()로 AttributeError 발생

def main():
    df = load_and_clean("dirty_sales.csv")
    result = df.groupby("category")["revenue"].sum()
    print(result)

if __name__ == "__main__":
    main()