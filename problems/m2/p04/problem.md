# p04. 온라인 강좌 클래스 (빈칸 채우기 · 6점)

과목 이름과 수업 시간을 저장하는 `Course` 클래스와, 이를 상속받아 수강 사이트까지 저장하는 `OnlineCourse` 클래스입니다. 빈칸(`____`) 3곳을 채워 프로그램을 완성하세요.

```python
class Course:
    def __init__(self, title, hours):
        self.title = title
        self.hours = hours

    def summary(self):
        return self.title + " " + str(self.hours) + "시간"


class OnlineCourse(____):
    def __init__(self, title, hours, site):
        ____(title, hours)
        self.site = site

    def summary(self):
        return ____ + " (" + self.site + ")"
```

- `OnlineCourse` 의 `__init__` 은 `title` 과 `hours` 를 직접 저장하지 않고 부모의 `__init__` 이 저장하게 합니다.
- `OnlineCourse` 의 `summary()` 는 부모의 `summary()` 가 돌려준 문자열 뒤에 공백 한 칸과 괄호로 감싼 사이트를 붙여 반환합니다. 세 번째 빈칸에는 부모의 `summary()` 를 호출하는 식을 적습니다.
- 클래스만 완성하면 됩니다. 채점할 때는 아래와 같은 테스트 코드가 객체를 만들어 메서드를 호출합니다.
- 제출하면 `Course` 의 `__init__` 이나 `summary()` 를 다른 함수로 바꿔 놓은 테스트도 함께 돌립니다. `OnlineCourse` 가 부모의 메서드를 호출하지 않고 부모의 코드를 옮겨 적은 답은 이 테스트에서 오답 처리됩니다.
- **빈칸만** 채웁니다. 다른 줄을 고치거나 줄을 추가하면 오답 처리됩니다.

## 테스트 코드와 출력 예

```python
c = OnlineCourse("파이썬", 40, "rokey.kr")
print(c.summary())
```

```
파이썬 40시간 (rokey.kr)
```

```python
c = OnlineCourse("ROS", 32, "edu.net")
print(c.title, c.hours, c.site)
print(Course("수학", 20).summary())
```

```
ROS 32 edu.net
수학 20시간
```
