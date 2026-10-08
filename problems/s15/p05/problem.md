# p05. 제너레이터 두 가지 방법 (빈칸 채우기 · 6점)

제너레이터를 함수로 한 번, 표현식으로 한 번 만드는 프로그램입니다. 빈칸(`____`) 2곳을 채워 완성하세요.

```python
def countdown(start):
    n = start
    while n > 0:
        ____ n
        n = n - 1


gen = countdown(3)
print(next(gen))
print(next(gen))
print(next(gen))

squares = ____
print(type(squares))
print(next(squares))
for s in squares:
    print(s)
```

- `countdown(start)` 는 `start` 부터 1 까지 값을 하나씩 돌려주는 제너레이터 함수입니다. 첫 번째 빈칸에는 값을 하나 돌려주고 멈추는 키워드가 들어갑니다.
- `squares` 는 1 부터 4 까지의 제곱(1, 4, 9, 16)을 차례로 만드는 **제너레이터 표현식**입니다. 두 번째 빈칸에 표현식 전체를 한 줄로 적습니다.
- `print(type(squares))` 가 `<class 'generator'>` 를 출력해야 합니다. 리스트나 `iter(리스트)` 로 만들면 이 줄의 출력이 달라집니다.
- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

## 출력 예

```
3
2
1
<class 'generator'>
1
4
9
16
```
