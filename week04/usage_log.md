# 4주차 과제 — 진단 보고 및 AI 활용 기록

## 1. 진단 보고

### buggy_1.py
- **무엇이**: `ValueError: invalid literal for int() with base 10: ''` (최초에는 `'5,200'`)
- **어디서**: `buggy_1.py` 19행, `calc_total()`의 `price = int(row["price"]...)`
- **왜**: `print(repr(row["price"]))`로 확인한 결과 콤마(`'5,200'`), 단위(`'4200원'`), 부호(`'-4500'`)가 섞여 있었고, 이를 replace로 정제한 뒤에도 401행(아메리카노)·470행(마들렌)은 price가 빈 문자열(`''`)이라 `int()` 변환에 실패함
- **수정**: 콤마·원 제거 후, 빈 문자열이면 `continue`로 해당 행을 계산에서 제외
- **범위 판단**: 9999999 같은 이상치는 `int()` 변환 자체는 성공해 Traceback을 유발하지 않으므로 이번 과제 범위 밖으로 판단, 처리하지 않음

### buggy_2.py
- **무엇이**: `KeyError: '단가'`
- **어디서**: `buggy_2.py` 20행, `summarize()`의 `df["매출액"] = df["단가"] * df["수량"]`
- **왜**: `print(df.columns.tolist())` 결과 실제 컬럼은 `['date', 'product', 'category', 'price', 'quantity', 'stock']`로 영문이며 `단가`/`수량`은 존재하지 않음
- **추가 발견**: 컬럼명만 고치면 에러는 사라지지만 price의 dtype이 `str`이라 `quantity`와 곱할 때 문자열 반복(`"15000"*7`)이 일어나 결과가 `"1500015000..."` 형태로 조용히 틀림 → `pd.to_numeric()`으로 숫자 변환 추가

### buggy_3.py
- **무엇이**: `AttributeError: 'NoneType' object has no attribute 'groupby'`
- **어디서**: `buggy_3.py` 28행, `main()`의 `df.groupby("category")["revenue"].sum()`
- **왜**: `df`가 `None`이므로 직전 단계인 27행 `df = load_and_clean(...)`을 역추적. `load_and_clean()`에 `return df`가 없어 함수가 암묵적으로 `None`을 반환함
- **수정**: `load_and_clean()` 끝에 `return df` 추가

### buggy_4.py (에러 없음)
- **무엇이 틀렸나**: 실행은 되지만 총 매출액이 약 1,500억 원으로 커피숍 매출로는 비현실적임
- **어떻게 알아챘나**: `df.info()`에서 price가 498 non-null(결측 2건), `df["price"].describe()`에서 min `-4500`, max `9999999` 확인. `df.describe()`에서 quantity max도 `9999999`임을 확인
- **왜**: 결측은 `sum()`이 조용히 건너뛰고, 음수·극단값은 정상값처럼 그대로 더해짐
- **처리**: 결측 2건(0.4%)은 비율이 낮아 `dropna` 선택. IQR 규칙(lower=-8500, upper=24300)과 음수 조건으로 price 이상치 2건 제외(마들렌 -4500은 다른 마들렌 행이 모두 2800원이라 단순 부호 오타로 보기 어려움). quantity 9999999(텀블러) 1건은 placeholder로 추정해 제외
- **결과**: 총 매출액 438,939,400원 / 평균 단가 8,291원

### buggy_5.py
- **무엇이**: `IndexError: list index out of range`
- **어디서**: `buggy_5.py` 29행, `find_big_jumps()`의 `diff = prices[i + 1] - prices[i]`
- **왜**: 조건부 중단점(`i >= len(prices) - 2`)으로 확인한 결과 `len(prices)=500`, 마지막 반복에서 `i=499`일 때 `prices[500]`을 참조함. `range(len(prices))`의 off-by-one 오류
- **수정**: `range(len(prices) - 1)`로 변경

---

## 2. 검증 증빙

