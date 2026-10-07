# p07. 자전거 정보 출력 (빈칸 채우기 · 6점)

탈것(`Vehicle`)을 상속받은 자전거(`Bicycle`) 클래스를 정의하고, **이 파일을 직접 실행했을 때만** 객체를 만들어 정보를 출력하는 프로그램입니다.
빈칸(`____`) 3곳을 채워 프로그램을 완성하세요.

- `Bicycle` 의 `__init__` 은 부모의 `__init__` 으로 `name`, `speed` 를 저장하고 `gears` 를 추가로 저장합니다.
- `Bicycle` 의 `info()` 는 **부모의 `info()`** 를 먼저 호출한 뒤 기어 수를 한 줄 더 출력합니다.
- 마지막 `if` 문은 이 파일이 **메인 모듈로 직접 실행될 때만** 참이 되도록 합니다. 다른 파일에서 import 되면 안쪽 코드가 실행되지 않습니다.
- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

```python
class Vehicle:
    def __init__(self, name, speed):
        self.name = name
        self.speed = speed

    def info(self):
        print(self.name, self.speed)


class Bicycle(Vehicle):
    def __init__(self, name, speed, gears):
        super().__init__(____, speed)
        self.gears = gears

    def info(self):
        ____.info()
        print("기어:", self.gears)


if __name__ == "____":
    b = Bicycle("자전거", 25, 7)
    b.info()
```

## 출력 예 (직접 실행했을 때)

```
자전거 25
기어: 7
```
