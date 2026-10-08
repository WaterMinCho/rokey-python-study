# 모의고사 2회 (1~16차시) 퀴즈

> 코드를 실행하지 말고 눈으로 풀어 보세요. 답은 `submissions/<내 ID>/m2/quiz.py` 에 적습니다.
> 출력 예측 문항은 여러 줄이면 `"""` 로 감싸서 줄을 나눠 적고, 띄어쓰기와 따옴표까지 정확히 적습니다.
> PyQt6 코드가 나오는 문항은 `import sys` 와 필요한 `from PyQt6.QtWidgets import ...` 가 이미 되어 있다고 가정합니다.

## Q1 (객관식 · 2점)

다음 (가)~(다)에 해당하는 용어를 순서대로 적은 것은?

- (가) 소스 코드를 실행하는 도중에 해석해 가며 실행하는 프로그램
- (나) 명령어를 입력해 컴퓨터를 직접 제어하는 소프트웨어
- (다) 프로그램을 검사하고, 에러가 났을 때 고치는 일을 돕는 도구

1. 디버거 · 터미널 · 인터프리터
2. 인터프리터 · 터미널 · 디버거
3. 인터프리터 · 디버거 · 터미널
4. IDE · 터미널 · 디버거

## Q2 (객관식 · 2점)

다음 코드를 실행하고 `8` 을 입력했을 때, 첫째 줄부터 차례로 출력되는 것은?

```python
n = input()
print(n + n)
print(int(n) + int(n))
print(int(n) / 2)
```

1. `16`, `16`, `4`
2. `88`, `16`, `4`
3. `16`, `16`, `4.0`
4. `88`, `16`, `4.0`

## Q3 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요. (여러 줄이면 `"""` 로 감싸서 줄을 나눠 적습니다)

```python
score = 75
bonus = 0
if score >= 90:
    grade = "A"
elif score >= 70:
    grade = "B"
    bonus = 5
elif score >= 60:
    grade = "C"
    bonus = 10
else:
    grade = "F"
score = score + bonus
if score >= 80:
    print("우수")
if score % 2 == 0 and not grade == "A":
    print("짝수", grade)
else:
    print("홀수", grade)
print(score, bonus)
```

## Q4 (객관식 · 2점)

다음 코드를 실행했을 때 출력되는 것은?

```python
a = [1, 2, 3]
b = list(map(lambda x: x + 3, a))
a.append(b)
a.extend(b)
t = (a[1], a[-1])
d = {"x": len(a), "y": a[3]}
d["x"] = d["x"] + 1
print(len(a), t, d)
```

1. `9 (2, 6) {'x': 10, 'y': 4}`
2. `5 (2, [4, 5, 6]) {'x': 6, 'y': [4, 5, 6]}`
3. `7 (2, 6) {'x': 8, 'y': [4, 5, 6]}`
4. `7 (5, 6) {'x': 8, 'y': [4, 5, 6]}`

## Q5 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요.

```python
total = 0
n = 0
while n < 20:
    n += 3
    if n % 2 == 0:
        continue
    if total > 10:
        break
    total += n
    print(n, total)
print(n, total)
```

## Q6 (객관식 · 2점)

다음 코드를 실행했을 때 화면에 출력되는 줄 수와 마지막 줄을 옳게 적은 것은?

```python
def find(nums, target):
    for i in range(len(nums)):
        if nums[i] == target:
            return i
        print("확인", i)

a = find([4, 8, 6], 8)
b = find([4, 8], 5)
print(a, b)
```

1. 3줄, 마지막 줄은 `1 None`
2. 4줄, 마지막 줄은 `1 None`
3. 4줄, 마지막 줄은 `1 2`
4. 5줄, 마지막 줄은 `1 None`

## Q7 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요. (여러 줄이면 `"""` 로 감싸서 줄을 나눠 적습니다)

```python
def join_all(words, sep=", "):
    if len(words) == 1:
        return words[0]
    rest = join_all(words[1:])
    print(len(words), rest)
    return words[0] + sep + rest

print(join_all(["a", "b", "c"], "/"))
print(join_all(["x", "y"]))
```