| 파일 | 수정 후 실행 결과 | 회귀 확인 |
|---|---|---|
| buggy_1 | `총 매출액: 151,198,388,824원` | 2,413,400원 일치, 104행 |
| buggy_2 | 굿즈 1.500995e+11 / 베이커리 6.525450e+07 / 원두 1.808970e+08 / 음료 8.410400e+08 | 베이커리 합계를 따로 계산한 값(66,325,500원)과 일치 |
| buggy_3 | 굿즈 1.500995e+11 / 베이커리 6.525450e+07 / 원두 1.808970e+08 / 음료 8.410400e+08 | 굿즈·원두·음료 합계가 buggy_2와 동일함 확인 (네 카테고리 모두 buggy_2와 동일) |
| buggy_4 | `총 매출액: 438,939,400원` / `평균 단가: 8,291원` | 전체 500행 → 495행, 제외된 5건이 결측 2 + price 이상치 2 + quantity 이상치 1과 정확히 일치 |
| buggy_5 | `급변 지점 2건` — (249, 21000→9999999), (250, 9999999→3500) | 탐지된 2건이 모두 알려진 이상치(9999999) 구간이며, 정상 구간에서는 급변 지점이 잡히지 않음 |

※ buggy_1~3의 굿즈 합계가 큰 것은 quantity 9999999(텀블러) 이상치 때문이며, 각 스크립트의 과제 범위(해당 Traceback 해결)를 벗어나 처리하지 않음. 

---

## 3. AI 활용 기록 (buggy_2 · buggy_3 · buggy_4: 미사용)

### 사례 1 — buggy_1.py (ValueError)

- 사용 도구: GitHub Copilot Chat

**프롬프트 전문**
> ① **맥락**: dirty_sales.csv를 csv 모듈로 한 줄씩 읽어 매출액(단가 x 수량)을 누적하는 스크립트입니다.
>
> ② **코드**:
> ```python
> def calc_total(path):
>     total = 0
>     with open(path, "r", encoding="utf-8") as f:
>         reader = csv.DictReader(f)
>         for i, row in enumerate(reader):
>             price = int(row["price"])
>             qty = int(row["quantity"])
>             total += price * qty
>     return total
> ```
> ③ **Traceback**:
> ```
> Traceback (most recent call last):
>   File "c:\ai-studio\ai-studio-week04\buggy_1.py", line 25, in <module>
>     total = calc_total("dirty_sales.csv")
>   File "c:\ai-studio\ai-studio-week04\buggy_1.py", line 19, in calc_total
>     price = int(row["price"])
> ValueError: invalid literal for int() with base 10: '5,200'
> ```
> ④ **내가 확인한 것**: 마지막 값이 '5,200'이었습니다. 콤마 때문에 int 변환이 안 되는 것 같습니다.
>
> ⑤ **요청**: 제 가설이 맞는지 원인을 먼저 설명해 주세요. 그리고 콤마 외에도 int 변환을 막는 값이 데이터에 더 있는지 확인하는 방법을 알려 주세요. 수정 코드는 원인을 확인한 뒤 제가 직접 작성하겠습니다.

**AI 답변 요지**
- 가설이 맞음. `csv.DictReader`는 값을 문자열로 반환하고, `int()`는 천 단위 콤마를 처리하지 못해 `'5,200'`에서 ValueError가 발생함 (CSV의 따옴표는 파싱 중에 벗겨짐)
- price·quantity 전체를 검사한 결과 변환 실패는 **price 12건, quantity 0건**
  - 콤마 8건(319, 343, 368, 391, 414, 435, 457, 480행), "원" 2건(330, 404행), 빈 값 2건(401, 470행)
- 실패한 값을 찾는 진단 코드(`try: int(raw) except ValueError: print(...)`)를 제안
- `-4500`은 `int()`로 변환은 되지만 가격으로는 이상한 값이며, 하이픈을 무조건 제거하면 음수의 의미가 바뀐다고 경고
- 코드는 수정하지 않음

**채택/기각**
- 원인 설명: 채택. 에러 직전에 `print(repr(row["price"]))`로 찍힌 마지막 값이 `'5,200'`이었고, Copilot의 설명(`csv.DictReader`는 문자열을 반환하고 `int()`는 콤마를 처리하지 못함)과 일치함
- 진단 코드: 채택. 제안받은 `try/except` 코드를 그대로 실행해 보니 변환 실패가 price 12건, quantity 0건으로 Copilot 답변과 같았음
- 하이픈 제거 경고: 기각. `-4500`은 `int()`로 변환되므로 ValueError의 원인이 아니고, buggy_1의 과제 범위는 ValueError 해결임. 음수 가격이 정상인지는 buggy_4에서 IQR과 도메인 판단으로 따로 처리함. 다만 경고 내용 자체는 타당하다고 보고, 하이픈 제거가 값의 의미를 바꿀 수 있다는 점을 진단 보고에 적어 둠
- 기타: Copilot이 현재 파일이 이미 수정된 상태라 Traceback 당시 코드와 다르다고 지적함. 질문에 붙인 코드가 수정 전 원본이라 생긴 차이로, 답변 내용에는 영향 없음

