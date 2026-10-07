# p04. 카운터 클래스 (빈칸 채우기 · 6점)

숫자를 세는 `Counter` 클래스입니다. 객체를 만들 때 받은 시작값을 인스턴스 변수 `value` 에 저장하고, `up()` 메서드는 `value` 를 `step` 만큼 늘린 뒤 **늘어난 뒤의 `value` 를 반환**합니다. `step` 을 생략하면 1 씩 늘어납니다. 빈칸(`____`) 2곳을 채워 클래스를 완성하세요.

```python
class Counter:
    def __init__(self, start):
        ____ = start

    def up(self, step=1):
        self.value += step
        return ____
```

- 클래스만 완성하면 됩니다. 채점할 때는 아래와 같은 테스트 코드가 객체를 만들어 메서드를 호출합니다.
- 객체마다 `value` 는 따로 관리됩니다.
- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

## 테스트 코드와 출력 예

```python
c = Counter(10)
c.up()
c.up(5)
print(c.value)
```

```
16
```

```python
c = Counter(0)
print(c.up(3))
print(c.up())
```

```
3
4
```
