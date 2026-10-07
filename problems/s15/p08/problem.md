# p08. 카운트다운 이터레이터 클래스 (출력 · 6점)

`Countdown(start)` 객체를 for 문에 넣으면 `start`, `start - 1`, …, `1` 을 차례로 돌려주는 이터레이터 클래스를 완성하세요.
`__init__` 은 이미 작성되어 있으니 `__iter__` 와 `__next__` 메서드를 추가하면 됩니다.

- `start` 가 0 이면 아무 값도 돌려주지 않습니다.
- 값을 다 돌려준 뒤 `next()` 가 호출되면 `StopIteration` 예외를 일으켜야 합니다.
- 객체마다 따로 세어야 합니다(두 객체를 번갈아 써도 서로 영향이 없어야 합니다).

## 테스트 코드와 출력 예

```python
for x in Countdown(3):
    print(x)
```

```
3
2
1
```

```python
c = Countdown(2)
print(next(c))
print(next(c))
try:
    next(c)
except StopIteration:
    print("done")
```

```
2
1
done
```

```python
print(list(Countdown(4)))
print(list(Countdown(0)))
```

```
[4, 3, 2, 1]
[]
```