**검증 결과**
- 콤마·"원"·하이픈 제거 후 다시 실행했더니 401행에서 `ValueError: invalid literal for int() with base 10: ''` 발생 → Copilot이 찾아준 빈 값 2건(401, 470행) 중 첫 번째와 일치
- `if not price_raw: continue` 추가 후 재실행: 총 매출액 151,199,459,824원 (에러 없이 끝까지 실행)
- 회귀 확인: 정상 데이터 3행만 담은 CSV(텀블러 15000×7, 크루아상 3800×58, 에코백 12000×174)로 `calc_total()`을 실행한 결과 2,413,400원. 계산기로 계산한 값(105,000 + 220,400 + 2,088,000 = 2,413,400)과 일치하여, 전처리를 추가한 뒤에도 정상 행이 그대로 합산됨을 확인

### 사례 2 — buggy_5.py (IndexError + 조건부 중단점)

- 사용 도구: GitHub Copilot Chat

**프롬프트 전문**
> ① **맥락**: 정제한 price 리스트를 앞뒤로 비교해 변화폭이 10만 원 이상인 급변 지점을 찾는 스크립트입니다.
>
> ② **코드**:
> ```python
> def find_big_jumps(prices, threshold=100000):
>     jumps = []
>     for i in range(len(prices)):
>         diff = prices[i + 1] - prices[i]
>         if abs(diff) >= threshold:
>             jumps.append((i, prices[i], prices[i + 1], diff))
>     return jumps
> ```
> ③ **Traceback**:
> ```
> Traceback (most recent call last):
>   File "c:\ai-studio\ai-studio-week04\buggy_5.py", line 36, in <module>
>     jumps = find_big_jumps(prices)
>   File "c:\ai-studio\ai-studio-week04\buggy_5.py", line 29, in find_big_jumps
>     diff = prices[i + 1] - prices[i]
> IndexError: list index out of range
> ```
> ④ **내가 확인한 것**:  "i=499, len(prices)=500일 때 멈췄습니다. prices[i+1]이 prices[500]이 되는 게 원인 같습니다.
>
> ⑤ **요청**: 제 관찰로 원인을 설명할 수 있는지 확인해 주세요. 반복 범위를 어떻게 바꾸면 되는지와, 수정 후 마지막 원소 쌍(prices[498], prices[499])이 빠짐없이 비교되는지 확인하는 방법을 알려 주세요.

**AI 답변 요지**
- 관찰한 원인이 맞음. 길이 500인 리스트의 유효 인덱스는 0~499인데 `range(len(prices))`는 i=499까지 돌고, 이때 `prices[i + 1]`이 `prices[500]`이 되어 IndexError 발생
- 인접 쌍 비교에서 유효한 i는 0 ~ len(prices)-2이므로 `range(len(prices) - 1)`로 바꿔야 함. 마지막 반복은 i=498로 prices[498]과 prices[499]를 비교함
- 마지막 쌍 확인 방법으로, 마지막 쌍에서만 임계값 이상의 변화가 생기는 테스트 데이터를 제안함
  `prices = [0] * 499 + [100000]` → `find_big_jumps(prices) == [(498, 0, 100000, 100000)]`
- 현재 파일에는 이미 수정이 적용되어 있어 Traceback은 수정 전 코드에서 나온 것이라고 지적함. 코드는 수정하지 않음

**채택/기각**
- 원인 설명: 채택. 조건부 중단점(`i >= len(prices) - 2`)에서 관찰한 값과 일치함
- 수정 방법 `range(len(prices) - 1)`: 채택
- 마지막 쌍 확인 테스트: 채택. 앞 499개가 모두 0이라 변화가 전혀 없고 마지막 쌍에서만 급변이 생기므로, 결과에 i=498이 잡히면 마지막 쌍까지 비교했다는 확실한 증거가 됨

