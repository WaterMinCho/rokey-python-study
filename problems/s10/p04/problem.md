# p04. 노트북은 기기다 (빈칸 채우기 · 6점)

제품 이름과 가격을 저장하는 `Device` 클래스와, 이를 **상속받아** 램 용량(`ram`)을 추가한 `Laptop` 클래스입니다.
빈칸(`____`) 3곳을 채워 클래스를 완성하세요.

- `Laptop` 의 `__init__` 은 **부모의 `__init__`** 을 호출해 `name`, `price` 를 저장하게 하고, 이어서 `ram` 을 인스턴스 변수에 저장합니다.
- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

```python
class Device:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def info(self):
        print("제품:", self.name)
        print("가격:", self.price)


class Laptop(____):
    def __init__(self, name, price, ram):
        ____.__init__(name, price)
        self.ram = ____
```

## 테스트 코드와 출력 예

```python
l = Laptop("그램", 1500000, 16)
l.info()
print(l.ram)
```

```
제품: 그램
가격: 1500000
16
```

```python
l = Laptop("맥북", 2000000, 8)
print(l.name, l.price, l.ram)
```

```
맥북 2000000 8
```
