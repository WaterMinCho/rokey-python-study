# p11. 정사각형은 직사각형이다 (출력 · 6점)

아래 `Rect` 클래스가 이미 작성되어 있습니다(시작 코드에 포함).

```python
class Rect:
    kind = "직사각형"

    def __init__(self, width, height):
        self.width = width
        self.height = height
        print("도형 생성")

    def area(self):
        return self.width * self.height

    def info(self):
        print(self.kind, self.area())
```

`Rect` 를 **상속받는** `Square` 클래스를 정의하세요. 정사각형은 가로와 세로가 같은 직사각형입니다.

- 생성자는 `Square(side)` 처럼 한 변의 길이 **하나만** 받습니다. 안에서 **부모의 `__init__`** 을 호출해 `width` 와 `height` 에 모두 `side` 가 저장되게 합니다. (부모 `__init__` 이 출력하는 `도형 생성` 도 그대로 나와야 합니다)
- 클래스 변수 `kind` 를 `정사각형` 으로 다시 선언합니다.
- `area()` 와 `info()` 는 새로 만들지 않습니다. 부모의 것을 그대로 씁니다.
- `Rect` 클래스는 고치지 않습니다. 채점할 때는 아래와 같은 테스트 코드가 객체를 만들어 메서드를 호출합니다.

## 테스트 코드와 출력 예

```python
s = Square(4)
s.info()
```

```
도형 생성
정사각형 16
```

```python
r = Rect(2, 5)
r.info()
s = Square(5)
s.info()
print(Rect.kind, Square.kind)
```

```
도형 생성
직사각형 10
도형 생성
정사각형 25
직사각형 정사각형
```

## 제한 사항
- `side`, `width`, `height` 는 1 이상 100 이하의 정수