## Q8 (객관식 · 2점)

다음 코드를 실행했을 때 출력되는 것은?

```python
class Cart:
    items = []

    def __init__(self, owner):
        self.owner = owner
        self.count = 0

    def add(self, name):
        self.items.append(name)
        self.count += 1


a = Cart("A")
b = Cart("B")
a.add("펜")
b.add("자")
b.add("풀")
print(len(a.items), a.count, b.count)
```

1. `3 1 2`
2. `1 1 2`
3. `3 3 3`
4. `items` 는 `self.items = []` 로 만든 적이 없으므로 `a.add("펜")` 에서 오류가 발생한다

## Q9 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요. (여러 줄이면 `"""` 로 감싸서 줄을 나눠 적습니다)

```python
class Alarm:
    def __init__(self, label):
        self.label = label

    def sound(self):
        return "삐"

    def ring(self):
        print(self.label, self.sound())


class LoudAlarm(Alarm):
    def __init__(self, label, times):
        super().__init__(label)
        self.times = times

    def sound(self):
        return super().sound() * self.times + "!"


class SilentAlarm(Alarm):
    def sound(self):
        return "(무음)"

    def ring(self):
        super().ring()
        print(self.label, "확인")


for a in [Alarm("회의"), LoudAlarm("기상", 2), SilentAlarm("약")]:
    a.ring()
print(LoudAlarm("점심", 3).sound())
```

## Q10 (객관식 · 2점)

다음 코드를 실행했을 때의 결과로 옳은 것은?

```python
class Device:
    def __init__(self, name):
        self.name = name
        self.power = False

    def turn_on(self):
        self.power = True
        print(self.name, "켜짐")


class Speaker(Device):
    def __init__(self, name, volume):
        self.volume = volume

    def louder(self):
        self.volume += 1
        print("볼륨", self.volume)


s = Speaker("거실", 5)    # (가)
s.louder()                # (나)
s.turn_on()               # (다)
print(s.power)            # (라)
```

1. (가)에서 인수 개수가 맞지 않아 오류가 발생한다.
2. `볼륨 6`, `거실 켜짐`, `True` 가 차례로 출력된다.
3. `볼륨 6` 과 `거실 켜짐` 이 출력된 뒤 (라)에서 오류가 발생한다.
4. `볼륨 6` 이 출력된 뒤 (다)에서 오류가 발생한다.

## Q11 (객관식 · 2점)

다음 프로그램을 실행한 뒤, 사용자가 `큰 컵` 을 체크하고 `ICE` 를 선택한 다음 `샷 추가` 를 체크하고 `주문` 버튼을 한 번 클릭했습니다. 콘솔에 출력되는 것은?

```python
def order():
    if r_hot.isChecked():
        text = "따뜻한"
    elif r_ice.isChecked():
        text = "차가운"
    if chk_shot.isChecked():
        text = text + " 샷추가"
    if chk_big.isChecked():
        text = text + " 큰컵"
    print(text)

app = QApplication(sys.argv)
window = QWidget()

r_hot = QRadioButton("HOT")
r_ice = QRadioButton("ICE")
r_hot.setChecked(True)
chk_shot = QCheckBox("샷 추가")
chk_big = QCheckBox("큰 컵")
btn = QPushButton("주문")
btn.clicked.connect(order)

layout = QVBoxLayout()
layout.addWidget(r_hot)
layout.addWidget(r_ice)
layout.addWidget(chk_shot)
layout.addWidget(chk_big)
layout.addWidget(btn)
window.setLayout(layout)
window.show()
sys.exit(app.exec())
```

1. `차가운 큰컵 샷추가`
2. `따뜻한 샷추가 큰컵`
3. `차가운 샷추가 큰컵`
4. `따뜻한`

## Q12 (객관식 · 2점)