**검증 결과**
- 수정 후 재실행: 에러 없이 `급변 지점 2건` 출력
  - `(249, 21000.0, 9999999.0, 9978999.0)`
  - `(250, 9999999.0, 3500.0, -9996499.0)`
  - 두 지점 모두 카페라떼 price 9999999 이상치 구간과 일치
- 마지막 쌍 확인: Copilot이 제안한 테스트를 실행한 결과 `[(498, 0, 100000, 100000)]`이 나와 assert 통과
- 회귀 확인: 직접 만든 리스트 `[1000, 2000, 300000, 3000]`으로 실행하니 `(1, 2000, 300000, 298000)`, `(2, 300000, 3000, -297000)` 2건이 나옴. 변화폭이 작은 첫 쌍(1000→2000)은 잡히지 않고 큰 변화만 정상적으로 탐지됨

### AI에게 '본인이 수정한 코드'의 설명 요구 — buggy_1.py

- 사용 도구: GitHub Copilot Chat

**요청 전문**
> 제가 buggy_1.py를 아래처럼 수정했습니다.
> ```python
> price_raw = (row["price"].replace(",", "")
>               .replace("-", "")
>               .replace("원", "")
>               .strip())
> if not price_raw:
>     continue
> price = int(price_raw)
> ```
> 이 코드를 한 줄씩 설명해 주세요. 특히 다음 두 가지가 궁금합니다.
> 1. `if not price_raw: continue`는 결측치를 데이터에서 삭제하는 건가요, 합계 계산에서만 빼는 건가요?
> 2. `.strip()`이나 `.replace(" ", "")`로는 빈 값을 처리할 수 없는 이유가 무엇인가요?

**AI 설명 요지**
- 정제 부분: 콤마·하이픈·"원"을 제거하고 `.strip()`으로 앞뒤 공백을 정리해 `price_raw`에 저장함. 단, 하이픈 제거는 `"-4500"`을 `"4500"`으로 바꿔 음수의 의미를 없애므로 음수가 오류인지 환불인지 먼저 확인해야 한다고 지적함
- 질문 1: `continue`는 현재 행을 합계 계산에서만 제외할 뿐, CSV 파일이나 이미 읽은 `row`를 삭제·수정하지 않음
- 질문 2: `.strip()`과 `.replace(" ", "")`는 문자열을 정리할 뿐 빈 값인지 판단하거나 변환을 건너뛰지 않음. `""`에 적용해도 여전히 `""`이므로, `int("")`를 막으려면 `if not price_raw` 검사가 필요함
- `int(price_raw)`: 앞의 조건문 덕분에 빈 값이 들어오지 않으며, `"0"`은 빈 문자열이 아니므로 정상적으로 0으로 변환됨

**본인 검증 의견**
설명이 정확했다. 설명의 주장을 하나씩 실행해서 확인했다.
- `calc_total()` 실행 전후로 dirty_sales.csv의 해시가 같아, 원본 파일이 바뀌지 않음을 확인
- 건너뛴 행을 출력해 보니 401행(아메리카노)과 470행(마들렌) 2건뿐이라, 빈 가격 행만 합계에서 빠진다는 설명과 일치
- `"".strip()`과 `"".replace(" ", "")`가 둘 다 `''`를 반환하고, `int("")`가 ValueError를 내는 것을 직접 확인
- `int("0")`이 0을 반환해, `if not price_raw`가 문자열 `"0"`을 잘못 건너뛰지 않는다는 점도 확인 (숫자 0이었다면 `not 0`이 True라 건너뛰었겠지만, 이 시점의 `price_raw`는 문자열이라 문제없음)

하이픈 제거에 대한 지적은 사례 1에서 받은 경고와 같은 내용이다. 처음에는 buggy_1의 범위가 ValueError 해결이라 코드를 그대로 두었지만, 하이픈 제거는 ValueError 해결에 필요 없고 -4500을 +4500으로 바꿔 합산하는 부작용이 있어 .replace("-", "")를 삭제했다(buggy_2도 같은 이유로 삭제). 수정 후 총 매출액은 151,199,459,824원에서 151,198,388,824원으로 1,071,000원 줄었다. 이 차이는 -4500 행 하나(4,500 × 2 × 수량 119)와 정확히 일치해, 다른 행에는 영향이 없음을 확인했다. 음수 가격이 정상인지는 buggy_4에서 이상치로 따로 판단했다.
