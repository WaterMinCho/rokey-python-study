# p13. 수강생 합격 판정 (출력 · 8점)

수강생의 점수를 모아 합격 여부를 알려 주는 `Student` 클래스를 정의하세요.

| 구분 | 이름 | 내용 |
|---|---|---|
| 클래스 변수 | `cut` | 합격 기준 점수. 처음 값은 `60` |
| 생성자 | `Student(name)` | 이름을 인스턴스 변수 `name` 에 저장하고, 점수를 담을 빈 리스트를 인스턴스 변수 `scores` 에 저장 |
| 메서드 | `add(score)` | `scores` 의 맨 뒤에 `score` 를 추가. 반환값 없음 |
| 메서드 | `average()` | 점수의 평균에서 소수점 아래를 버린 **정수**를 **반환**. 점수가 하나도 없으면 `0` 을 반환 |
| 메서드 | `passed()` | `average()` 의 반환값이 `cut` **이상**이면 `True`, 아니면 `False` 를 **반환** |

- `cut` 은 모든 수강생이 함께 쓰는 값이라 클래스 변수(클래스 안, 메서드 밖)로 선언합니다. `scores` 는 수강생마다 따로 있어야 하므로 생성자 안에서 만듭니다.
- `passed()` 안에 숫자 `60` 을 직접 적지 않고 클래스 변수 `cut` 을 읽어서 비교합니다. 테스트 코드가 `Student.cut = 80` 으로 기준을 바꾸면, 그 뒤에 호출한 `passed()` 는 이미 만들어 둔 수강생도 80 을 기준으로 판정해야 합니다.
- 클래스만 정의하면 됩니다. 채점할 때는 아래와 같은 테스트 코드가 객체를 만들어 메서드를 호출합니다.

## 테스트 코드와 출력 예

```python
s = Student("Mina")
s.add(70)
s.add(55)
print(s.average())
print(s.passed())
```

```
62
True
```

70 과 55 의 평균은 62.5 이고, 소수점 아래를 버리면 62 입니다.

```python
a = Student("A")
b = Student("B")
c = Student("C")
a.add(60)
b.add(59)
print(a.passed(), b.passed())
print(a.scores, b.scores)
print(c.average(), c.passed())
```

```
True False
[60] [59]
0 False
```

```python
a = Student("A")
a.add(75)
print(Student.cut, a.passed())
Student.cut = 80
b = Student("B")
b.add(90)
print(a.passed(), b.passed())
```

```
60 True
False True
```

- 출력은 글자 하나까지 같아야 합니다. `average()` 가 `62.5` 나 `62.0` 을 반환하면 오답입니다.

## 제한 사항
- `score` 와 `cut` 은 0 이상 100 이하의 정수
