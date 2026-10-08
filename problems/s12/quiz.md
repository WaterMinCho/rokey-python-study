# 12차시 퀴즈: 파일 처리

> 코드를 실행하지 말고 눈으로 풀어 보세요. 답은 `submissions/<내 ID>/s12/quiz.py` 에 적습니다.
> 출력 예측 문항은 실제로 파일을 만들고 다시 읽는 코드입니다. 파일에 무엇이 남는지부터 따라가 보세요.

## Q1 (객관식 · 2점)

파일 열기 모드에 대한 설명으로 옳지 **않은** 것은?

1. `"r"` 은 읽기 모드이며, 모드를 생략하고 `open("a.txt")` 라고만 써도 이 모드로 열린다.
2. `"w"` 로 열 때 파일이 없으면 새 파일이 만들어진다.
3. `"w"` 로 열 때 파일이 이미 있으면 기존 내용 **뒤에** 새 내용이 이어 붙는다.
4. `"a"` 는 기존 내용을 유지한 채 파일의 맨 끝에 새 내용을 추가한다.

## Q2 (객관식 · 2점)

파일에 대한 설명으로 옳지 **않은** 것은?

1. 파일은 이름과 확장자로 식별하며, 보통 HDD·SSD 같은 보조기억장치에 저장된다.
2. `.txt`, `.csv`, `.html` 은 사람이 읽을 수 있는 문자로 저장된 텍스트 파일이다.
3. `.jpg`, `.mp3`, `.exe` 는 바이너리 파일이지만 메모장 같은 텍스트 에디터로 열면 내용을 바로 읽을 수 있다.
4. 파일 크기, 생성 날짜, 접근 권한처럼 파일에 대한 정보를 메타데이터라고 한다.

## Q3 (객관식 · 2점)

현재 작업 디렉터리가 `C:/rokey/work/ch12` 이고, 읽으려는 파일의 절대 경로가 `C:/rokey/work/data/score.txt` 입니다. 이 파일을 가리키는 **상대 경로**로 옳은 것은?

1. `./data/score.txt`
2. `../data/score.txt`
3. `./ch12/data/score.txt`
4. `../../data/score.txt`

## Q4 (객관식 · 2점)

인코딩에 대한 설명으로 옳지 **않은** 것은?

1. 인코딩은 문자를 컴퓨터가 이해하는 바이너리 형식으로 바꾸는 것이고, 디코딩은 바이너리를 사람이 읽을 수 있는 문자로 되돌리는 것이다.
2. ASCII 는 미국에서 표준화한 7비트 부호 체계이고, 유니코드는 모든 문자를 다루도록 설계된 국제 표준이다.
3. 윈도우의 기본 한글 인코딩은 CP949(MS949) 이고 VSCode 의 기본 인코딩은 UTF-8 이라서, CP949 로 저장된 파일을 VSCode 에서 열면 한글이 깨져 보일 수 있다.
4. 파이썬은 운영체제와 상관없이 항상 UTF-8 로 파일을 읽고 쓰므로 `open()` 에 인코딩을 따로 지정할 필요가 없다.

## Q5 (객관식 · 2점)

현재 폴더에 `data.txt` 파일이 **없을 때**, 실행하면 오류가 발생하는 것은?

1. `f = open("data.txt", "w")`
2. `f = open("data.txt", "a")`
3. `f = open("data.txt")`
4. `f = open("data.txt", "w", encoding="utf-8")`

## Q6 (객관식 · 2점)

다음 코드를 실행했을 때의 결과로 옳은 것은?

```python
f = open("memo.txt", "w")
f.write("hello")
f.close()
f.write("bye")
```

1. `memo.txt` 에 `hellobye` 가 저장된다.
2. `memo.txt` 에 `hello` 가 저장되고, `bye` 는 조용히 무시된다.
3. `memo.txt` 에 `hello` 가 저장된 뒤, 마지막 줄에서 오류가 발생한다.
4. `f.close()` 가 파일을 삭제하므로 `memo.txt` 는 남지 않는다.

## Q7 (객관식 · 2점)

다음 코드를 실행했을 때의 결과로 옳은 것은?

