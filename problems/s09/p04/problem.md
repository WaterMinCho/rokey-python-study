# p04. 책 정보 초기화 (빈칸 채우기 · 4점)

책의 제목과 가격을 저장하는 `Book` 클래스입니다. 빈칸(`____`) 3곳을 채워 클래스를 완성하세요.

- 객체를 만들 때 제목과 가격을 받아 인스턴스 변수 `title`, `price` 에 저장합니다. (객체를 생성하면 자동으로 호출되는 초기화 메서드를 사용합니다)
- `info()` 메서드는 제목과 가격을 아래 형식으로 출력합니다.
- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

## 테스트 코드와 출력 예

```python
b = Book("파이썬 입문", 18000)
b.info()
```

```
제목: 파이썬 입문
가격: 18000
```

```python
b = Book("로봇 공학", 32000)
print(b.title)
print(b.price)
```

```
로봇 공학
32000
```

## 시작 코드

```python
class Book:
    def ____(self, title, price):
        self.title = title
        ____ = price

    def info(self):
        print("제목:", self.title)
        print("가격:", ____)
```