다음 tkinter 프로그램을 실행해 창이 뜬 뒤 `호출` 버튼을 두 번 클릭했습니다. 그때까지 콘솔에 출력된 것을 모두 적은 것은?

```python
import tkinter as tk

count = 0

def call():
    global count
    count += 1
    print("호출", count)

root = tk.Tk()
root.title("대기 번호")
btn = tk.Button(root, text="호출", command=call())
btn.pack()
root.mainloop()
```

1. `호출 1`, `호출 2`
2. `호출 1`
3. `호출 1`, `호출 2`, `호출 3`
4. 아무것도 출력되지 않는다

## Q13 (출력 예측 · 3점)

버튼의 `clicked` 시그널과 `setEnabled()` 를 GUI 없이 흉내 낸 코드입니다. 출력 결과를 그대로 적으세요. (여러 줄이면 `"""` 로 감싸서 줄을 나눠 적습니다)

```python
class Signal:
    def __init__(self):
        self.slots = []

    def connect(self, func):
        self.slots.append(func)

    def emit(self):
        for func in self.slots:
            func()


class Button:
    def __init__(self, text):
        self.text = text
        self.enabled = True
        self.clicked = Signal()

    def setEnabled(self, value):
        self.enabled = value

    def click(self):
        if self.enabled:
            self.clicked.emit()


count = 0

def add():
    global count
    count += 1
    if count >= 3:
        btn.setEnabled(False)

def show():
    print(btn.text, count)

btn = Button("담기")
btn.clicked.connect(add)
btn.clicked.connect(show)
btn.click()
btn.clicked.connect(add)
btn.click()
btn.click()
print(count, btn.enabled)
```

## Q14 (객관식 · 2점)

다음 코드를 실행했을 때 출력되는 것은? (`log.txt` 는 처음에 없습니다)

```python
f = open("log.txt", "w")
f.write("a\nb\n")
f.close()
f = open("log.txt", "a")
f.write("c\n")
f.close()
f = open("log.txt", "w")
f.write("d\n")
f.close()
f = open("log.txt", "a")
f.write("e")
f.close()
f = open("log.txt")
first = f.readline()
rest = f.readlines()
f.close()
print(len(first), rest)
```

1. `2 ['e']`
2. `1 ['e']`
3. `2 ['b\n', 'c\n', 'd\n', 'e']`
4. `2 ['d\n', 'e']`

## Q15 (출력 예측 · 3점)

다음 코드의 출력 결과를 그대로 적으세요. (여러 줄이면 `"""` 로 감싸서 줄을 나눠 적습니다)

```python
def check(x):
    if x < 0:
        raise ValueError("음수")
    return 10 // x

def run(items):
    done = 0
    for item in items:
        try:
            value = check(int(item))
            done += 1
        except ValueError as e:
            print("값 오류:", e)
            continue
        except ZeroDivisionError:
            print("0 오류")
        finally:
            print("확인", item)
        print(item, "->", value)
    return done

print(run(["4", "-1", "0"]))
```

## Q16 (객관식 · 2점)

다음 코드를 실행했을 때 출력되는 것은?

```python
import re

p = re.compile(r"[a-z]+\d*")
text = "Room7 a12 b c3"
m = p.match(text)
s = p.search(text)
print(m, s.group(), len(p.findall(text)))
```

1. `None a12 3`
2. `None oom7 3`
3. `None oom7 4`
4. `m` 이 `None` 이어서 `print` 에서 오류가 발생한다

## Q17 (단답 · 3점)

다음 코드를 실행했을 때 출력되는 값을 적으세요.

```python
import re

p = re.compile(r"\d{2,3}")
m = p.search("tel 5 0421-88")
print(m.end())
```

## Q18 (단답 · 3점)

다음 코드를 실행했을 때 출력되는 값을 적으세요.

```python
from collections import deque

dq = deque()
for x in [1, 2, 3, 4]:
    if x % 2 == 0:
        dq.appendleft(x)
    else:
        dq.append(x)
dq.append(dq.popleft())
print(dq.pop() + dq.popleft())
```
