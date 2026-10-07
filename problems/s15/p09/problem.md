# p09. 파일을 한 줄씩 읽는 제너레이터 (출력 · 8점)

텍스트 파일의 경로 `path` 를 받아, 파일의 각 줄을 한 줄씩 돌려주는 **제너레이터 함수** `read_lines(path)` 를 작성하세요.

- 돌려주는 각 줄에서는 줄 끝의 줄바꿈 문자(`\n`)를 뺍니다. `strip()` 을 쓰면 됩니다.
- 파일은 `with open(path, "r") as f:` 로 열고, 읽은 줄을 `yield` 로 하나씩 내보냅니다.
- 함수를 호출한 결과는 리스트가 아니라 **제너레이터 객체**여야 합니다(`type(g).__name__` 이 `generator`).
- 빈 파일이면 아무 값도 돌려주지 않습니다.
- 테스트마다 아래 예와 같은 파일이 현재 폴더에 미리 만들어져 있습니다.

## 테스트 코드와 출력 예

`memo.txt` 의 내용이 다음과 같을 때

```
apple
banana
cherry
```

```python
g = read_lines("memo.txt")
print(type(g).__name__)
print(next(g))
print(next(g))
```

```
generator
apple
banana
```

```python
for line in read_lines("memo.txt"):
    print(line + "!")
```

```
apple!
banana!
cherry!
```

`todo.txt` 의 내용이 `buy milk` 와 `walk dog` 두 줄일 때

```python
print(list(read_lines("todo.txt")))
```

```
['buy milk', 'walk dog']
```
