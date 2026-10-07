# 14차시 퀴즈 — 정규표현식

> 코드를 실행하지 말고 눈으로 풀어 보세요. 답은 `submissions/<내 ID>/s14/quiz.py` 에 적습니다.
> 출력 예측은 여러 줄이면 `"""` 로 감싸서 줄을 나눠 적고, 단답은 문자열로 적습니다(역슬래시가 들어가면 `r"..."` 로).

## Q1 (객관식 · 2점)

정규식 `[xyz]` 로 `search` 했을 때, 매치되는 부분이 **없는** 문자열은?

1. `box`
2. `sky`
3. `lazy`
4. `dog`

## Q2 (객관식 · 2점)

정규식 `go{2,3}d` 를 `re.match` 로 조사했을 때 매치되는 문자열을 **모두 고르세요**.

1. `god`
2. `good`
3. `goood`
4. `gooood`

## Q3 (객관식 · 2점)

정규식 `ca+t` 와 **완전히 같은 의미**인 것은?

1. `ca*t`
2. `ca{1,}t`
3. `ca?t`
4. `ca{0,}t`

## Q4 (객관식 · 2점)

다음 두 패턴에 대한 설명으로 **옳은** 것은?

```python
import re
p1 = re.compile("a.c")
p2 = re.compile("a[.]c")
```

1. `p1.match("abc")` 는 매치되고, `p2.match("abc")` 는 매치되지 않는다.
2. `p1.match("a.c")` 는 매치되지 않는다.
3. `p2.match("a0c")` 는 매치된다.
4. `p1.match("ac")` 는 매치된다.

## Q5 (객관식 · 2점)

컴파일된 패턴 객체의 메서드에 대한 설명으로 옳지 **않은** 것은?

1. `match()` 는 문자열의 처음부터 정규식과 매치되는지 조사한다.
2. `search()` 는 문자열 전체를 검색하여 정규식과 매치되는 부분이 있는지 조사한다.
3. `findall()` 은 정규식과 매치되는 모든 문자열을 리스트로 리턴한다.
4. `match()` 와 `search()` 는 매치되지 않으면 빈 문자열 `''` 을 리턴한다.

## Q6 (객관식 · 2점)

컴파일 옵션에 대한 설명으로 옳지 **않은** 것은?

1. `re.IGNORECASE` 와 `re.I` 는 같은 옵션으로, 대소문자 구별 없이 매치되게 한다.
2. `re.DOTALL` 은 `.` 메타 문자가 줄바꿈 문자 `\n` 과도 매치되게 한다.
3. `re.MULTILINE` 은 `.` 메타 문자가 여러 줄에 걸쳐 매치되게 하는 옵션이다.
4. `re.VERBOSE` 를 쓰면 정규식 안에 줄바꿈과 주석을 넣어 읽기 쉽게 작성할 수 있다.

## Q7 (객관식 · 2점)

어떤 텍스트 안에 들어 있는 글자 그대로의 `\data` (역슬래시 + data) 를 찾으려고 합니다. 정규식 엔진에 역슬래시 2개짜리 `\\data` 가 전달되도록 **올바르게** 컴파일한 것은?

1. `re.compile('\\data')`
2. `re.compile(r'\data')`
3. `re.compile(r'\\data')`
4. `re.compile('data')`

## Q8 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요. (여러 줄이면 `"""` 로 감싸서 줄을 나눠 적습니다)

```python
import re
text = "ab12cd345e6"
print(re.findall(r"\d", text))
print(re.findall(r"\d+", text))
print(re.findall(r"[a-z]+", text))
print(re.findall(r"\w+", text))
```

## Q9 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
import re
p = re.compile("[a-z]+")
m = p.match("42 apples")
print(m)
s = p.search("42 apples")
print(s.group())
print(s.start(), s.end())
print(s.span())
```

## Q10 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
import re
p = re.compile("[a-z]+", re.I)
m = p.match("Hello World")
print(m)
print(m.group())
```

## Q11 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
import re
data = """cat one
dog two
cat three"""
p1 = re.compile(r"^cat \w+")
p2 = re.compile(r"^cat \w+", re.M)
p3 = re.compile(r"\w+$", re.M)
print(p1.findall(data))
print(p2.findall(data))
print(p3.findall(data))
```

## Q12 (단답 · 3점)

정규식에서 `{0,1}` 과 같은 뜻을 가지는 메타 문자 **한 글자**를 적으세요.

## Q13 (단답 · 3점)

`\D` 와 같은 뜻을 대괄호 `[ ]` 문자 클래스로 적으세요. (숫자 범위는 `0-9` 로 표현)

## Q14 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
import re
text = "color colour colr"
print(re.findall(r"colou?r", text))
print(re.findall(r"colo*r", text))
print(re.findall(r"colo+r", text))
```

## Q15 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요. (`be` 와 `or` 사이의 공백은 2개입니다)

```python
import re
text = "to be  or"
print(len(re.findall(r"\s", text)))
p = re.compile(r"\S+")
for m in p.finditer(text):
    print(m.start(), m.end(), m.group())
```

## Q16 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
import re
p = re.compile(r"\d{2}")
print(p.match("2024").group())
print(p.findall("2024"))
print(p.findall("12345"))
print(p.match("7"))
print(p.search("a1b22").span())
```

## Q17 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
import re
text = "a1\nb2"
print(re.findall(".", text))
print(len(re.findall(".", text, re.S)))
print(re.match("a1.b2", text))
print(re.match("a1.b2", text, re.S).group())
```

## Q18 (객관식 · 2점)

`text = "A-1 b_2 C3"` 일 때, 실행 결과가 `['b_2', 'C3']` 인 것은?

1. `re.findall(r"\w+", text)`
2. `re.findall(r"\w{2,}", text)`
3. `re.findall(r"[a-z]\w+", text)`
4. `re.findall(r"\w\d", text)`

## Q19 (객관식 · 2점)

정규식 `[^a-z]+$` 를 `re.match` 로 조사했을 때 매치되는 문자열을 **모두 고르세요**.

1. `ABC`
2. `A1b`
3. `12 3`
4. `x9`
