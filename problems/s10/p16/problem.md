# p16. 범위 센서와 경보 센서 (빈칸 채우기 · 8점)

측정값을 리스트에 모으는 `Sensor`, 정해진 범위의 값만 받는 `RangeSensor`, 범위를 벗어난 값이 몇 번 들어왔는지 세는 `AlarmSensor` 가 차례로 상속하는 프로그램입니다.
빈칸(`____`) 3곳을 채워 클래스를 완성하세요.

| 클래스 | `read(value)` 가 하는 일 |
|---|---|
| `Sensor` | `value` 를 리스트 `values` 맨 뒤에 추가 |
| `RangeSensor` | `low` 이상 `high` 이하인 값만 **부모의 `read`** 에 넘겨 저장하고, 범위 밖의 값은 버림 |
| `AlarmSensor` | 범위 밖의 값이 들어오면 `alarms` 를 1 올리고, 그 값을 **부모의 `read`** 에 넘겨 부모와 같은 규칙으로 처리 |

- `AlarmSensor` 의 `__init__` 은 자기 변수 `alarms` 만 직접 만들고, 나머지 변수는 부모의 `__init__` 이 저장하게 합니다.
- `AlarmSensor` 의 `report()` 는 물려받은 `report()` 가 출력하는 한 줄 뒤에 `경보` 와 `alarms` 값을 한 줄 더 출력합니다.
- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다. 채점할 때는 아래와 같은 테스트 코드가 객체를 만들어 메서드를 호출합니다.

```python
class Sensor:
    def __init__(self, name):
        self.name = name
        self.values = []

    def read(self, value):
        self.values.append(value)

    def report(self):
        print(self.name, self.values)


class RangeSensor(Sensor):
    def __init__(self, name, low, high):
        super().__init__(name)
        self.low = low
        self.high = high

    def read(self, value):
        if value >= self.low and value <= self.high:
            ____.read(value)


class AlarmSensor(____):
    def __init__(self, name, low, high):
        super().__init__(____)
        self.alarms = 0

    def read(self, value):
        if value < self.low or value > self.high:
            self.alarms = self.alarms + 1
        super().read(value)

    def report(self):
        super().report()
        print("경보", self.alarms)
```

## 테스트 코드와 출력 예

```python
s = AlarmSensor("온도", 0, 50)
s.read(20)
s.read(70)
s.read(35)
s.report()
```

```
온도 [20, 35]
경보 1
```

```python
r = RangeSensor("습도", 10, 90)
r.read(5)
r.read(10)
r.read(90)
r.read(91)
r.report()
```

```
습도 [10, 90]
```

## 제한 사항
- `low`, `high`, `value` 는 -1000 이상 1000 이하의 정수이고 `low` 는 `high` 보다 크지 않습니다.