```python
f = open("count.txt", "w")
f.write(100)
f.close()
```

1. `count.txt` 에 `100` 이 저장된다.
2. 숫자가 자동으로 문자열 `"100"` 으로 바뀌어 저장된다.
3. `write()` 는 문자열만 받을 수 있어서 오류가 발생한다.
4. 아무것도 쓰지 않고 오류 없이 끝난다.

## Q8 (객관식 · 2점)

다음 코드를 실행했을 때 출력되는 것은?

```python
with open("num.txt", "w") as f:
    f.write("1\n2\n3")

with open("num.txt", "r") as f:
    lines = f.readlines()
print(lines)
```

1. `['1', '2', '3']`
2. `['1\n', '2\n', '3\n']`
3. `['1\n', '2\n', '3']`
4. `1\n2\n3`

## Q9 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
f = open("memo.txt", "w")
f.write("one")
f.write("two")
f.close()

f = open("memo.txt", "r")
print(f.read())
f.close()
```

## Q10 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요. (여러 줄이면 `"""` 로 감싸서 줄을 나눠 적습니다)

```python
with open("note.txt", "w") as f:
    f.write("abc")
    print(f.closed)
print(f.closed)
```

## Q11 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요. 빈 줄이 있다면 빈 줄도 그대로 적습니다.

```python
with open("color.txt", "w") as f:
    f.write("red\nblue\n")

with open("color.txt", "r") as f:
    print(f.readline())
    print(f.readline(), end="")
```

## Q12 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
f = open("log.txt", "w")
f.write("start\n")
f.close()

f = open("log.txt", "w")
for i in range(1, 3):
    f.write("%d호\n" % i)
f.close()

f = open("log.txt", "a")
f.write("end")
f.close()

f = open("log.txt", "r")
print(f.read())
f.close()
```

## Q13 (단답 · 3점)

현재 작업 디렉터리(폴더)의 경로를 돌려주는 `os` 모듈의 함수 이름을 적으세요.

## Q14 (단답 · 3점)

다음 코드를 실행했을 때 출력되는 값을 적으세요.

```python
with open("t.txt", "w") as f:
    n = f.write("rokey")
print(n)
```

## Q15 (객관식 · 2점)

`with open("memo.txt", "w") as f:` 구문에 대한 설명으로 옳은 것은?

1. 블록이 끝나면 파일이 자동으로 닫히므로 `f.close()` 를 따로 쓰지 않아도 된다.
2. 블록 안에서 `print(f.closed)` 를 실행하면 `True` 가 출력된다.
3. `with` 로 연 파일에는 `write()` 를 쓸 수 없고 읽기만 할 수 있다.
4. `with` 로 열면 `"w"` 모드여도 `memo.txt` 의 기존 내용이 지워지지 않는다.

## Q16 (객관식 · 2점)

현재 작업 디렉터리가 `D:/study/week4` 일 때, `open("./log/run.txt", "r")` 이 여는 파일의 절대 경로는?

1. `D:/log/run.txt`
2. `D:/study/log/run.txt`
3. `D:/study/week4/log/run.txt`
4. `D:/study/week4/run.txt`

## Q17 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
with open("word.txt", "w") as f:
    f.write("go\nstop\nwait")

with open("word.txt", "r") as f:
    first = f.readline()
    second = f.readline()
    rest = f.readlines()
    last = f.readline()

print(len(first), len(second), len(rest), len(last))
```

## Q18 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요. 실행 전에는 `n.txt` 와 `j.txt` 가 없습니다. (여러 줄이면 `"""` 로 감싸서 줄을 나눠 적습니다)

```python
class Note:
    def __init__(self, path):
        self.path = path
        self.save("start")

    def save(self, text):
        f = open(self.path, "w")
        f.write(text + "\n")
        f.close()


class Journal(Note):
    def save(self, text):
        f = open(self.path, "a")
        f.write(text + "\n")
        f.close()


n = Note("n.txt")
j = Journal("j.txt")
for word in ["one", "two"]:
    n.save(word)
    j.save(word)

with open("n.txt", "r") as f:
    print(f.read(), end="")
with open("j.txt", "r") as f:
    print(f.read(), end="")
```
