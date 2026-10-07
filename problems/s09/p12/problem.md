# p12. 점수판 관리 함수 (출력 · 8점)

선수를 나타내는 `Player` 클래스와, `Player` 객체 **여러 개가 담긴 리스트**를 다루는 함수 두 개를 작성하세요.

## Player 클래스

| 구분 | 이름 | 내용 |
|---|---|---|
| 생성자 | `Player(name)` | 이름을 인스턴스 변수 `name` 에 저장하고, 점수 `score` 는 `0` 으로 시작 |
| 메서드 | `add(n)` | 점수를 `n` 만큼 더한다. `n` 은 **음수일 수도** 있다. 반환값 없음 |

## 함수

| 함수 | 하는 일 |
|---|---|
| `top(players)` | 리스트에서 점수가 가장 높은 **`Player` 객체**를 반환. 같은 점수가 여러 명이면 리스트에서 **앞에 있는** 선수를 반환 |
| `reset(players)` | 리스트에 있는 모든 선수의 점수를 `0` 으로 되돌린다. 반환값 없음 |

- `top` 은 이름(문자열)이 아니라 **객체**를 반환합니다. 채점 코드는 반환된 객체의 `.name`, `.score` 를 읽습니다.
- `reset` 은 새 객체를 만드는 것이 아니라, 리스트에 들어 있는 **기존 객체**의 `score` 를 바꿔야 합니다.
- 클래스와 함수를 정의하기만 하면 됩니다. 채점할 때는 아래와 같은 테스트 코드가 객체를 만들어 호출합니다.

## 테스트 코드와 출력 예

```python
a = Player("A")
b = Player("B")
print(a.score, b.score)
a.add(3)
b.add(5)
print(top([a, b]).name)
```

```
0 0
B
```

```python
a = Player("A")
b = Player("B")
c = Player("C")
a.add(5)
b.add(5)
c.add(2)
print(top([a, b, c]).name)
print(top([c, b, a]).name)
```

```
A
B
```

```python
a = Player("A")
b = Player("B")
a.add(4)
b.add(9)
reset([a, b])
print(a.score, b.score)
a.add(2)
print(a.score, b.score)
print(top([a, b]).name)
```

```
0 0
2 0
A
```

## 제한 사항
- `players` 의 길이는 1 이상 10 이하 (빈 리스트는 주어지지 않습니다)
- `n` 은 -100 이상 100 이하의 정수. 모든 선수의 점수가 음수인 경우도 있습니다.
